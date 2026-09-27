from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MarketOffer:
    product_name: str
    merchant: str
    listed_price: float
    mrp: Optional[float] = None
    delivery_fee: float = 0
    coupon_discount: float = 0
    bank_discount: float = 0
    cashback: float = 0
    availability: str = "Available"
    source_type: str = "UNKNOWN"
    source_url: Optional[str] = None
    fetched_at: Optional[str] = None

    @property
    def effective_price(self):
        return (
            self.listed_price
            + self.delivery_fee
            - self.coupon_discount
            - self.bank_discount
            - self.cashback
        )


def normalize_offer(offer):
    """
    Converts a merchant offer into BidCart's common economic format.
    """

    if not offer.fetched_at:
        offer.fetched_at = datetime.now().isoformat(timespec="seconds")

    return offer