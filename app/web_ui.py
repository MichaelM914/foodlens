import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from food_lens.agent import analyze_restaurant_allergens


# ✅ Set page config FIRST
st.set_page_config(page_title="FoodLens", layout="centered")

# Load custom CSS
with open("app/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Logo and Header ---
st.image("app/assets/logo.png", width=120)  # MWM logo goes here
st.title("FoodLens")
st.markdown("Allergen-Safe Menu Finder for Restaurants")
st.markdown("Enter a restaurant and allergen to find safe foods from official allergen guides.")

st.divider()

# --- Input form layout ---
col1, col2 = st.columns([2, 1])
with col1:
    restaurant = st.text_input("Restaurant name", placeholder="e.g. Panera, Chick-fil-A, McDonald's")
with col2:
    allergen = st.selectbox("Allergen to avoid", [
        "dairy", "egg", "peanuts", "tree nuts", "soy", "wheat", "fish", "shellfish", "sesame"
    ])

# --- Analyze on click ---
if st.button("Find Safe Menu Items"):
    if not restaurant:
        st.warning("Please enter a restaurant name.")
    else:
        with st.spinner("Analyzing allergen data..."):
            result = analyze_restaurant_allergens(restaurant.strip(), allergen.lower())

        st.divider()

        # --- Results display ---
        with st.container():
            if result is None:
                st.error("No results found or analysis failed. Please try another restaurant.")
            else:
                full_items, sub_items = result

                st.subheader("Safe Main Menu Items")
                if full_items:
                    for item in full_items:
                        st.markdown(f"- {item}")
                else:
                    st.markdown("_None found._")

                st.subheader("Safe Ingredients / Sides")
                if sub_items:
                    for item in sub_items:
                        st.markdown(f"- {item}")
                else:
                    st.markdown("_None found._")

# --- Footer ---
st.divider()
st.caption("Built with care for people with food allergies. Always verify with restaurant staff.")
