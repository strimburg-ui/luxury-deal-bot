"""
Shared filter logic every adapter's raw results get passed through.
A "deal" dict is expected to have:
    brand, title, price, original_price, url, source,
    available_sizes (list[str]), color (str), category_text (str)
"""
import re

from config import (
    TOP_SIZES_ACCEPTABLE, PANT_SIZE_STRINGS, TARGET_COLORS,
    TARGET_CATEGORIES, MIN_DISCOUNT_PERCENT, BRAND_TIER_LOOKUP,
    LOW_PRICE_BY_CATEGORY, LOW_PRICE_DEFAULT,
)

SHORTS_EXCLUDE_PATTERN = re.compile(r"short[\s-]?sleeve", re.IGNORECASE)


def discount_percent(price: float, original_price: float) -> float:
    if not original_price or original_price <= 0:
        return 0.0
    return round((1 - price / original_price) * 100, 1)


def matches_size(deal: dict) -> bool:
    sizes = [s.upper().replace(" ", "") for s in deal.get("available_sizes", [])]
    top_hits = any(any(t.replace(" ", "") in s for t in TOP_SIZES_ACCEPTABLE) for s in sizes)
    pant_hits = any(any(p.replace(" ", "") in s for p in PANT_SIZE_STRINGS) for s in sizes)
    return top_hits or pant_hits


def matches_color(deal: dict) -> bool:
    color = (deal.get("color") or "").lower()
    title = (deal.get("title") or "").lower()
    return any(c in color or c in title for c in TARGET_COLORS)


def matches_category(deal: dict) -> bool:
    text = f"{deal.get('title', '')} {deal.get('category_text', '')}".lower()
    return any(cat in text for cat in TARGET_CATEGORIES)


def meets_discount(deal: dict) -> bool:
    pct = discount_percent(deal["price"], deal.get("original_price", deal["price"]))
    deal["discount_percent"] = pct
    return pct >= MIN_DISCOUNT_PERCENT


def price_ceiling_for(deal: dict) -> float:
    """Finds the low-price ceiling for whichever category this item matches
    first (list is ordered pricier/more-specific categories first)."""
    text = f"{deal.get('title', '')} {deal.get('category_text', '')}".lower()

    for label, keywords, ceiling in LOW_PRICE_BY_CATEGORY:
        for kw in keywords:
            if kw not in text:
                continue
            if label == "Shorts" and SHORTS_EXCLUDE_PATTERN.search(text):
                continue
            return ceiling

    return LOW_PRICE_DEFAULT


def meets_price_or_discount(deal: dict) -> bool:
    """
    True if the item clears the normal discount threshold, OR if it's just
    flat-out cheap for its category regardless of discount %. This catches
    genuinely low-price items (e.g. a $20 eBay listing with no marked-down
    "original price") that would otherwise get filtered out for showing 0% off.
    """
    if meets_discount(deal):
        return True
    return deal["price"] <= price_ceiling_for(deal)


def passes_all_filters(deal: dict) -> bool:
    return (
        matches_size(deal)
        and matches_color(deal)
        and matches_category(deal)
        and meets_price_or_discount(deal)
    )


def tier_for_brand(brand: str) -> str:
    return BRAND_TIER_LOOKUP.get(brand.lower(), "?")
