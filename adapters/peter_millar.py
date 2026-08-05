"""
Adapter for Peter Millar's sale section.

NOTE: This is a TEMPLATE. I cannot browse petermillar.com from this environment to
verify live CSS selectors (my sandbox only has network access to a small dev-tool
allowlist, not general retail sites). Before this runs for real, you'll need to:

  1. Open https://www.petermillar.com/sale/ in your browser
  2. Right-click a product tile -> Inspect -> find the actual class names for
     product container, title, price, sale price, size options, color, and link
  3. Swap the placeholder selectors below (marked with # ADJUST ME)

This same pattern applies to every adapter in this folder — they're all templates
following the same structure. Retail sites change their HTML periodically, so
expect to revisit selectors every few months if a source stops returning results.
"""
from bs4 import BeautifulSoup
from adapters.base import safe_get

SALE_URL = "https://www.petermillar.com/sale/mens/"
SOURCE_NAME = "Peter Millar"
BRAND_NAME = "Peter Millar"


def fetch_deals() -> list:
    resp = safe_get(SALE_URL)
    if resp is None:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    deals = []

    # ADJUST ME: real selector for each product tile
    for tile in soup.select(".product-tile"):
        try:
            title_el = tile.select_one(".product-title")          # ADJUST ME
            price_el = tile.select_one(".price-sale")              # ADJUST ME
            orig_price_el = tile.select_one(".price-original")     # ADJUST ME
            link_el = tile.select_one("a")                         # ADJUST ME
            color_el = tile.select_one(".color-name")              # ADJUST ME
            size_els = tile.select(".size-swatch:not(.unavailable)")  # ADJUST ME

            if not (title_el and price_el and orig_price_el and link_el):
                continue

            title = title_el.get_text(strip=True)
            price = float(price_el.get_text(strip=True).replace("$", "").replace(",", ""))
            original_price = float(orig_price_el.get_text(strip=True).replace("$", "").replace(",", ""))
            url = link_el.get("href")
            if url and url.startswith("/"):
                url = "https://www.petermillar.com" + url
            color = color_el.get_text(strip=True) if color_el else ""
            sizes = [s.get_text(strip=True) for s in size_els] if size_els else []

            deals.append({
                "deal_id": url,
                "source": SOURCE_NAME,
                "brand": BRAND_NAME,
                "title": title,
                "price": price,
                "original_price": original_price,
                "url": url,
                "available_sizes": sizes,
                "color": color,
                "category_text": title,  # fallback: category often embedded in title
            })
        except (AttributeError, ValueError) as e:
            print(f"[peter_millar] skipped a tile due to parse error: {e}")
            continue

    return deals
