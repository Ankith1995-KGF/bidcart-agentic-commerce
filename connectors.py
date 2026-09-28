import os
import sqlite3
import requests
from datetime import datetime

from retailers import Offer, get_retailers
from price_history import record_price

BRIGHTDATA_API_KEY = os.environ.get("BRIGHTDATA_API_KEY")
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
COMMERCE_DATABASE = BASE_DIR / "bidcart_commerce.db"
def search_market(product, category):
    """
    Search all relevant retailers for a product.

    Retailer-specific connectors will be added here.
    For now this returns an empty list rather than
    generating fake commerce data.
    """

    retailers = get_retailers(category)

    offers = []

    for retailer in retailers:
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] "
            f"Searching {retailer} for: {product}"
        )

    return offers


def normalize_product_key(product):
    """
    Convert a user's product search into a stable key
    that BidCart can use for price-history tracking.
    """
    return "-".join(
        product.lower().strip().split()
    )


def is_matching_product(search_product, result_title):
    """
    Check whether a shopping result is actually the product
    the user searched for, rather than an accessory or
    a different model.
    """

    if not result_title:
        return False

    search_text = search_product.lower().strip()
    title_text = result_title.lower().strip()

    normalized_search = search_text.replace("-", " ")
    normalized_title = title_text.replace("-", " ")

    # Extract tokens containing numbers.
    # These are especially useful for model-number products
    # such as WH-1000XM5.
    search_tokens = normalized_search.split()

    # Require the complete model identifier when one is present.
    # Example: WH-1000XM5 must not match WF-1000XM5.
    model_tokens = [
        token
        for token in search_text.split()
        if any(char.isdigit() for char in token)
    ]

    for model_token in model_tokens:
        comparable_model = model_token.replace(" ", "-")
        comparable_title = title_text.replace(" ", "-")

        if comparable_model not in comparable_title:
            return False

    # Exclude accessories that legitimately mention
    # the searched model because they are compatible with it.
    # BidCart compares new products by default.
    # Reject listings explicitly marked as used, pre-owned,
    # renewed or refurbished.
    used_condition_words = [
        "used",
        "pre-owned",
        "preowned",
        "second hand",
        "second-hand",
        "refurbished",
        "renewed",
        "中古",
    ]

    if any(word in title_text for word in used_condition_words):
        return False
    accessory_words = [
        "earpad",
        "earpads",
        "ear cushion",
        "ear cushions",
        "replacement",
        "case",
        "cover",
        "skin",
        "wrap",
        "protector",
        "cable",
        "adapter",
    ]

    if any(word in title_text for word in accessory_words):
        return False

    return True
def start_brightdata_product_search(product):
    """
    Start a Bright Data Google Shopping search
    for the canonical product resolved by BidCart.
    """

    if not BRIGHTDATA_API_KEY:
        raise RuntimeError("Bright Data API key is not configured.")

    url = (
        "https://api.brightdata.com/datasets/v3/scrape"
        "?dataset_id=gd_ltppk50q18kdw67omz"
        "&notify=false"
        "&include_errors=true"
        "&type=discover_new"
        "&discover_by=keyword"
    )

    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "input": [
            {
                "keyword": product,
                "country": "IN",
            }
        ],
        "limit_per_input": 10,
    }

    response = requests.post(
        url,
        headers=headers,
        json=data,
        timeout=30,
    )

    return response
def save_commerce_observation(
    product_key,
    product_name,
    retailer,
    price,
    rating=None,
    review_count=None,
    availability=None,
    product_url=None,
):
    """
    Save one validated commerce observation to BidCart's cache.
    """
    fetched_at = datetime.now().isoformat(timespec="seconds")

    with sqlite3.connect(COMMERCE_DATABASE) as connection:
        connection.execute(
            """
            INSERT INTO commerce_cache (
                product_key,
                product_name,
                retailer,
                price,
                rating,
                review_count,
                availability,
                product_url,
                fetched_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                product_key,
                product_name,
                retailer,
                float(price),
                rating,
                review_count,
                availability,
                product_url,
                fetched_at,
            ),
        )
def create_commerce_cache():
    """
    Create BidCart's local cache of validated commerce observations.
    """
    with sqlite3.connect(COMMERCE_DATABASE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS commerce_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_key TEXT NOT NULL,
                product_name TEXT NOT NULL,
                retailer TEXT NOT NULL,
                price REAL NOT NULL,
                rating REAL,
                review_count INTEGER,
                availability TEXT,
                product_url TEXT,
                fetched_at TEXT NOT NULL
            )
            """
        )


create_commerce_cache()
def has_cached_product(product):
    """
    Check whether BidCart already has cached commerce data
    for the exact normalized product.
    """
    product_key = normalize_product_key(product)

    with sqlite3.connect(COMMERCE_DATABASE) as connection:
        row = connection.execute(
            """
            SELECT 1
            FROM commerce_cache
            WHERE product_key = ?
            LIMIT 1
            """,
            (product_key,),
        ).fetchone()

    return row is not None
def get_cached_commerce(product_key):
    """
    Return cached commerce observations for a product,
    ordered from lowest to highest price.
    """
    with sqlite3.connect(COMMERCE_DATABASE) as connection:
        rows = connection.execute(
            """
            SELECT
                product_name,
                retailer,
                price,
                rating,
                review_count,
                availability,
                product_url,
                fetched_at
            FROM commerce_cache
            WHERE product_key = ?
            ORDER BY price ASC
            """,
            (product_key,),
        ).fetchall()

    return [
        {
            "product_name": row[0],
            "retailer": row[1],
            "price": row[2],
            "rating": row[3],
            "review_count": row[4],
            "availability": row[5],
            "product_url": row[6],
            "fetched_at": row[7],
        }
        for row in rows
    ]
