import streamlit as st
from price_history import get_30_day_price_intelligence
from catalog import PRODUCT_CATEGORIES
from retailers import get_retailers
from payment_agent import (
    PaymentInstrument,
    PaymentOffer,
    rank_payment_options,
    authorization_readiness,
)
from connectors import (
    normalize_product_key,
    is_matching_product,
    get_cached_commerce,
    has_cached_product,
)
from product_identity import find_product_candidates

from payment_agent import (
    PaymentInstrument,
    PaymentOffer,
    evaluate_payment_option,
    rank_payment_options,
    authorization_readiness,
)
if "screen" not in st.session_state:
    st.session_state.screen = "search"

show_search = st.session_state.screen == "search"
# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="BidCart",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------
# STYLING
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(circle at 15% 0%,
            rgba(99,102,241,0.10), transparent 30%),
            radial-gradient(circle at 90% 10%,
            rgba(14,165,233,0.08), transparent 28%),
            #f8fafc;
    }

    .block-container {
        max-width: 1120px;
        padding-top: 1.4rem;
        padding-bottom: 4rem;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        min-height: 48px;
        border-radius: 12px;
    }

    div[data-baseweb="select"] > div {
        min-height: 48px;
        border-radius: 12px;
    }

    .stButton > button {
        min-height: 50px;
        border-radius: 12px;
        font-weight: 700;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# BRAND
# ---------------------------------------------------------

st.markdown("### 🛒 BidCart")

st.caption("AGENTIC COMMERCE INTELLIGENCE")

st.markdown(
    """
    # Don't just find a product.
    # **Know if it's actually a good deal.**
    """
)

st.write(
    "BidCart independently evaluates price history, customer evidence "
    "and payment economics before you buy."
)

st.divider()

# ---------------------------------------------------------
# COMMERCE SEARCH
# ---------------------------------------------------------

if st.session_state.screen == "results":
    st.markdown(
        """
        <style>
        div[data-testid="stVerticalBlock"]:has(
            button[kind="primary"]
        ) {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

st.subheader("What are you looking to buy?")

category_col, subcategory_col = st.columns(2)

with category_col:

    category = st.selectbox(
        "Product category",
        list(PRODUCT_CATEGORIES.keys()),
    )

with subcategory_col:

    subcategory = st.selectbox(
        "Sub-category",
        PRODUCT_CATEGORIES[category],
    )

product = st.text_input(
    "Product",
    placeholder=(
        "e.g. Surf Excel Matic 2 kg, "
        "Nike running shoes, Sony headphones..."
    ),
)

city = st.text_input(
    "Delivery city",
    placeholder="e.g. Chennai, Bengaluru, Mumbai",
)
budget_col, retailer_col = st.columns([1, 2])

with budget_col:
    st.markdown("**Budget range (₹)**")

    min_budget_col, max_budget_col = st.columns(2)

    with min_budget_col:
        min_budget = st.number_input(
            "Minimum",
            min_value=0,
            step=100,
            placeholder="e.g. 20000",
        )

    with max_budget_col:
        max_budget = st.number_input(
            "Maximum",
            min_value=0,
            step=100,
            placeholder="e.g. 30000",
        )

with retailer_col:
    st.markdown("**Retailers BidCart will evaluate**")

    retailers = get_retailers(category)

    st.write(" · ".join(retailers))

st.markdown("")

search = st.button(
    "Find the Best Deal →",
    type="primary",
    use_container_width=True,
)
if search:
    if not product.strip():
        st.error("Enter the product you want BidCart to evaluate.")
        st.stop()

    if not city.strip():
        st.error("Enter your delivery city.")
        st.stop()

    if max_budget > 0 and min_budget > max_budget:
        st.error("Minimum budget cannot be higher than maximum budget.")
        st.stop()

    st.session_state.search_product = product
    st.session_state.search_city = city
    st.session_state.search_min_budget = min_budget
    st.session_state.search_max_budget = max_budget
    st.session_state.search_retailers = retailers
    st.session_state.screen = "results"

    st.rerun()
if st.session_state.screen == "results":
    result_product = st.session_state.search_product
    result_city = st.session_state.search_city
    result_min = st.session_state.search_min_budget
    result_max = st.session_state.search_max_budget
    preferred_retailers = st.session_state.search_retailers

    if st.button("← New Search"):
        st.session_state.screen = "search"
        st.rerun()

    st.markdown("# BidCart Decision")
    st.caption(
        f"{result_product} · Delivery city: {result_city}"
    )

    product_key = normalize_product_key(result_product)
    all_offers = get_cached_commerce(product_key)

    # Apply customer's budget to all validated offers.
    if result_min > 0:
        all_offers = [
            offer for offer in all_offers
            if offer["price"] >= result_min
        ]

    if result_max > 0:
        all_offers = [
            offer for offer in all_offers
            if offer["price"] <= result_max
        ]

    preferred_names = [
        retailer.lower()
        for retailer in preferred_retailers
    ]

    preferred_offers = [
        offer for offer in all_offers
        if offer["retailer"].lower() in preferred_names
    ]

    market_offers = [
        offer for offer in all_offers
        if offer["retailer"].lower() not in preferred_names
    ]

    st.markdown("### Preferred Retailers")

    if preferred_offers:
        for offer in preferred_offers:
            rating = (
                f"{offer['rating']:.1f}★"
                if offer["rating"] is not None
                else "Rating unavailable"
            )

            reviews = (
                f"{offer['review_count']:,} reviews"
                if offer["review_count"] is not None
                else "Review count unavailable"
            )

            st.write(
                f"**{offer['retailer']}** — "
                f"₹{offer['price']:,.2f} · "
                f"{rating} · {reviews}"
            )
    else:
        st.info(
            "No validated offer is currently available from "
            "your preferred retailers."
        )

    st.markdown("### Other Validated Market Offers")

    if market_offers:
        market_offers = sorted(
            market_offers,
            key=lambda offer: offer["price"],
        )

        for offer in market_offers:
            rating = (
                f"{offer['rating']:.1f}★"
                if offer["rating"] is not None
                else "Rating unavailable"
            )

            reviews = (
                f"{offer['review_count']:,} reviews"
                if offer["review_count"] is not None
                else "Review count unavailable"
            )

            with st.container(border=True):
                st.markdown(
                    f"### {offer['retailer']}"
                )

                st.write(
                    f"**₹{offer['price']:,.2f}** · "
                    f"{rating} · {reviews}"
                )

                if offer["product_url"]:
                    st.link_button(
                        "View retailer offer →",
                        offer["product_url"],
                    )
    else:
        st.info(
            "No additional validated market offers are "
            "currently available within your budget."
        )
    st.markdown("### 💳 Card & Bank Offer Intelligence")

    st.caption(
        "Enter an offer published by the retailer or bank. "
        "BidCart calculates eligibility and effective cost."
    )

    pay1, pay2, pay3 = st.columns(3)

    with pay1:
        bank = st.text_input(
            "Bank / issuer",
            placeholder="e.g. HDFC",
        )

    with pay2:
        network = st.selectbox(
            "Card network",
            ["Visa", "Mastercard", "RuPay", "Amex"],
        )

    with pay3:
        instrument_type = st.selectbox(
            "Card type",
            ["Credit", "Debit"],
        )

    offer_url = st.text_input(
        "Official offer terms link",
        placeholder="Paste bank or retailer offer URL",
    )
    st.stop()
    offer1, offer2, offer3 = st.columns(3)

    with offer1:
        discount_pct = st.number_input(
            "Instant discount (%)",
            min_value=0.0,
            max_value=100.0,
            step=1.0,
        )

    with offer2:
        max_discount = st.number_input(
            "Maximum discount (₹)",
            min_value=0.0,
            step=100.0,
        )

    with offer3:
        minimum_transaction = st.number_input(
            "Minimum transaction (₹)",
            min_value=0.0,
            step=500.0,
        )

    if all_offers and bank.strip():
        best_offer = min(
            all_offers,
            key=lambda offer: offer["price"],
        )

        instrument = PaymentInstrument(
            name=f"{bank} {network} {instrument_type}",
            issuer=bank,
            network=network,
            instrument_type=instrument_type,
        )

        payment_offer = PaymentOffer(
            offer_name="Published card offer",
            issuer=bank,
            network=network,
            instrument_type=instrument_type,
            discount_pct=discount_pct,
            max_discount=max_discount,
            minimum_transaction=minimum_transaction,
        )

        decisions = rank_payment_options(
            best_offer["price"],
            [instrument],
            [payment_offer],
        )

        if decisions:
            decision = decisions[0]

            st.success(
                f"Eligible · Instant discount "
                f"₹{decision.instant_discount:,.2f} · "
                f"Effective cost ₹{decision.effective_cost:,.2f}"
            )

            if offer_url.strip():
                st.link_button(
                    "View official offer terms →",
                    offer_url,
                )
        else:
            st.warning(
                "This card offer is not eligible for the transaction."
            )


st.divider()

# ---------------------------------------------------------
# PRODUCT CAPABILITIES
# ---------------------------------------------------------

st.subheader("What BidCart will evaluate")

c1, c2, c3 = st.columns(3)

with c1:

    with st.container(border=True):

        st.markdown("### 📉 Price Intelligence")

        st.write(
            "Track validated price observations over time and identify "
            "30-day lows, highs and how often the lowest price was observed."
        )
with c2:

    with st.container(border=True):

        st.markdown("### ⭐ Customer Evidence")

        st.write(
            "Compare absolute positive-review evidence "
            "instead of relying only on star ratings."
        )

with c3:

    with st.container(border=True):

        st.markdown("### 💳 Payment Economics")

        st.write(
            "Resolve offer eligibility, discounts and "
            "effective transaction cost before checkout."
        )

st.caption(
    "BidCart provides independent pre-purchase and "
    "pre-authorization intelligence. Payments remain "
    "with the merchant and payment network."
)