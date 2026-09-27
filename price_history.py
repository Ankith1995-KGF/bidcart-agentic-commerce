import sqlite3
from datetime import datetime, timedelta
from statistics import median


DATABASE_NAME = "bidcart_prices.db"


def create_price_history_table():
    """Create the local price-history database if it does not already exist."""

    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_key TEXT NOT NULL,
                product_name TEXT NOT NULL,
                retailer TEXT NOT NULL,
                price REAL NOT NULL,
                observed_at TEXT NOT NULL
            )
            """
        )


def record_price(product_key, product_name, retailer, price):
    """Store one observed retailer price."""

    observed_at = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(DATABASE_NAME) as connection:
        connection.execute(
            """
            INSERT INTO price_history
            (product_key, product_name, retailer, price, observed_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                product_key,
                product_name,
                retailer,
                float(price),
                observed_at,
            ),
        )


def get_30_day_price_intelligence(product_key):
    """Return truthful 30-day price intelligence from observed prices."""
    cutoff = (datetime.now() - timedelta(days=30)).isoformat(timespec="seconds")

    with sqlite3.connect(DATABASE_NAME) as connection:
        rows = connection.execute(
            """
            SELECT retailer, price, observed_at
            FROM price_history
            WHERE product_key = ?
              AND observed_at >= ?
            ORDER BY observed_at DESC
            """,
            (product_key, cutoff),
        ).fetchall()

    if not rows:
        return {
            "observation_count": 0,
            "current_price": None,
            "low": None,
            "high": None,
            "days_observed_at_low": 0,
            "last_seen_at_low": None,
            "history": [],
        }

    prices = [float(row[1]) for row in rows]

    current_price = prices[0]
    low_price = min(prices)
    high_price = max(prices)

    low_price_rows = [
        row for row in rows
        if float(row[1]) == low_price
    ]

    low_price_dates = {
        datetime.fromisoformat(row[2]).date()
        for row in low_price_rows
    }

    days_observed_at_low = len(low_price_dates)

    last_seen_at_low = max(
        datetime.fromisoformat(row[2])
        for row in low_price_rows
    ).isoformat(timespec="seconds")

    return {
        "observation_count": len(prices),
        "current_price": current_price,
        "low": low_price,
        "high": high_price,
        "days_observed_at_low": days_observed_at_low,
        "last_seen_at_low": last_seen_at_low,
        "history": [
            {
                "retailer": row[0],
                "price": float(row[1]),
                "observed_at": row[2],
            }
            for row in rows
        ],
    }
create_price_history_table()