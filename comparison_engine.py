from offer_engine import MarketOffer


def rank_offers(offers):
    """
    Rank offers from lowest to highest effective price.
    """
    return sorted(
        offers,
        key=lambda offer: offer.effective_price
    )


def find_best_offer(offers):
    """
    Return the offer with the lowest effective price.
    """
    if not offers:
        return None

    ranked = rank_offers(offers)
    return ranked[0]


def calculate_savings(best_offer, other_offer):
    """
    Calculate how much the buyer saves compared with another offer.
    """
    return other_offer.effective_price - best_offer.effective_price