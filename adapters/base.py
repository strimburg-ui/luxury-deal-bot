"""
Every adapter module must expose a single function:

    fetch_deals() -> list[dict]

Each dict in the returned list should have these keys:
    deal_id          str   — stable unique id (e.g. SKU or URL) so we can dedup
    source            str   — e.g. "Nordstrom Rack"
    brand             str   — must match a brand name in config.BRAND_TIERS (or close enough)
    title             str   — product title
    price             float — current price
    original_price    float — list/original price
    url               str   — link to the product
    available_sizes   list[str] — e.g. ["M TALL", "L", "32x34"]
    color             str   — e.g. "Navy"
    category_text     str   — free text, e.g. "Sweaters" or "Quarter-Zip Pullover"

Adapters should NOT apply filters themselves — filters.py handles that centrally.
Adapters should be defensive: wrap requests in try/except and return [] on failure
rather than crashing the whole run.
"""
import requests

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def safe_get(url: str, **kwargs):
    """GET with sane defaults + error handling. Returns Response or None."""
    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=15, **kwargs)
        if resp.status_code == 200:
            return resp
        print(f"[adapter] {url} returned status {resp.status_code}")
        return None
    except requests.RequestException as e:
        print(f"[adapter] request failed for {url}: {e}")
        return None
