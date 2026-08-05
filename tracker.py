"""
Tracks previously-seen deals so we only alert on NEW matches or price drops.
Uses SQLite so state persists between GitHub Actions runs (see .github/workflows/daily.yml
for how the DB file is cached/restored between runs).
"""
import sqlite3
from contextlib import contextmanager

from config import DB_PATH


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS seen_deals (
                deal_id TEXT PRIMARY KEY,
                source TEXT,
                brand TEXT,
                title TEXT,
                price REAL,
                last_seen_price REAL,
                url TEXT,
                first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
                last_seen TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def should_alert(deal_id: str, current_price: float) -> bool:
    """
    Returns True if this deal is new, or if the price dropped since we last saw it.
    Updates the record either way.
    """
    with _conn() as conn:
        row = conn.execute(
            "SELECT last_seen_price FROM seen_deals WHERE deal_id = ?", (deal_id,)
        ).fetchone()

        if row is None:
            return True  # brand new deal, always alert

        last_price = row[0]
        return current_price < last_price  # only alert again if price dropped further


def record_deal(deal: dict):
    with _conn() as conn:
        conn.execute("""
            INSERT INTO seen_deals (deal_id, source, brand, title, price, last_seen_price, url, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(deal_id) DO UPDATE SET
                last_seen_price = excluded.last_seen_price,
                last_seen = CURRENT_TIMESTAMP
        """, (
            deal["deal_id"], deal["source"], deal["brand"], deal["title"],
            deal["price"], deal["price"], deal["url"],
        ))
