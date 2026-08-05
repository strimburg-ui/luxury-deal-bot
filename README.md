# Luxury Deal Bot

Daily check across your target brands + discounters for items matching your
size (M/L Tall tops, 32x34 pants), colors (navy/cream/beige/light blue/gray),
categories (sweaters, quarter-zips, overshirts, knits, trousers), and a
minimum 30% discount. Alerts are sent to you via Telegram.

## ⚠️ Important — read this first

The site adapters in `adapters/` are **templates**, not finished scrapers.
I built the full framework (filtering, dedup, scheduling, notifications) and
one worked example (`adapters/peter_millar.py`), but I don't have the ability
to browse the actual retail sites from where I built this, so I can't verify
their real HTML structure. Every adapter has placeholder CSS selectors marked
`# ADJUST ME` — you (or I, in a future chat where you paste in a page's HTML)
need to fill those in with the real selectors before that source will return
results.

This is genuinely a bit of ongoing maintenance: retail sites change their
layouts periodically, and some (especially big-box retailers like Nordstrom
Rack/Macy's) use bot-detection that may block simple scripted requests
entirely — for those, it's often more reliable to set up their **native
saved-search/price-alert emails** instead and skip scraping them.

## How to finish setting up an adapter

1. Open the sale page (e.g. `https://www.petermillar.com/sale/mens/`) in Chrome
2. Right-click a product card → Inspect
3. Find the actual class names for: product container, title, price, sale
   price, color, size options, and link
4. Paste those into the matching adapter file, replacing the `# ADJUST ME` lines
5. Test locally: `python -c "from adapters.peter_millar import fetch_deals; print(fetch_deals())"`

Feel free to paste a site's HTML back to me in a future chat and I'll write
the real selectors for you.

## One-time setup

### 1. Create your Telegram bot
1. In Telegram, message **@BotFather** → send `/newbot` → follow the prompts
2. Copy the **bot token** it gives you
3. Send your new bot any message (e.g. "hi") so it's allowed to reply to you
4. Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser
   and find `"chat":{"id": ...}` — that number is your **chat ID**

### 2. Create a GitHub repo
1. Create a new **private** repo (e.g. `luxury-deal-bot`)
2. Push this project to it:
   ```bash
   cd luxury-deal-bot
   git init
   git add .
   git commit -m "Initial setup"
   git branch -M main
   git remote add origin https://github.com/<you>/luxury-deal-bot.git
   git push -u origin main
   ```

### 3. Add your secrets
In the repo: **Settings → Secrets and variables → Actions → New repository secret**
- `TELEGRAM_BOT_TOKEN` — from step 1
- `TELEGRAM_CHAT_ID` — from step 1

### 4. Test it
Go to the **Actions** tab → **Daily Deal Check** → **Run workflow** (this
triggers it manually so you don't have to wait for the schedule). Check your
Telegram for the digest message.

Once that works, it'll run automatically every day at 9 AM Eastern — no
computer or babysitting required.

## Tuning your filters

Everything you'd want to adjust lives in `config.py`:
- `MIN_DISCOUNT_PERCENT` — currently 30
- `TARGET_COLORS`, `TARGET_CATEGORIES` — substring matches
- `TOP_SIZES_ACCEPTABLE`, `PANT_SIZE_STRINGS` — your sizing
- `BRAND_TIERS` — add/remove brands or move them between tiers
- `SOURCES` — which adapters actually run each day

## Project structure

```
luxury-deal-bot/
├── config.py              # your brands, sizes, colors, discount threshold
├── filters.py              # shared filtering logic
├── tracker.py               # SQLite dedup — only alerts on new/lower prices
├── notifier.py             # Telegram sending
├── main.py                  # orchestrator — run this to check for deals
├── requirements.txt
├── adapters/
│   ├── base.py               # shared HTTP helper
│   ├── peter_millar.py       # fully worked example
│   └── ...                   # one file per source, all templates
└── .github/workflows/daily.yml   # free daily scheduler
```
