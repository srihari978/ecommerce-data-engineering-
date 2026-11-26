
# import streamlit as st
# import pandas as pd

# st.set_page_config(
#     page_title="E-Commerce Analytics",
#     page_icon="🛒",
#     layout="wide"
# )

# # Load CSV data
# @st.cache_data
# def load_data():
#     return pd.read_csv("fact_orders_enriched.csv")

# df = load_data()

# st.title("🛒 E-Commerce Sales Analytics")
# st.caption("End-to-End Data Engineering Project | Databricks Gold Layer")

# # Market filter
# markets = st.multiselect(
#     "Select Market",
#     df["market"].dropna().unique(),
#     default=list(df["market"].dropna().unique())
# )

# filtered_df = df[df["market"].isin(markets)]

# # KPIs
# col1, col2, col3, col4 = st.columns(4)

# col1.metric(
#     "Total Sales",
#     f"₹{filtered_df['total_amount_inr'].sum():,.0f}"
# )

# col2.metric(
#     "Quantity Sold",
#     f"{filtered_df['sold_quantity'].sum():,.0f}"
# )

# col3.metric(
#     "Customers",
#     filtered_df["customer_code"].nunique()
# )

# col4.metric(
#     "Products",
#     filtered_df["product_code"].nunique()
# )

# st.divider()

# # Monthly sales
# st.subheader("Monthly Sales Trend")

# monthly = filtered_df.groupby("month_name")["total_amount_inr"].sum()
# st.bar_chart(monthly)

# # Category and market analysis
# col1, col2 = st.columns(2)

# with col1:
#     st.subheader("Sales by Category")
#     category = filtered_df.groupby("category")["total_amount_inr"].sum()
#     st.bar_chart(category)

# with col2:
#     st.subheader("Sales by Market")
#     market = filtered_df.groupby("market")["total_amount_inr"].sum()
#     st.bar_chart(market)

# # Data preview
# st.subheader("Gold Layer Data Preview")
# st.dataframe(filtered_df.head(100), use_container_width=True)

# st.caption(f"Total records: {len(filtered_df):,}")

