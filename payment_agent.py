from dataclasses import dataclass
from typing import Optional, List


@dataclass
class PaymentInstrument:
    name: str
    issuer: str
    network: str
    instrument_type: str


@dataclass
class PaymentOffer:
    offer_name: str
    issuer: Optional[str] = None
    network: Optional[str] = None
    instrument_type: Optional[str] = None

    discount_pct: float = 0
    max_discount: float = 0
    flat_discount: float = 0
    cashback: float = 0

    minimum_transaction: float = 0
    emi_required: bool = False
    emi_excluded: bool = False


@dataclass
class PaymentDecision:
    instrument: PaymentInstrument
    offer: Optional[PaymentOffer]

    checkout_amount: float
    instant_discount: float
    cashback: float
    effective_cost: float

    eligible: bool
    reason: str


def check_offer_eligibility(
    checkout_amount: float,
    instrument: PaymentInstrument,
    offer: PaymentOffer,
    using_emi: bool = False
):
    """
    Determine whether a payment instrument qualifies
    for a merchant payment offer.
    """

    if checkout_amount < offer.minimum_transaction:
        return False, "Minimum transaction value not met"

    if offer.issuer:
        if instrument.issuer.lower() != offer.issuer.lower():
            return False, "Issuer not eligible"

    if offer.network:
        if instrument.network.lower() != offer.network.lower():
            return False, "Card network not eligible"

    if offer.instrument_type:
        if instrument.instrument_type.lower() != offer.instrument_type.lower():
            return False, "Payment instrument type not eligible"

    if offer.emi_required and not using_emi:
        return False, "Offer requires EMI"

    if offer.emi_excluded and using_emi:
        return False, "Offer excludes EMI transactions"

    return True, "Eligible"


def calculate_offer_benefit(
    checkout_amount: float,
    offer: PaymentOffer
):
    """
    Calculate the actual monetary benefit instead
    of relying on the advertised 'up to' amount.
    """

    percentage_discount = (
        checkout_amount * offer.discount_pct / 100
    )

    if offer.discount_pct > 0 and offer.max_discount > 0:
        percentage_discount = min(
            percentage_discount,
            offer.max_discount
        )

    instant_discount = (
        percentage_discount + offer.flat_discount
    )

    cashback = offer.cashback

    return round(instant_discount, 2), round(cashback, 2)


def evaluate_payment_option(
    checkout_amount: float,
    instrument: PaymentInstrument,
    offer: PaymentOffer,
    using_emi: bool = False
):
    """
    Evaluate one payment instrument + offer combination.
    """

    eligible, reason = check_offer_eligibility(
        checkout_amount,
        instrument,
        offer,
        using_emi
    )

    if not eligible:
        return PaymentDecision(
            instrument=instrument,
            offer=offer,
            checkout_amount=checkout_amount,
            instant_discount=0,
            cashback=0,
            effective_cost=checkout_amount,
            eligible=False,
            reason=reason
        )

    instant_discount, cashback = calculate_offer_benefit(
        checkout_amount,
        offer
    )

    effective_cost = (
        checkout_amount
        - instant_discount
        - cashback
    )

    return PaymentDecision(
        instrument=instrument,
        offer=offer,
        checkout_amount=checkout_amount,
        instant_discount=instant_discount,
        cashback=cashback,
        effective_cost=round(effective_cost, 2),
        eligible=True,
        reason="Offer applicable"
    )


def rank_payment_options(
    checkout_amount: float,
    instruments: List[PaymentInstrument],
    offers: List[PaymentOffer]
):
    """
    Evaluate all instrument/offer combinations and rank
    eligible options by effective transaction cost.
    """

    decisions = []

    for instrument in instruments:
        for offer in offers:

            decision = evaluate_payment_option(
                checkout_amount,
                instrument,
                offer
            )

            if decision.eligible:
                decisions.append(decision)

    decisions.sort(
        key=lambda decision: decision.effective_cost
    )

    return decisions


def authorization_readiness(
    expected_amount: float,
    final_checkout_amount: float,
    maximum_authorized_amount: float
):
    """
    Pre-payment intent check.

    This does NOT authorize or execute a payment.
    It only determines whether the proposed checkout
    remains within the consumer's stated boundaries.
    """

    if final_checkout_amount > maximum_authorized_amount:
        return {
            "status": "REVIEW_REQUIRED",
            "reason": "Checkout exceeds consumer's maximum authorized amount",
            "difference": round(
                final_checkout_amount - maximum_authorized_amount,
                2
            )
        }

    if final_checkout_amount > expected_amount:
        return {
            "status": "REVIEW_REQUIRED",
            "reason": "Checkout amount increased from expected amount",
            "difference": round(
                final_checkout_amount - expected_amount,
                2
            )
        }

    return {
        "status": "READY_FOR_AUTHORIZATION",
        "reason": "Transaction remains within stated consumer intent",
        "difference": 0
    }