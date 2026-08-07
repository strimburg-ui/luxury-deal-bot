"""
Adapter for finding deals on brands whose own retail sites block scraping
(Ralph Lauren, Peter Millar, Barbour, Brooks Brothers, etc.) by instead
searching eBay's official Browse API for new-condition listings.

Why this works when the retail sites don't: eBay's API is meant to be used
by outside apps, so there's no bot-blocking to fight — you just need a free
developer account and API key.

Setup required (one-time):
  1. Create a free account at https://developer.ebay.com
  2. Create an application to get an App ID (Client ID) and Cert ID (Client Secret)
  3. Add these as GitHub repo secrets: EBAY_CLIENT_ID, EBAY_CLIENT_SECRET

Docs: https://developer.ebay.com/api-docs/buy/browse/overview.html

Caveats (real limitations, not bugs):
  - Listing quality varies by seller — we filter to condition "NEW" but this
    is seller-reported, not verified.
  - Most sellers don't set an official strikethrough price, so we fall back
    to a rough typical-retail estimate per brand to compute an approximate
    discount %. This is an estimate, not a live retail price.
  - Sizes are guessed from the listing title (eBay's search API doesn't
    expose structured size data), so this is looser than the Shopify feeds.
"""
import base64
import os
import re

import requests

TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"

CLIENT_ID = os.environ.get("EBAY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("EBAY_CLIENT_SECRET")

# Brands whose own sites are blocked — search for these on eBay instead.
BLOCKED_BRANDS = [
    "Polo Ralph Lauren",
    "Peter Millar",
    "Barbour",
    "Brooks Brothers",
    "Vineyard Vines",
    "Lululemon",
    "J.Crew",
    "Banana Republic",
]

# Search each brand across these category terms separately (rather than one
# combined query) — eBay's search relevance narrows hard on multi-word
# queries, so splitting finds meaningfully more listings per brand.
SEARCH_CATEGORIES = [
    "sweater", "quarter zip", "trouser", "chino", "overshirt",
    "jogger", "short", "t-shirt", "sweatshirt",
]

# Most individual eBay sellers don't set an official strikethrough/MSRP price
# on their listing (that's mostly an eBay-certified-program feature), so we
# can rarely compute a real discount % from the listing data alone. As a
# fallback, we use rough typical retail prices per brand — these are
# estimates, not live prices, so treat the resulting discount % as approximate.
TYPICAL_RETAIL_PRICE = {
    "Polo Ralph Lauren": 130,
    "Peter Millar": 155,
    "Barbour": 230,
    "Brooks Brothers": 120,
    "Vineyard Vines": 115,
    "Lululemon": 95,
    "J.Crew": 90,
    "Banana Republic": 95,
}

SOURCE_NAME = "eBay"

SIZE_TOKEN_PATTERN = re.compile(
    r"\b(XS|S|M|L|XL|XXL|MT|LT|XLT|MED|MEDIUM|LARGE|SMALL|32X34|32/34|32-34)\b",
    re.IGNORECASE,
)
TALL_PATTERN = re.compile(r"\btall\b", re.IGNORECASE)


def _get_access_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("[ebay] missing EBAY_CLIENT_ID or EBAY_CLIENT_SECRET env vars")
        return None

    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }
    try:
        resp = requests.post(TOKEN_URL, headers=headers, data=data, timeout=15)
        if resp.status_code != 200:
            print(f"[ebay] token request failed: {resp.status_code} {resp.text}")
            return None
        return resp.json().get("access_token")
    except requests.RequestException as e:
        print(f"[ebay] token request error: {e}")
        return None


def _guess_sizes(title: str) -> list:
    matches = [m.upper() for m in SIZE_TOKEN_PATTERN.findall(title)]
    is_tall = bool(TALL_PATTERN.search(title))

    normalized = {"MEDIUM": "M", "LARGE": "L", "SMALL": "S", "MED": "M"}
    sizes = {normalized.get(m, m) for m in matches}

    if is_tall:
        # Combine base size + tall into one token, e.g. "M" + Tall -> "MT"
        sizes = {f"{s}T" if s in ("M", "L", "XL") else s for s in sizes}
        if not sizes:
            sizes = {"TALL"}

    return list(sizes)


def _search_brand_category(token: str, brand: str, category: str) -> list:
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
    }
    params = {
        "q": f"{brand} men's {category}",
        "filter": "conditions:{NEW},itemLocationCountry:US",
        "limit": "30",
    }

    try:
        resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=15)
    except requests.RequestException as e:
        print(f"[ebay] search failed for {brand} / {category}: {e}")
        return []

    if resp.status_code != 200:
        print(f"[ebay] search for {brand} / {category} returned status {resp.status_code}")
        return []

    try:
        data = resp.json()
    except ValueError:
        print(f"[ebay] search for {brand} / {category} did not return valid JSON")
        return []

    items = data.get("itemSummaries", [])
    deals = []

    for item in items:
        title = item.get("title", "")
        price_info = item.get("price", {})
        price = price_info.get("value")
        if price is None:
            continue
        price = float(price)

        # Prefer the seller's own strikethrough price if eBay provides one.
        original_price = None
        marketing_price = item.get("marketingPrice", {})
        if marketing_price:
            orig = marketing_price.get("originalPrice", {}).get("value")
            if orig is not None:
                original_price = float(orig)

        # Fall back to a rough typical-retail estimate for this brand so we
        # can still compute an approximate discount %.
        if original_price is None:
            original_price = TYPICAL_RETAIL_PRICE.get(brand)
        if original_price is None or original_price <= price:
            continue  # can't estimate a real discount — skip

        url = item.get("itemWebUrl", "")
        image_url = item.get("image", {}).get("imageUrl", "")

        deals.append({
            "deal_id": url,
            "source": SOURCE_NAME,
            "brand": brand,
            "title": title,
            "price": price,
            "original_price": original_price,
            "url": url,
            "available_sizes": _guess_sizes(title),
            "color": title,
            "category_text": title,
            "image_url": image_url,
        })

    return deals


def fetch_deals() -> list:
    token = _get_access_token()
    if not token:
        return []

    all_deals = []
    seen_ids = set()
    for brand in BLOCKED_BRANDS:
        brand_count = 0
        for category in SEARCH_CATEGORIES:
            category_deals = _search_brand_category(token, brand, category)
            for d in category_deals:
                if d["deal_id"] in seen_ids:
                    continue  # same listing matched more than one category search
                seen_ids.add(d["deal_id"])
                all_deals.append(d)
                brand_count += 1
        print(f"[ebay] {brand}: found {brand_count} listings with a computable discount")

    return all_deals