import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>
.stApp {
    background-color: #0B1120;
    color: #F8FAFC;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

h1, h2, h3 {
    color: #F8FAFC !important;
}

.metric-card {
    background: linear-gradient(135deg, #172554, #1E293B);
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #334155;
    margin-bottom: 10px;
}

.metric-title {
    color: #94A3B8;
    font-size: 14px;
    font-weight: 600;
}

.metric-value {
    color: #FFFFFF;
    font-size: 27px;
    font-weight: 800;
    margin-top: 8px;
}

.metric-subtitle {
    color: #38BDF8;
    font-size: 12px;
    margin-top: 5px;
}

div[data-testid="stPlotlyChart"] {
    background-color: #111827;
    border-radius: 15px;
    padding: 8px;
}

div[data-testid="stDataFrame"] {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    df = pd.read_csv("fact_orders_enriched.csv")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    df["sold_quantity"] = pd.to_numeric(
        df["sold_quantity"], errors="coerce"
    ).fillna(0)

    df["price_inr"] = pd.to_numeric(
        df["price_inr"], errors="coerce"
    ).fillna(0)

    df["total_amount_inr"] = pd.to_numeric(
        df["total_amount_inr"], errors="coerce"
    ).fillna(0)

    return df


df = load_data()

# =========================================================
# HEADER
# =========================================================

st.markdown("""
# 🛒 E-Commerce Sales Intelligence

### Business Analytics Dashboard
""")

st.markdown(
    "Analyze revenue, customers, products, markets and sales performance."
)

st.divider()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title("🎛️ Dashboard Filters")

years = sorted(df["year"].dropna().unique().tolist())

selected_years = st.sidebar.multiselect(
    "Year",
    years,
    default=years
)

markets = sorted(df["market"].dropna().unique())

selected_markets = st.sidebar.multiselect(
    "Market",
    markets,
    default=markets
)

divisions = sorted(df["division"].dropna().unique())

selected_divisions = st.sidebar.multiselect(
    "Division",
    divisions,
    default=divisions
)

categories = sorted(df["category"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "Category",
    categories,
    default=categories
)

channels = sorted(df["channel"].dropna().unique())

selected_channels = st.sidebar.multiselect(
    "Channel",
    channels,
    default=channels
)

platforms = sorted(df["platform"].dropna().unique())

selected_platforms = st.sidebar.multiselect(
    "Platform",
    platforms,
    default=platforms
)

# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df[
    (df["year"].isin(selected_years)) &
    (df["market"].isin(selected_markets)) &
    (df["division"].isin(selected_divisions)) &
    (df["category"].isin(selected_categories)) &
    (df["channel"].isin(selected_channels)) &
    (df["platform"].isin(selected_platforms))
].copy()

# =========================================================
# KPI METRICS
# =========================================================

total_sales = filtered_df["total_amount_inr"].sum()

total_quantity = filtered_df["sold_quantity"].sum()

total_customers = filtered_df["customer_code"].nunique()

total_products = filtered_df["product_code"].nunique()

total_markets = filtered_df["market"].nunique()

average_price = (
    filtered_df["price_inr"].mean()
    if not filtered_df.empty else 0
)

sales_records = len(filtered_df)

# =========================================================
# KPI CARDS
# =========================================================

st.subheader("📊 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">💰 TOTAL REVENUE</div>
        <div class="metric-value">₹{total_sales:,.0f}</div>
        <div class="metric-subtitle">Sales revenue</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">📦 QUANTITY SOLD</div>
        <div class="metric-value">{total_quantity:,.0f}</div>
        <div class="metric-subtitle">Units sold</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">👥 CUSTOMERS</div>
        <div class="metric-value">{total_customers:,}</div>
        <div class="metric-subtitle">Unique customers</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">🏷️ PRODUCTS</div>
        <div class="metric-value">{total_products:,}</div>
        <div class="metric-subtitle">Unique products</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Sales Records", f"{sales_records:,}")

col2.metric("Markets", f"{total_markets:,}")

col3.metric("Average Unit Price", f"₹{average_price:,.2f}")

col4.metric("Revenue per Record", 
            f"₹{total_sales/sales_records:,.2f}" 
            if sales_records > 0 else "₹0")

st.divider()

# =========================================================
# MONTHLY SALES TREND
# =========================================================

st.subheader("📈 Revenue Trend")

if not filtered_df.empty:

    monthly_sales = (
        filtered_df.groupby("date")["total_amount_inr"]
        .sum()
        .reset_index()
        .sort_values("date")
    )

    fig = px.area(
        monthly_sales,
        x="date",
        y="total_amount_inr",
        title="Revenue Over Time",
        markers=True
    )

    fig.update_traces(
        line_color="#38BDF8",
        fillcolor="rgba(56,189,248,0.20)"
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font_color="#F8FAFC",
        height=420,
        xaxis_title="Date",
        yaxis_title="Revenue (INR)",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# MARKET & CATEGORY ANALYSIS
# =========================================================

st.subheader("🌍 Market & Product Analysis")

col1, col2 = st.columns(2)

with col1:

    market_sales = (
        filtered_df.groupby("market")["total_amount_inr"]
        .sum()
        .reset_index()
        .sort_values("total_amount_inr", ascending=False)
    )

    fig = px.bar(
        market_sales,
        x="market",
        y="total_amount_inr",
        color="market",
        title="Revenue by Market",
        text_auto=".2s",
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        showlegend=False,
        height=400,
        yaxis_title="Revenue (INR)"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    category_sales = (
        filtered_df.groupby("category")["total_amount_inr"]
        .sum()
        .reset_index()
        .sort_values("total_amount_inr", ascending=False)
    )

    fig = px.pie(
        category_sales,
        names="category",
        values="total_amount_inr",
        title="Revenue Share by Category",
        hole=0.55,
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111827",
        font_color="#F8FAFC",
        height=420
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent"
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# DIVISION ANALYSIS
# =========================================================

st.subheader("🏆 Division Performance")

division_sales = (
    filtered_df.groupby("division")["total_amount_inr"]
    .sum()
    .reset_index()
    .sort_values("total_amount_inr", ascending=True)
)

fig = px.bar(
    division_sales,
    x="total_amount_inr",
    y="division",
    orientation="h",
    color="total_amount_inr",
    title="Revenue by Division",
    color_continuous_scale="Viridis"
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    height=500,
    coloraxis_showscale=False,
    xaxis_title="Revenue (INR)",
    yaxis_title=""
)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# CHANNEL & PLATFORM ANALYSIS
# =========================================================

st.subheader("🛍️ Sales Channel Analysis")

col1, col2 = st.columns(2)

with col1:

    channel_sales = (
        filtered_df.groupby("channel")["total_amount_inr"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        channel_sales,
        names="channel",
        values="total_amount_inr",
        title="Revenue by Channel",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111827",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:

    platform_sales = (
        filtered_df.groupby("platform")["total_amount_inr"]
        .sum()
        .reset_index()
        .sort_values("total_amount_inr", ascending=False)
    )

    fig = px.bar(
        platform_sales,
        x="platform",
        y="total_amount_inr",
        color="platform",
        title="Revenue by Platform",
        color_discrete_sequence=px.colors.qualitative.Safe
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        showlegend=False,
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# TOP PRODUCTS
# =========================================================

st.subheader("🔥 Top 10 Products")

top_products = (
    filtered_df.groupby("product")["total_amount_inr"]
    .sum()
    .reset_index()
    .sort_values("total_amount_inr", ascending=False)
    .head(10)
)

fig = px.bar(
    top_products.sort_values("total_amount_inr"),
    x="total_amount_inr",
    y="product",
    orientation="h",
    color="total_amount_inr",
    color_continuous_scale="Plasma",
    title="Top Products by Revenue"
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    height=500,
    coloraxis_showscale=False
)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# TOP CUSTOMERS
# =========================================================

st.subheader("💎 Top 10 Customers")

top_customers = (
    filtered_df.groupby("customer")["total_amount_inr"]
    .sum()
    .reset_index()
    .sort_values("total_amount_inr", ascending=False)
    .head(10)
)

fig = px.bar(
    top_customers.sort_values("total_amount_inr"),
    x="total_amount_inr",
    y="customer",
    orientation="h",
    color="total_amount_inr",
    color_continuous_scale="Blues",
    title="Top Customers by Revenue"
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    height=500,
    coloraxis_showscale=False
)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# QUARTER ANALYSIS
# =========================================================

st.subheader("📅 Quarterly Sales")

quarter_sales = (
    filtered_df.groupby("year_quarter")["total_amount_inr"]
    .sum()
    .reset_index()
    .sort_values("year_quarter")
)

fig = px.bar(
    quarter_sales,
    x="year_quarter",
    y="total_amount_inr",
    color="year_quarter",
    title="Revenue by Quarter",
    color_discrete_sequence=px.colors.qualitative.Vivid
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    showlegend=False,
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# QUANTITY ANALYSIS
# =========================================================

st.subheader("📦 Quantity Sold by Category")

quantity_category = (
    filtered_df.groupby("category")["sold_quantity"]
    .sum()
    .reset_index()
    .sort_values("sold_quantity", ascending=False)
)

fig = px.bar(
    quantity_category,
    x="category",
    y="sold_quantity",
    color="sold_quantity",
    title="Category-wise Quantity",
    color_continuous_scale="Teal"
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#111827",
    plot_bgcolor="#111827",
    height=450,
    coloraxis_showscale=False
)

st.plotly_chart(fig, use_container_width=True)

# =========================================================
# DETAILED DATA
# =========================================================

st.subheader("📋 Detailed Sales Data")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=400
)

# =========================================================
# DOWNLOAD FILTERED DATA
# =========================================================

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name="filtered_ecommerce_sales.csv",
    mime="text/csv"
)

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown("""
<div style="text-align:center; color:#94A3B8;">

<strong>E-Commerce Data Engineering Project</strong><br>

Built with Python • Streamlit • Pandas • Plotly • Databricks

</div>
""", unsafe_allow_html=True)

