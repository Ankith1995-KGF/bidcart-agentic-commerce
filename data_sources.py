from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class DataSource:
    name: str
    source_type: str
    category: str
    status: str
    last_checked: Optional[str] = None


DATA_SOURCES = [
    DataSource("Amazon", "RETAILER_CONNECTOR", "Multi-category", "PLANNED"),
    DataSource("Flipkart", "RETAILER_CONNECTOR", "Multi-category", "PLANNED"),
    DataSource("Croma", "RETAILER_CONNECTOR", "Electronics", "PLANNED"),
    DataSource("Reliance Digital", "RETAILER_CONNECTOR", "Electronics", "PLANNED"),
    DataSource("Myntra", "RETAILER_CONNECTOR", "Apparel & Footwear", "PLANNED"),
    DataSource("AJIO", "RETAILER_CONNECTOR", "Apparel & Footwear", "PLANNED"),
    DataSource("BigBasket", "RETAILER_CONNECTOR", "Grocery & FMCG", "PLANNED"),
    DataSource("Blinkit", "RETAILER_CONNECTOR", "Quick Commerce", "PLANNED"),
    DataSource("Zepto", "RETAILER_CONNECTOR", "Quick Commerce", "PLANNED"),
    DataSource("Swiggy Instamart", "RETAILER_CONNECTOR", "Quick Commerce", "PLANNED"),
]


def get_source_registry():
    return DATA_SOURCES


def timestamp_now():
    return datetime.now().isoformat(timespec="seconds")