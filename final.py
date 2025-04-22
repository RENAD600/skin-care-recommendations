import streamlit as st 
import pandas as pd
import random

# 🌸 Pink themed soft design with background gradient + updated input styles
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital@1&display=swap');

    .stApp {
        font-family: 'Playfair Display', serif;
        background-color: #fff0f5 !important;
        background-image: linear-gradient(to bottom right, #fff0f5, #ffe6f0);
        background-attachment: fixed;
        background-size: cover;
        color: #a34c84;
    }

    h1, h2, h3 {
        color: #d36ba6;
        font-style: italic;
    }

    .stButton>button {
        background-color: #e754a6;
        color: white;
        font-style: italic;
        font-weight: bold;
        border-radius: 30px;
        padding: 10px 25px;
    }

    .stButton>button:hover {
        background-color: #c7448c;
        color: white;
    }

    .stSelectbox, .stSlider, .stRadio, input[type="text"] {
        background-color: #fcd8e8 !important;
        border-radius: 12px;
        padding: 10px;
        border: none;
    }

    .stDataFrame {
        background-color: white;
        border-radius: 20px;
    }

    .topnav {
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: #fcd8e8;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 30px;
    }

    .topnav a {
        display: inline-block;
        color: #a34c84;
        padding: 10px 24px;
        margin: 0px 8px;
        text-decoration: none;
        font-size: 17px;
        font-weight: bold;
        border-radius: 30px;
        transition: background-color 0.3s ease, color 0.3s ease;
        background-color: #f8d0e0;
    }

    .topnav a:hover {
        background-color: #f3b6d0;
        color: white;
    }

    .topnav a.active {
        background-color: #d36ba6;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# 💄 Logo and title with beige color
st.markdown("""
<h1 style='text-align: center; font-style: italic; font-family: "Playfair Display", serif; color: #c2a179;'>
    Find Your Perfect Beauty
</h1>
""", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center; color: #c2a179;'>Share your skin type we’ll take care of the rest.</h3>", unsafe_allow_html=True)
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("cosmetics.csv")

df = load_data()

def rank_to_stars(rank):
    full_stars = int(round(rank))
    return "⭐" * full_stars + "☆" * (5 - full_stars)

def get_unique_ingredients(df, n=3):
    all_ingredients = df['Ingredients'].dropna().str.lower().str.split(',').explode().str.strip().unique()
    return random.sample(list(all_ingredients), min(n, len(all_ingredients)))

# Navigation bar
nav_param = st.query_params.get("nav", "Skin Type Based Recommendation")
if nav_param in ["Skin Type Based Recommendation", "Ingredient Based Recommendation"]:
    st.session_state["nav"] = nav_param
else:
    st.session_state["nav"] = "Skin Type Based Recommendation"

st.markdown(f"""
<div class="topnav">
    <a href="?nav=Skin Type Based Recommendation" class="{'active' if st.session_state['nav'] == 'Skin Type Based Recommendation' else ''}">Skin Type Recommendation</a>
    <a href="?nav=Ingredient Based Recommendation" class="{'active' if st.session_state['nav'] == 'Ingredient Based Recommendation' else ''}">Ingredient Recommendation</a>
</div>
""", unsafe_allow_html=True)

choice = st.session_state["nav"]

# Skin Type Based Recommendation
if choice == "Skin Type Based Recommendation":
    st.markdown("### ✨Discover What Suits Your Skin Best")

    skin_columns = ["Oily", "Dry", "Normal", "Combination", "Sensitive"]
    selected_skin = st.selectbox("Select your skin type:", skin_columns)

    price_min, price_max = st.slider("🎯 Select price range:", 
                                     min_value=float(df['Price'].min()), 
                                     max_value=float(df['Price'].max()), 
                                     value=(float(df['Price'].min()), float(df['Price'].max())))

    rank_min, rank_max = st.slider("⭐ Select rating range:", 
                                   min_value=1, max_value=5, value=(1, 5))

    sort_order = st.radio("Sort order:", ["Ascending", "Descending"], key="order_skin")

    if st.button("Show suitable products for my skin"):
        skin_filtered = df[
            (df[selected_skin] == 1) & 
            (df["Price"] >= price_min) & (df["Price"] <= price_max) &
            (df["Rank"] >= rank_min) & (df["Rank"] <= rank_max)
        ]

        if not skin_filtered.empty:
            ascending = True if sort_order == "Ascending" else False
            sorted_df = skin_filtered.sort_values(by=["Price", "Rank"], ascending=ascending).copy()
            sorted_df["Rank (Stars)"] = sorted_df["Rank"].apply(rank_to_stars)

            st.success("✨ Suitable products for you:")
            for _, row in sorted_df.iterrows():
                with st.expander(f"{row['Brand']} - {row['Name']}"):
                    st.write(f"💰 Price: {row['Price']} SAR")
                    st.write(f"⭐ Rating: {row['Rank (Stars)']}")
        else:
            st.warning("❌ No products available within the selected range.")

# Ingredient Based Recommendation
elif choice == "Ingredient Based Recommendation":
    st.markdown("### 🧪 Tailored Picks from Ingredients You Love ")

    user_input = st.text_input("🧬 Enter ingredients separated by commas (e.g. hyaluronic acid, niacinamide):")

    price_min_sim, price_max_sim = st.slider("🎯 Select price range:", 
                                         min_value=float(df['Price'].min()), 
                                         max_value=float(df['Price'].max()), 
                                         value=(float(df['Price'].min()), float(df['Price'].max())), key="price_sim")

    rank_min_sim, rank_max_sim = st.slider("⭐ Select rating range:", 
                                       min_value=1, max_value=5, value=(1, 5), key="rank_sim")

    sort_order_similar = st.radio("Sort order:", ["Ascending", "Descending"], key="order_similar")

    if st.button("Find matching products"):
        if user_input.strip() == "":
            st.warning("⚠ Please enter at least one ingredient.")
        else:
            ingredients = [i.strip().lower() for i in user_input.split(",") if i.strip()]
            ingredient_matches = df["Ingredients"].fillna("").str.lower().apply(
                lambda ing: any(ingredient in ing for ingredient in ingredients)
            )

            if not ingredient_matches.any():
                suggestions = get_unique_ingredients(df, n=3)
                st.error(f"❌ Sorry, this ingredient is not available. Choose another ingredient, such as {suggestions[0]}, **{suggestions[1]}, or **{suggestions[2]}.")
            else:
                filtered_df = df[ingredient_matches].copy()
                filtered_df = filtered_df[
                    (filtered_df["Price"] >= price_min_sim) & (filtered_df["Price"] <= price_max_sim) &
                    (filtered_df["Rank"] >= rank_min_sim) & (filtered_df["Rank"] <= rank_max_sim)
                ]

                if not filtered_df.empty:
                    ascending = True if sort_order_similar == "Ascending" else False
                    sorted_filtered = filtered_df.sort_values(by=["Price", "Rank"], ascending=ascending).copy()
                    sorted_filtered["Rank (Stars)"] = sorted_filtered["Rank"].apply(rank_to_stars)

                    st.success("🔍 Products containing one or more of your ingredients:")
                    for _, row in sorted_filtered.iterrows():
                        with st.expander(f"{row['Brand']} - {row['Name']}"):
                            st.write(f"💰 Price: {row['Price']} SAR")
                            st.write(f"⭐ Rating: {row['Rank (Stars)']}")
                else:
                    st.error("😔 No products found within the selected filters.")