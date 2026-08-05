"""
Entry point. Run this daily (via GitHub Actions, see .github/workflows/daily.yml).

Flow:
    1. Loop through every source in config.SOURCES
    2. Call that adapter's fetch_deals()
    3. Run every deal through filters.passes_all_filters()
    4. For deals that pass, check tracker.should_alert() to dedup
    5. Send a Telegram digest of everything new
    6. Write ALL currently-matching deals to docs/deals.json for the gallery website
"""
import importlib
import json
import traceback
from datetime import datetime, timezone

from config import SOURCES
from filters import passes_all_filters, tier_for_brand
from tracker import init_db, should_alert, record_deal
from notifier import send_daily_digest

GALLERY_JSON_PATH = "docs/deals.json"


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
            if should_alert(deal["deal_id"], deal["price"]):
                new_deals.append(deal)
            record_deal(deal)

    print(f"[main] {len(new_deals)} new deal(s) matched all filters and are new/price-dropped")
    send_daily_digest(new_deals)
    write_gallery_json(all_matching_deals)


if __name__ == "__main__":
    run()
