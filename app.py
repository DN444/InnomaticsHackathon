import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import numpy as np

st.set_page_config(page_title="Food Delivery Dashboard", layout="wide")

@st.cache_data
def load_raw():
    df = pd.read_csv("final_food_delivery_dataset.csv")
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df["order_date"] = pd.to_datetime(df["order_date"], format="%d-%m-%Y", errors="coerce")
    for c in ["city", "membership", "cuisine", "restaurant_name", "name"]:
        if c in df.columns:
            df[c] = df[c].astype("string")
    return df

@st.cache_data
def load_artifacts():
    return joblib.load("dashboard_artifacts.joblib")

df = load_raw()
art = load_artifacts()

st.title("Food Delivery Analytics Dashboard")

# SAFE metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Orders", f"{len(df):,}")
c2.metric("Users", f"{df['user_id'].nunique():,}")
c3.metric("Revenue", f"Rs{df['total_amount'].sum():,.0f}")
c4.metric("Avg Order", f"Rs{df['total_amount'].mean():.0f}")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "City", "Cuisine", "Analysis"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(df, x="total_amount", nbins=30, title="Order Value")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.box(df, x="membership", y="total_amount", title="AOV by Membership")
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("City Revenue")
    # FIXED: Create city data properly for plotly
    city_data = df.groupby("city")["total_amount"].sum().sort_values(ascending=False).reset_index()
    city_data.columns = ['city_name', 'revenue']

    st.dataframe(city_data.head(10))

    # FIXED: Use correct column names
    fig = px.bar(city_data.head(10), x="revenue", y="city_name", orientation="h", 
                title="Top Cities by Revenue")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Cuisine Revenue") 
    # FIXED: Create cuisine data properly
    cuisine_data = df.groupby("cuisine")["total_amount"].sum().sort_values(ascending=False).reset_index()
    cuisine_data.columns = ['cuisine_name', 'revenue']

    st.dataframe(cuisine_data.head(10))

    fig = px.bar(cuisine_data.head(10), x="revenue", y="cuisine_name", orientation="h",
                title="Top Cuisines by Revenue")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Original IPYNB Analysis")

    if "specific_rest_df" in art:
        st.subheader("Specific Restaurants Analysis")
        st.dataframe(art["specific_rest_df"])

    if "combo_df" in art and len(art["combo_df"]) > 0:
        st.subheader("Membership + Cuisine Combinations")
        st.dataframe(art["combo_df"])
        winner = art["combo_df"].iloc[0]
        st.success(f"WINNER: {winner['Membership']} + {winner['Cuisine']} (Rs{winner['Revenue']:,})")

    if "new_q" in art:
        new_q = art["new_q"]
        col1, col2 = st.columns(2)
        col1.metric("Gold Orders", f"{new_q.get('gold_orders', 0):,}")
        col2.metric("High Rating Orders", f"{new_q.get('rating_ge45', 0):,}")

st.markdown("---")
st.caption("Complete EDA + Original IPYNB Analysis - All Errors Fixed")
