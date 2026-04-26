
import streamlit as st
import pandas as pd
import json

# Load Credit Card Data from JSON
try:
    with open('cards_db.json', 'r') as f:
        cards_data_list = json.load(f)
    cards_data = {card['name']: card for card in cards_data_list}
except FileNotFoundError:
    st.error("cards_db.json not found. Please ensure the file is in the same directory as app.py")
    st.stop()
except json.JSONDecodeError:
    st.error("Error decoding cards_db.json. Please check the JSON format.")
    st.stop()

# Custom CSS for a sleek, modern fintech look
custom_css = """
<style>
    /* Hide Streamlit header and footer */
    .stApp > header {visibility: hidden;}
    .stApp > footer {visibility: hidden;}

    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }

    /* Card-like containers for sections */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    .stTabs {
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    .stTabs > div:first-child {
        border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] {
        margin: 0 0.5rem;
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Segoe UI', sans-serif;
        color: #333;
    }
    p, div, label {
        font-family: 'Roboto', sans-serif;
    }

    /* Metric component styling */
    [data-testid="stMetric"] {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 0.0625rem 0.125rem rgba(0, 0, 0, 0.05);
    }
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #555;
    }
    [data-testid="stMetricDelta"] {
        font-size: 1.2rem;
    }

    /* Input field styling */
    .st-dg, .st-ck, .st-at, .st-bd {
        border-radius: 0.25rem;
        border: 1px solid #ccc;
    }

    /* Button styling */
    .stButton > button {
        background-color: #007bff;
        color: white;
        border-radius: 0.25rem;
        border: none;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }

</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Streamlit App Title
st.set_page_config(layout="wide")
st.title("Credit Card Reward Optimizer")

# Create Tabs
tab1, tab2, tab3 = st.tabs(["Single Purchase Optimizer", "Card Comparison Matrix", "Smart Wallet Routing"])

with tab1:
    st.header("Single Purchase Optimizer")

    # User Inputs
    owned_cards = st.multiselect(
        "Select your owned credit cards:",
        options=list(cards_data.keys()),
        default=[]
    )

    all_categories = sorted(list(set(cat for card in cards_data.values() for cat in card["accelerated_categories"].keys())))
    spend_categories_options = all_categories + ["General"]

    col1, col2 = st.columns(2)
    with col1:
        spend_category = st.selectbox(
            "Select Spend Category:",
            options=spend_categories_options
        )
    with col2:
        amount = st.number_input("Enter Amount Spent:", min_value=0.01, format="%.2f")

    if st.button("Optimize Purchase") and owned_cards:
        best_card = None
        max_rewards = -1

        for card_name in owned_cards:
            card = cards_data[card_name]
            cashback_rate = card["base_reward_rate"]

            # Check for accelerated categories
            if spend_category in card["accelerated_categories"]:
                cashback_rate = card["accelerated_categories"][spend_category]

            rewards = amount * cashback_rate

            if rewards > max_rewards:
                max_rewards = rewards
                best_card = card_name

        if best_card:
            st.subheader(f"Highest Yielding Card for ${amount:.2f} spend in {spend_category}:")
            st.metric(
                label=f"Best Card: {best_card}",
                value=f"${max_rewards:.2f}"
            )
            st.success("Use this card to maximize your rewards!")
        else:
            st.warning("Please select at least one owned card.")

with tab2:
    st.header("Card Comparison Matrix")

    # Prepare data for DataFrame
    comparison_data = []
    for card_name, card_info in cards_data.items():
        accelerated_cats = ", ".join([f"{cat} ({rate:.1%})" for cat, rate in card_info["accelerated_categories"].items()])
        milestone_benefits = [f"Spend {b['spend']:,}: {b['benefit']}" for b in card_info["milestone_benefits"]]

        comparison_data.append({
            "Card": card_name,
            "Annual Fee": f"${card_info['annual_fee']:.2f}",
            "Fee Waived On Spend": f"${card_info['fee_waived_on_spend']:,}" if card_info['fee_waived_on_spend'] > 0 else "N/A",
            "Base Reward Rate": f"{card_info['base_reward_rate']:.1%}",
            "Accelerated Categories": accelerated_cats if accelerated_cats else "N/A",
            "Milestone Benefits": "; ".join(milestone_benefits) if milestone_benefits else "N/A",
            "Key Benefits": ", ".join(card_info["key_benefits"])
        })

    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, hide_index=True, use_container_width=True)

with tab3:
    st.header("Smart Wallet Routing")

    st.write("Enter your estimated monthly spend in different categories to get an optimized wallet strategy.")

    # Dynamically get all unique categories including 'General'
    all_categories_wallet = sorted(list(set(cat for card in cards_data.values() for cat in card["accelerated_categories"].keys())))
    if "General" not in all_categories_wallet:
        all_categories_wallet.append("General")

    # Monthly Spend Profile Inputs
    monthly_spend = {}

    # Use columns for monthly spend inputs
    cols_spend = st.columns(len(all_categories_wallet))
    for i, category in enumerate(all_categories_wallet):
        with cols_spend[i]:
            monthly_spend[category] = st.number_input(f"Monthly Spend in {category}:", min_value=0.0, format="%.2f", key=f"monthly_{category}")

    # User Owned Cards for Wallet Routing
    owned_cards_wallet = st.multiselect(
        "Select your owned credit cards for wallet routing:",
        options=list(cards_data.keys()),
        default=[],
        key="owned_cards_wallet"
    )

    if st.button("Generate Optimized Strategy", key="generate_strategy") and owned_cards_wallet:
        if not any(monthly_spend.values()):
            st.warning("Please enter some monthly spend values to generate a strategy.")
        else:
            optimized_strategy = {}
            total_monthly_rewards = 0
            total_annual_fees = 0

            # Calculate annual fees for owned cards
            for card_name in owned_cards_wallet:
                total_annual_fees += cards_data[card_name]["annual_fee"]

            for category in all_categories_wallet:
                if monthly_spend.get(category, 0) > 0:
                    best_card_for_category = None
                    max_rewards_for_category = -1

                    for card_name in owned_cards_wallet:
                        card = cards_data[card_name]
                        cashback_rate = card["base_reward_rate"]

                        if category in card["accelerated_categories"]:
                            cashback_rate = card["accelerated_categories"][category]
                        elif category == "General": # Fallback to base rate for 'General' category
                            cashback_rate = card["base_reward_rate"]
                        else:
                            continue # Skip categories not explicitly covered or not 'General'

                        rewards = monthly_spend[category] * cashback_rate

                        if rewards > max_rewards_for_category:
                            max_rewards_for_category = rewards
                            best_card_for_category = card_name

                    if best_card_for_category:
                        optimized_strategy[category] = {
                            "card": best_card_for_category,
                            "monthly_rewards": max_rewards_for_category
                        }
                        total_monthly_rewards += max_rewards_for_category

            st.subheader("Optimized Wallet Strategy:")
            if optimized_strategy:
                for category, details in optimized_strategy.items():
                    st.write(f"- For **{category}**, use **{details['card']}** to earn **${details['monthly_rewards']:.2f}** in rewards.")

                total_annual_rewards = total_monthly_rewards * 12
                net_annual_value = total_annual_rewards - total_annual_fees

                st.subheader("Projected Annual Value:")
                col_metrics_1, col_metrics_2, col_metrics_3 = st.columns(3)
                with col_metrics_1:
                    st.metric(label="Projected Total Monthly Rewards", value=f"${total_monthly_rewards:.2f}")
                with col_metrics_2:
                    st.metric(label="Projected Total Annual Rewards", value=f"${total_annual_rewards:.2f}")
                with col_metrics_3:
                    st.metric(label="Total Annual Fees for Owned Cards", value=f"-${total_annual_fees:.2f}", delta_color="inverse")

                st.metric(label="Net Annual Value (Rewards - Fees)", value=f"${net_annual_value:.2f}")
            else:
                st.warning("No optimized strategy could be generated based on your inputs. Please check your monthly spend and owned cards.")