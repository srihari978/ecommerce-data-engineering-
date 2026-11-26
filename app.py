
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛒",
    layout="wide"
)

# Load CSV data
@st.cache_data
def load_data():
    return pd.read_csv("fact_orders_enriched.csv")

df = load_data()

st.title("🛒 E-Commerce Sales Analytics")
st.caption("End-to-End Data Engineering Project | Databricks Gold Layer")

# Market filter
markets = st.multiselect(
    "Select Market",
    df["market"].dropna().unique(),
    default=list(df["market"].dropna().unique())
)

filtered_df = df[df["market"].isin(markets)]

# KPIs
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Sales",
    f"₹{filtered_df['total_amount_inr'].sum():,.0f}"
)

col2.metric(
    "Quantity Sold",
    f"{filtered_df['sold_quantity'].sum():,.0f}"
)

col3.metric(
    "Customers",
    filtered_df["customer_code"].nunique()
)

col4.metric(
    "Products",
    filtered_df["product_code"].nunique()
)

st.divider()

# Monthly sales
st.subheader("Monthly Sales Trend")

monthly = filtered_df.groupby("month_name")["total_amount_inr"].sum()
st.bar_chart(monthly)

# Category and market analysis
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales by Category")
    category = filtered_df.groupby("category")["total_amount_inr"].sum()
    st.bar_chart(category)

with col2:
    st.subheader("Sales by Market")
    market = filtered_df.groupby("market")["total_amount_inr"].sum()
    st.bar_chart(market)

# Data preview
st.subheader("Gold Layer Data Preview")
st.dataframe(filtered_df.head(100), use_container_width=True)

st.caption(f"Total records: {len(filtered_df):,}")
