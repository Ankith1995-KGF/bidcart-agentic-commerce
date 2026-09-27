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

    /* ---------- BIDCART GLOBAL ---------- */

    .stApp {
        background:
            radial-gradient(circle at 5% 0%,
                rgba(16,185,129,0.10), transparent 25%),
            radial-gradient(circle at 95% 5%,
                rgba(37,99,235,0.10), transparent 28%),
            linear-gradient(180deg, #ffffff 0%, #f8fafc 55%, #f1f5f9 100%);
        color: #172033;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.25rem;
        padding-bottom: 5rem;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    /* ---------- TYPOGRAPHY ---------- */

    h1 {
        letter-spacing: -1.4px;
        color: #111827;
    }

    h2, h3 {
        color: #172033;
    }

    p {
        line-height: 1.65;
    }

    /* ---------- INPUTS ---------- */

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {
        min-height: 50px;
        border-radius: 14px;
        border: 1px solid #dbe3ec;
        background: #ffffff;
    }

    div[data-baseweb="select"] > div {
        min-height: 50px;
        border-radius: 14px;
        border-color: #dbe3ec;
        background: #ffffff;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus {
        border-color: #14b8a6;
        box-shadow: 0 0 0 1px #14b8a6;
    }

    /* ---------- BUTTONS ---------- */

    .stButton > button {
        min-height: 52px;
        border-radius: 14px;
        font-weight: 800;
        padding-left: 1.6rem;
        padding-right: 1.6rem;
        transition: all 0.18s ease;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(
            90deg,
            #0f766e 0%,
            #0d9488 45%,
            #2563eb 100%
        );
        color: white;
        border: 0;
        box-shadow: 0 8px 22px rgba(13,148,136,0.20);
    }

    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 11px 26px rgba(37,99,235,0.22);
    }

    .stLinkButton > a {
        border-radius: 12px;
        font-weight: 700;
    }

    /* ---------- CARDS ---------- */

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px;
        border-color: #e2e8f0;
        background: rgba(255,255,255,0.94);
        box-shadow: 0 5px 20px rgba(15,23,42,0.05);
    }

    /* ---------- ALERTS ---------- */

    div[data-testid="stAlert"] {
        border-radius: 14px;
    }

    /* ---------- CATEGORY STRIP ---------- */

    .category-strip {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 20px 0 28px 0;
    }

    .category-tile {
        padding: 16px;
        border-radius: 17px;
        font-weight: 800;
        text-align: center;
        box-shadow: 0 5px 18px rgba(15,23,42,0.05);
    }

    .grocery-tile {
        background: linear-gradient(135deg, #dcfce7, #bbf7d0);
        color: #166534;
    }

    .electronics-tile {
        background: linear-gradient(135deg, #111827, #334155);
        color: #ffffff;
    }

    .women-tile {
        background: linear-gradient(135deg, #fce7f3, #fbcfe8);
        color: #be185d;
    }

    .men-tile {
        background: linear-gradient(135deg, #dbeafe, #bfdbfe);
        color: #1d4ed8;
    }

    .sports-tile {
        background: linear-gradient(135deg, #ffedd5, #fed7aa);
        color: #c2410c;
}

    .footwear-tile {
        background: linear-gradient(135deg, #ede9fe, #ddd6fe);
        color: #6d28d9;
}
    .home-tile {
        background: linear-gradient(135deg, #fef3c7, #fde68a);
        color: #92400e;
}

    .beauty-tile {
        background: linear-gradient(135deg, #fae8ff, #f5d0fe);
        color: #a21caf;
}

    /* ---------- RETAILER BADGES ---------- */

    .retailer-row {
        display: flex;
        flex-wrap: wrap;
        gap: 9px;
        margin-top: 8px;
        margin-bottom: 12px;
    }

    .retailer-badge {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 999px;
        padding: 7px 13px;
        font-size: 0.86rem;
        font-weight: 750;
        box-shadow: 0 3px 10px rgba(15,23,42,0.04);
    }

    /* ---------- HERO ---------- */
    .bidcart-hero {
        padding: 30px 32px;
        border-radius: 24px;
        background: linear-gradient(
            120deg,
            rgba(236,253,245,0.98),
            rgba(239,246,255,0.98)
        );
        border: 1px solid #dbeafe;
        box-shadow: 0 10px 35px rgba(15,23,42,0.06);
        margin-bottom: 20px;
    }

    .bidcart-brand {
        font-size: 1.15rem;
        font-weight: 900;
        color: #0f766e;
    }

    .bidcart-tag {
        display: inline-block;
        margin-top: 7px;
        padding: 5px 10px;
        border-radius: 999px;
        background: #ccfbf1;
        color: #115e59;
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.8px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# BRAND
# ---------------------------------------------------------
if st.session_state.screen == "search":
    st.markdown(
        """
<div class="bidcart-hero">
<div class="bidcart-brand">🛒 BidCart</div>
<div class="bidcart-tag">AGENTIC COMMERCE INTELLIGENCE</div>
<h1>Shop smarter. Pay smarter.</h1>
<p style="font-size:1.08rem;color:#475569;">Compare products, validated market prices, customer evidence and payment economics before you buy.</p>
</div>

<div class="category-strip">
<div class="category-tile grocery-tile">🥬 Groceries</div>
<div class="category-tile electronics-tile">🎧 Electronics</div>
<div class="category-tile women-tile">👗 Women's Fashion</div>
<div class="category-tile men-tile">👕 Men's Fashion</div>
<div class="category-tile sports-tile">🏏 Sports & Fitness</div>
<div class="category-tile footwear-tile">👟 Footwear</div>
<div class="category-tile home-tile">🏠 Home & Kitchen</div>
<div class="category-tile beauty-tile">💄 Beauty & Personal Care</div>
</div>
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
        placeholder="e.g. Surf Excel Matic 2 kg, Nike running shoes, Sony headphones...",
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
            )

        with max_budget_col:
            max_budget = st.number_input(
                "Maximum",
                min_value=0,
                step=100,
            )

    with retailer_col:
        st.markdown("**Retailers BidCart will evaluate**")
        retailers = get_retailers(category)

        retailer_styles = {
            "Amazon": ("🟠", "#fff7ed", "#9a3412"),
            "Flipkart": ("🟡", "#eff6ff", "#1d4ed8"),
            "Croma": ("🟢", "#ecfdf5", "#047857"),
            "Reliance Digital": ("🔵", "#eff6ff", "#1e40af"),
            "Myntra": ("🩷", "#fdf2f8", "#be185d"),
            "AJIO": ("⚫", "#f8fafc", "#111827"),
            "Blinkit": ("🟡", "#fefce8", "#854d0e"),
            "Zepto": ("🟣", "#faf5ff", "#7e22ce"),
            "Swiggy Instamart": ("🟠", "#fff7ed", "#c2410c"),
            "BigBasket": ("🟢", "#f0fdf4", "#15803b"),
        }

        retailer_badges = ""
        for retailer in retailers:
            icon, bg, colour = retailer_styles.get(
                retailer,
                ("🛍️", "#f8fafc", "#334155"),
            )
            retailer_badges += (
                f'<span class="retailer-badge" '
                f'style="background:{bg}; color:{colour};">'
                f'{icon} {retailer}</span>'
            )

        st.markdown(
            f'<div class="retailer-row">{retailer_badges}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    search = st.button(
        "Find the Best Deal →",
        type="primary",
        use_container_width=True,
    )

    if search:
        if not product.strip():
            st.error("Enter the product you want BidCart to evaluate.")
        elif not city.strip():
            st.error("Enter your delivery city.")
        elif max_budget > 0 and min_budget > max_budget:
            st.error("Minimum budget cannot be higher than maximum budget.")
        else:
            st.session_state.search_product = product.strip()
            st.session_state.search_city = city.strip()
            st.session_state.search_min_budget = min_budget
            st.session_state.search_max_budget = max_budget
            st.session_state.search_retailers = retailers
            st.session_state.screen = "results"
            st.rerun()

    st.divider()

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


