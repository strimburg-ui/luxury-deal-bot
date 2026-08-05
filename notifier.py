"""
Sends deal alerts to your phone via a Telegram bot.

Setup (one-time, ~5 minutes):
1. In Telegram, message @BotFather -> /newbot -> follow prompts -> copy the BOT TOKEN it gives you.
2. Message your new bot anything (e.g. "hi") so it's allowed to message you back.
3. Visit https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates in a browser and find your "chat":{"id": ...}
   That number is your CHAT_ID.
4. Set these as GitHub repo secrets: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
   (Settings -> Secrets and variables -> Actions -> New repository secret)
"""
import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_message(text: str):
    if not BOT_TOKEN or not CHAT_ID:
        print("[notifier] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID env vars — skipping send.")
        print(text)
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    resp = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    })
    if resp.status_code != 200:
        print(f"[notifier] Telegram send failed: {resp.status_code} {resp.text}")


def format_deal_message(deal: dict, tier: str) -> str:
    return (
        f"🟢 <b>Tier {tier}</b> — {deal['brand']}\n"
        f"{deal['title']}\n"
        f"💰 ${deal['price']:.2f} (was ${deal['original_price']:.2f}, "
        f"{deal['discount_percent']}% off)\n"
        f"📦 Source: {deal['source']}\n"
        f"🔗 {deal['url']}"
    )


def send_daily_digest(deals: list):
    if not deals:
        send_message("No new deals matching your filters today.")
        return

    send_message(f"🛍️ {len(deals)} new deal(s) found today:")
    for deal in deals:
        from filters import tier_for_brand
        tier = tier_for_brand(deal["brand"])
        send_message(format_deal_message(deal, tier))
