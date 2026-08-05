"""
Entry point. Run this daily (via GitHub Actions, see .github/workflows/daily.yml).

Flow:
    1. Loop through every source in config.SOURCES
    2. Call that adapter's fetch_deals()
    3. Run every deal through filters.passes_all_filters()
    4. For deals that pass, check tracker.should_alert() to dedup
    5. Send a Telegram digest of everything new
"""
import importlib
import traceback

from config import SOURCES
from filters import passes_all_filters
from tracker import init_db, should_alert, record_deal
from notifier import send_daily_digest


def run():
    init_db()
    new_deals = []

    for source_module in SOURCES:
        try:
            adapter = importlib.import_module(f"adapters.{source_module}")
        except ImportError as e:
            print(f"[main] could not import adapter '{source_module}': {e}")
            continue

        try:
            raw_deals = adapter.fetch_deals()
        except Exception:
            print(f"[main] adapter '{source_module}' raised an error:")
            traceback.print_exc()
            continue

        print(f"[main] {source_module}: fetched {len(raw_deals)} raw listings")

        for deal in raw_deals:
            if not passes_all_filters(deal):
                continue
            if should_alert(deal["deal_id"], deal["price"]):
                new_deals.append(deal)
            record_deal(deal)

    print(f"[main] {len(new_deals)} new deal(s) matched all filters and are new/price-dropped")
    send_daily_digest(new_deals)


if __name__ == "__main__":
    run()
