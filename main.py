"""
Entry point. Run this daily (via GitHub Actions, see .github/workflows/daily.yml).

Flow:
    1. Loop through every source in config.SOURCES
    2. Call that adapter's fetch_deals()
    3. Run every deal through filters.passes_all_filters()
    4. Collapse near-duplicate listings (same seller/brand relisting the same
       item across sizes, or matching more than one search category)
    5. For deals that pass, check tracker.should_alert() to dedup
    6. Send a Telegram digest of everything new
    7. Write ALL currently-matching deals to docs/deals.json for the gallery website
"""
import difflib
import importlib
import json
import re
import traceback
from datetime import datetime, timezone

from config import SOURCES
from filters import passes_all_filters, tier_for_brand
from tracker import init_db, should_alert, record_deal
from notifier import send_daily_digest

GALLERY_JSON_PATH = "docs/deals.json"

# Two listings are treated as the same product (and collapsed to one) if
# they're from the same brand, within this many dollars of each other, and
# their titles are at least this similar after stripping size/color noise.
DUPLICATE_PRICE_TOLERANCE = 3.0
DUPLICATE_TITLE_SIMILARITY = 0.82

_SIZE_NOISE_PATTERN = re.compile(
    r"\b(xs|s|m|l|xl|xxl|xxxl|small|medium|large|tall|regular|slim|"
    r"\d{1,2}(x\d{1,2})?|\d{1,2}(w|l))\b",
    re.IGNORECASE,
)


def _normalized_title(title: str) -> str:
    """Strips size-ish tokens so 'Navy Sweater M' and 'Navy Sweater L' compare as the same product."""
    cleaned = _SIZE_NOISE_PATTERN.sub("", title.lower())
    return re.sub(r"\s+", " ", cleaned).strip()


def dedupe_near_duplicates(deals: list) -> list:
    """
    Collapses listings that are almost certainly the same product — same
    brand, similar price, near-identical title once size/color noise is
    stripped. Keeps the first (cheapest, since callers pass deals already
    sorted or roughly grouped) occurrence of each group.
    """
    kept = []
    for deal in deals:
        brand = (deal.get("brand") or "").lower()
        price = deal.get("price") or 0
        norm_title = _normalized_title(deal.get("title", ""))

        is_duplicate = False
        for existing in kept:
            if (existing.get("brand") or "").lower() != brand:
                continue
            if abs((existing.get("price") or 0) - price) > DUPLICATE_PRICE_TOLERANCE:
                continue
            existing_norm = _normalized_title(existing.get("title", ""))
            similarity = difflib.SequenceMatcher(None, norm_title, existing_norm).ratio()
            if similarity >= DUPLICATE_TITLE_SIMILARITY:
                is_duplicate = True
                break

        if not is_duplicate:
            kept.append(deal)

    return kept


def write_gallery_json(all_matching_deals: list):
    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "count": len(all_matching_deals),
        "deals": [
            {
                "title": d.get("title", ""),
                "brand": d.get("brand", ""),
                "tier": tier_for_brand(d.get("brand", "")),
                "price": d.get("price"),
                "original_price": d.get("original_price"),
                "discount_percent": d.get("discount_percent"),
                "source": d.get("source", ""),
                "url": d.get("url", ""),
                "image_url": d.get("image_url", ""),
                "color": d.get("color", ""),
                "available_sizes": d.get("available_sizes", []),
            }
            for d in all_matching_deals
        ],
    }
    # Sort so the biggest discounts show first
    output["deals"].sort(key=lambda d: d.get("discount_percent") or 0, reverse=True)

    with open(GALLERY_JSON_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"[main] wrote {len(all_matching_deals)} deal(s) to {GALLERY_JSON_PATH}")


def run():
    init_db()
    new_deals = []
    all_matching_deals = []

    for source_module in SOURCES:
        try:
            adapter = importlib.import_module(f"adapters.{source_module}")
        except ImportError as e:
            print(f"[main] could not import adapter '{source_module}': {e}")
            continue

        try:
            raw_deals = adapter.fetch_deals()
        except Exception:
            print(f"[main] adapter '{source_module}' raised an error:")
            traceback.print_exc()
            continue

        print(f"[main] {source_module}: fetched {len(raw_deals)} raw listings")

        for deal in raw_deals:
            if not passes_all_filters(deal):
                continue
            all_matching_deals.append(deal)

    before_count = len(all_matching_deals)
    all_matching_deals = dedupe_near_duplicates(all_matching_deals)
    removed = before_count - len(all_matching_deals)
    if removed:
        print(f"[main] collapsed {removed} near-duplicate listing(s)")

    for deal in all_matching_deals:
        if should_alert(deal["deal_id"], deal["price"]):
            new_deals.append(deal)
        record_deal(deal)

    print(f"[main] {len(new_deals)} new deal(s) matched all filters and are new/price-dropped")
    send_daily_digest(new_deals)
    write_gallery_json(all_matching_deals)


if __name__ == "__main__":
    run()
