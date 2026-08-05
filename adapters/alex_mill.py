"""
Adapter for Alex Mill's sale section.

Alex Mill runs on Shopify, which publishes a free public JSON feed of every
product in a collection — no scraping, no bot-blocking, no fragile CSS
selectors. This is the most reliable kind of adapter in this project.

Feed used: https://www.alexmill.com/collections/sale/products.json

This works the same way on any Shopify store: append /products.json to any
/collections/<handle> URL to get the raw product data as JSON.
"""
from adapters.base import safe_get

BASE_URL = "https://www.alexmill.com"
COLLECTION_HANDLE = "sale"
SOURCE_NAME = "Alex Mill"
BRAND_NAME = "Alex Mill"

SIZE_OPTION_HINTS = ("size",)
COLOR_OPTION_HINTS = ("color", "colour")


def _find_option_index(option_names: list, hints: tuple) -> int:
    for i, name in enumerate(option_names):
        if any(h in name.lower() for h in hints):
            return i
    return -1


def _parse_product(product: dict) -> list:
    variants = product.get("variants", [])
    if not variants:
        return []

    option_names = [o.get("name", "") for o in product.get("options", [])]
    size_idx = _find_option_index(option_names, SIZE_OPTION_HINTS)
    color_idx = _find_option_index(option_names, COLOR_OPTION_HINTS)

    def option_value(variant, idx):
        if idx < 0:
            return ""
        key = f"option{idx + 1}"
        return variant.get(key) or ""

    available_variants = [v for v in variants if v.get("available")]
    if not available_variants:
        return []

    sizes = sorted({option_value(v, size_idx) for v in available_variants if option_value(v, size_idx)})
    color = option_value(available_variants[0], color_idx)

    def to_float(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None

    prices = [to_float(v.get("price")) for v in available_variants]
    prices = [p for p in prices if p is not None]
    if not prices:
        return []
    price = min(prices)

    compare_prices = [to_float(v.get("compare_at_price")) for v in available_variants]
    compare_prices = [p for p in compare_prices if p is not None]
    original_price = max(compare_prices) if compare_prices else price

    handle = product.get("handle", "")
    url = f"{BASE_URL}/products/{handle}"
    title = product.get("title", "")
    product_type = product.get("product_type", "")
    tags = ", ".join(product.get("tags", []))

    images = product.get("images", [])
    image_url = images[0].get("src", "") if images else ""

    return [{
        "deal_id": url,
        "source": SOURCE_NAME,
        "brand": BRAND_NAME,
        "title": title,
        "price": price,
        "original_price": original_price,
        "url": url,
        "available_sizes": sizes,
        "color": color,
        "category_text": f"{product_type} {tags} {title}",
        "image_url": image_url,
    }]


def fetch_deals() -> list:
    deals = []
    page = 1
    max_pages = 10

    while page <= max_pages:
        url = f"{BASE_URL}/collections/{COLLECTION_HANDLE}/products.json?limit=250&page={page}"
        resp = safe_get(url)
        if resp is None:
            break

        try:
            data = resp.json()
        except ValueError:
            print(f"[alex_mill] page {page} did not return valid JSON")
            break

        products = data.get("products", [])
        if not products:
            break

        for product in products:
            deals.extend(_parse_product(product))

        page += 1

    print(f"[alex_mill] parsed {len(deals)} products across {page - 1} page(s)")
    return deals
