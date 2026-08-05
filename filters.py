"""
Shared filter logic every adapter's raw results get passed through.
A "deal" dict is expected to have:
    brand, title, price, original_price, url, source,
    available_sizes (list[str]), color (str), category_text (str)
"""
from config import (
    TOP_SIZES_ACCEPTABLE, PANT_SIZE_STRINGS, TARGET_COLORS,
    TARGET_CATEGORIES, MIN_DISCOUNT_PERCENT, BRAND_TIER_LOOKUP,
)


def discount_percent(price: float, original_price: float) -> float:
    if not original_price or original_price <= 0:
        return 0.0
    return round((1 - price / original_price) * 100, 1)


def matches_size(deal: dict) -> bool:
    sizes = [s.upper().replace(" ", "") for s in deal.get("available_sizes", [])]
    top_hits = any(any(t.replace(" ", "") in s for t in TOP_SIZES_ACCEPTABLE) for s in sizes)
    pant_hits = any(any(p.replace(" ", "") in s for p in PANT_SIZE_STRINGS) for s in sizes)
    # Deal matches if it's an acceptable top size OR an acceptable pant size
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


def passes_all_filters(deal: dict) -> bool:
    return (
        matches_size(deal)
        and matches_color(deal)
        and matches_category(deal)
        and meets_discount(deal)
    )


def tier_for_brand(brand: str) -> str:
    return BRAND_TIER_LOOKUP.get(brand.lower(), "?")
