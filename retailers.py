from dataclasses import dataclass
from typing import Optional


@dataclass
class Offer:
    retailer: str
    product_name: str
    price: float
    mrp: Optional[float] = None
    availability: str = "Unknown"
    product_url: Optional[str] = None
    source_type: str = "PUBLIC"
    fetched_at: Optional[str] = None


RETAILERS = {
    "Groceries": [
        "Blinkit",
        "Zepto",
        "Swiggy Instamart",
        "BigBasket"
    ],

    "Fruits & Vegetables": [
        "Blinkit",
        "Zepto",
        "Swiggy Instamart",
        "BigBasket"
    ],

    "FMCG": [
        "Amazon",
        "Flipkart",
        "Blinkit",
        "Zepto",
        "Swiggy Instamart",
        "BigBasket"
    ],

    "Consumer Electronics": [
        "Amazon",
        "Flipkart",
        "Croma",
        "Reliance Digital"
    ],

    "Apparel": [
        "Amazon",
        "Flipkart",
        "Myntra",
        "AJIO"
    ],

    "Footwear": [
        "Amazon",
        "Flipkart",
        "Myntra",
        "AJIO"
    ]
}


def get_retailers(category):
    return RETAILERS.get(category, [])