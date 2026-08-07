"""
Central configuration for the luxury deal bot.
Edit this file to tune brands, sizing, colors, and thresholds.
"""

# ---- Brand tiers (used for prioritization / labeling in alerts, not filtering) ----
BRAND_TIERS = {
    "S": [
        "Polo Ralph Lauren", "Ralph Lauren", "Peter Millar", "Todd Snyder",
        "Barbour", "Vineyard Vines",
    ],
    "A": [
        "Brooks Brothers", "J.Crew", "Billy Reid", "Faherty", "Rodd & Gunn",
        "Onward Reserve", "Drake's", "Rhoback", "Johnnie-O", "Buck Mason",
        "UNTUCKit", "Ledbury", "Alex Mill", "Southern Tide", "Bills Khakis",
        "Grayers",
    ],
    "B": [
        "Zegna", "Canali", "Loro Piana", "Brunello Cucinelli", "Paul Stuart",
        "Lacoste", "Ralph Lauren Purple Label",
    ],
    "C": [
        "Dior", "Saint Laurent", "Burberry", "Ferragamo", "Prada", "Gucci",
        "Ami Paris", "Theory",
    ],
}

# Flat lookup: brand name -> tier
def _flatten_tiers():
    flat = {}
    for tier, brands in BRAND_TIERS.items():
        for b in brands:
            flat[b.lower()] = tier
    return flat

BRAND_TIER_LOOKUP = _flatten_tiers()

# ---- Sizing ----
TOP_SIZES_ACCEPTABLE = ["M TALL", "MT", "L TALL", "LT", "L", "M"]  # preference order
PANT_WAIST = 32
PANT_INSEAM = 34
PANT_SIZE_STRINGS = ["32x34", "32 x 34", "32W 34L", "32/34"]

# ---- Colors (substring match, case-insensitive) ----
TARGET_COLORS = [
    "navy", "cream", "beige", "light blue", "sky blue", "grey", "gray",
    "ivory", "stone", "khaki", "black",
]

# ---- Categories (substring match against product title/category) ----
TARGET_CATEGORIES = [
    "sweater", "quarter-zip", "quarter zip", "1/4 zip", "overshirt",
    "knit", "trouser", "chino", "cardigan", "half-zip", "half zip",
    "shirt", "button-down", "button down", "oxford",
    "jogger", "short", "t-shirt", "tee", "sweatshirt", "hoodie",
]

# ---- Discount threshold ----
MIN_DISCOUNT_PERCENT = 30

# Items at or below their category's price ceiling show up regardless of
# discount % — catches genuinely cheap finds (e.g. eBay listings with no
# marked "original" price) that would otherwise get filtered out for
# showing 0% off. Checked in order — first matching category wins, so more
# specific/pricier categories are listed before broader ones.
# Format: (category_label, [keywords to match], price_ceiling)
LOW_PRICE_BY_CATEGORY = [
    ("Outerwear",     ["jacket", "coat", "vest", "overshirt"], 65),
    ("Sweaters",      ["sweater", "quarter-zip", "quarter zip", "1/4 zip",
                        "half-zip", "half zip", "cardigan", "knit"], 45),
    ("Trousers",      ["trouser", "chino", "jogger", "pant"], 35),
    ("Sweatshirts",   ["sweatshirt", "hoodie"], 30),
    ("Button-downs",  ["button-down", "button down", "oxford"], 30),
    ("Polos",         ["polo"], 25),
    ("Shorts",        ["short"], 20),
    ("Tees",          ["t-shirt", "tee", "tshirt"], 15),
]
# Fallback for anything that doesn't match a category above.
LOW_PRICE_DEFAULT = 25

# ---- Sources to check ----
# Each entry maps to an adapter module in adapters/ with a matching function `fetch_deals()`
SOURCES = [
    "todd_snyder",
    "faherty",
    "billy_reid",
    "ledbury",
    "alex_mill",
    "untuckit",
    "southern_tide",
    "bills_khakis",
    "grayers",
    "ebay",
]

# The sources below are confirmed blocked by enterprise bot-protection
# (Incapsula, Akamai, Salesforce Commerce Cloud) as of testing — their own
# adapter files are still in adapters/ if you ever want to re-enable one.
# eBay's adapter already covers these five brands via marketplace listings.
#
# BLOCKED_SOURCES = [
#     "polo_ralph_lauren",
#     "peter_millar",
#     "barbour",
#     "vineyard_vines",
#     "brooks_brothers",
#     "jcrew",
#     "nordstrom_rack",
#     "macys",
#     "luxury_garage_sale",
# ]

# ---- Storage ----
DB_PATH = "seen_deals.db"
