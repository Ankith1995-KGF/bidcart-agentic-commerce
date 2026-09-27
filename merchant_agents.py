from dataclasses import dataclass


@dataclass
class MerchantAgent:
    name: str
    cost_price: float
    listed_price: float
    minimum_margin_pct: float
    inventory_pressure: float
    target_pressure: float

    @property
    def minimum_bid(self):
        """
        Lowest price the merchant can offer
        without violating its minimum margin.
        """
        return self.cost_price * (1 + self.minimum_margin_pct)

    def generate_bid(self, buyer_budget):
        """
        Merchant decides how aggressively to bid.

        Higher inventory and sales-target pressure
        make the merchant more willing to discount.
        """

        pressure = (
            self.inventory_pressure
            + self.target_pressure
        ) / 2

        maximum_discount = (
            self.listed_price - self.minimum_bid
        )

        proposed_discount = maximum_discount * pressure

        bid = self.listed_price - proposed_discount

        # Merchant cannot bid below its minimum viable price
        bid = max(bid, self.minimum_bid)

        # If buyer has declared a lower budget,
        # merchant tries to meet it when economically possible
        if buyer_budget >= self.minimum_bid:
            bid = min(bid, buyer_budget)

        return round(bid, 2)