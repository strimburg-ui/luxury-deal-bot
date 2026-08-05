"""
Adapter for Brooks Brothers's sale section.

TEMPLATE — selectors are placeholders (marked # ADJUST ME). Inspect the live
page's HTML in your browser and swap in the real class/tag names before this
adapter will return real results. See adapters/peter_millar.py for a fully
annotated example of this same pattern.

This source only carries Brooks Brothers, so brand is fixed.
"""
from bs4 import BeautifulSoup
from adapters.base import safe_get

SALE_URL = "https://www.brooksbrothers.com/sale/men"
SOURCE_NAME = "Brooks Brothers"
BRAND_NAME = "Brooks Brothers"


def fetch_deals() -> list:
    resp = safe_get(SALE_URL)
    if resp is None:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    deals = []

    for tile in soup.select(".product-tile"):  # ADJUST ME
        try:
            title_el = tile.select_one(".product-title")          # ADJUST ME
            price_el = tile.select_one(".price-sale")              # ADJUST ME
            orig_price_el = tile.select_one(".price-original")     # ADJUST ME
            link_el = tile.select_one("a")                         # ADJUST ME
            color_el = tile.select_one(".color-name")              # ADJUST ME
            brand_el = tile.select_one(".product-brand")           # ADJUST ME
            size_els = tile.select(".size-swatch:not(.unavailable)")  # ADJUST ME

            if not (title_el and price_el and orig_price_el and link_el):
                continue

            title = title_el.get_text(strip=True)
            price = float(price_el.get_text(strip=True).replace("$", "").replace(",", ""))
            original_price = float(orig_price_el.get_text(strip=True).replace("$", "").replace(",", ""))
            url = link_el.get("href")
            if url and url.startswith("/"):
                url = SALE_URL.split("/")[0] + "//" + SALE_URL.split("/")[2] + url
            color = color_el.get_text(strip=True) if color_el else ""
            sizes = [s.get_text(strip=True) for s in size_els] if size_els else []
            brand = "Brooks Brothers"

            deals.append({
                "deal_id": url,
                "source": SOURCE_NAME,
                "brand": brand,
                "title": title,
                "price": price,
                "original_price": original_price,
                "url": url,
                "available_sizes": sizes,
                "color": color,
                "category_text": title,
            })
        except (AttributeError, ValueError) as e:
            print(f"[brooks_brothers] skipped a tile due to parse error: {e}")
            continue

    return deals
