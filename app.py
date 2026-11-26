import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="E-Commerce BI Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- THEME --------------------
BG = "#0B1220"
PANEL = "#111C2E"
TEXT = "#E5E7EB"
MUTED = "#94A3B8"
PALETTE = ["#38BDF8", "#A78BFA", "#34D399", "#FBBF24",
           "#FB7185", "#2DD4BF", "#818CF8", "#F97316"]

st.markdown("""
<style>
.stApp { background: #0B1220; color: #E5E7EB; }
[data-testid="stSidebar"] { background: #111827; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
h1, h2, h3 { color: #F8FAFC !important; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg,#172554,#172033);
    border: 1px solid #26364D; padding: 16px; border-radius: 14px;
}
[data-testid="stMetricLabel"] { color: #CBD5E1 !important; }
[data-testid="stMetricValue"] { color: #FFFFFF !important; }
div[data-testid="stPlotlyChart"] {
    background: #111C2E; border: 1px solid #26364D;
    border-radius: 14px; padding: 8px;
}
</style>
""", unsafe_allow_html=True)

# -------------------- DATA --------------------
@st.cache_data
def load_data():
    data = pd.read_csv("fact_orders_enriched.csv")
    required = [
        "date", "year", "quarter", "year_quarter", "month_name",
        "customer_code", "customer", "market", "platform", "channel",
        "division", "category", "product", "variant",
        "sold_quantity", "price_inr", "total_amount_inr"
    ]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")

    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    for col in ["year", "sold_quantity", "price_inr", "total_amount_inr"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.dropna(subset=["date"])
    data["year"] = data["year"].fillna(data["date"].dt.year).astype(int)
    data["month_number"] = data["date"].dt.month
    data["month_label"] = data["date"].dt.strftime("%b")
    data["year_month"] = data["date"].dt.to_period("M").astype(str)
    data["quarter_label"] = data["date"].dt.to_period("Q").astype(str)
    return data

try:
    df = load_data()
except Exception as exc:
    st.error(f"Could not load the dashboard data: {exc}")
    st.stop()

# -------------------- SHARED FILTERS --------------------
st.sidebar.title("🛒 E-Commerce BI")
st.sidebar.caption("Business intelligence dashboard")
page = st.sidebar.radio(
    "Navigate",
    ["Home", "Sales", "Marketing", "Finance", "Supply Chain"]
)
st.sidebar.divider()
st.sidebar.subheader("Global filters")

def options_for(column):
    return sorted(df[column].dropna().unique().tolist(), key=lambda x: str(x))

def multi_filter(label, column):
    values = options_for(column)
    return st.sidebar.multiselect(label, values, default=values)

years = multi_filter("Year", "year")
markets = multi_filter("Market", "market")
channels = multi_filter("Channel", "channel")
platforms = multi_filter("Platform", "platform")
divisions = multi_filter("Division", "division")
categories = multi_filter("Category", "category")

def get_filtered_df():
    result = df[
        df["year"].isin(years)
        & df["market"].isin(markets)
        & df["channel"].isin(channels)
        & df["platform"].isin(platforms)
        & df["division"].isin(divisions)
        & df["category"].isin(categories)
    ].copy()
    return result

data = get_filtered_df()

def money(value):
    return f"₹{value:,.0f}"

def plot_layout(fig, height=390):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=PANEL,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT),
        height=height,
        margin=dict(l=20, r=20, t=65, b=30),
        legend_title_text=""
    )
    return fig

def show_empty():
    st.warning("No records match the selected filters. Change or clear some filters.")

def kpi_row(frame):
    revenue = frame["total_amount_inr"].sum()
    qty = frame["sold_quantity"].sum()
    customers = frame["customer_code"].nunique()
    products = frame["product_code"].nunique() if "product_code" in frame else frame["product"].nunique()
    records = len(frame)
    avg_price = frame["price_inr"].mean() if records else 0
    a, b, c, d = st.columns(4)
    a.metric("Total revenue", money(revenue))
    b.metric("Quantity sold", f"{qty:,.0f}")
    c.metric("Unique customers", f"{customers:,}")
    d.metric("Unique products", f"{products:,}")
    e, f = st.columns(2)
    e.metric("Sales records", f"{records:,}")
    f.metric("Average unit price", money(avg_price) if pd.notna(avg_price) else "₹0")

def monthly_table(frame):
    return (frame.groupby("year_month", as_index=False)
            .agg(revenue=("total_amount_inr", "sum"),
                 quantity=("sold_quantity", "sum"))
            .sort_values("year_month"))

def bar_chart(frame, x, y, title, color=None, horizontal=False, top=None):
    grouped = frame.groupby(x, dropna=False, as_index=False)[y].sum()
    grouped = grouped.sort_values(y, ascending=False)
    if top:
        grouped = grouped.head(top)
    if horizontal:
        grouped = grouped.sort_values(y, ascending=True)
    fig = px.bar(
        grouped, x=y if horizontal else x, y=x if horizontal else y,
        color=color if color else x,
        orientation="h" if horizontal else "v",
        title=title, color_discrete_sequence=PALETTE,
        text_auto=".2s"
    )
    return plot_layout(fig, 430)

# -------------------- HEADER --------------------
st.title("🛒 E-Commerce Business Intelligence")
st.caption("Executive analytics | Source: Databricks Gold view export")
st.caption(f"Showing {len(data):,} of {len(df):,} source records")
st.divider()

if data.empty:
    show_empty()
    st.stop()

# -------------------- HOME --------------------
if page == "Home":
    st.subheader("Executive overview")
    kpi_row(data)

    left, right = st.columns([1.6, 1])
    with left:
        trend = monthly_table(data)
        fig = px.area(trend, x="year_month", y="revenue",
                      markers=True, title="Monthly revenue trend",
                      color_discrete_sequence=[PALETTE[0]])
        fig.update_traces(line_width=3, fillcolor="rgba(56,189,248,0.18)")
        st.plotly_chart(plot_layout(fig, 400), use_container_width=True)
    with right:
        market = data.groupby("market", as_index=False)["total_amount_inr"].sum()
        fig = px.pie(market, names="market", values="total_amount_inr",
                     hole=.58, title="Revenue by market",
                     color_discrete_sequence=PALETTE)
        st.plotly_chart(plot_layout(fig, 400), use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.plotly_chart(bar_chart(data, "category", "total_amount_inr",
                                  "Revenue by category", top=12),
                        use_container_width=True)
    with right:
        st.plotly_chart(bar_chart(data, "channel", "total_amount_inr",
                                  "Revenue by channel"),
                        use_container_width=True)

    st.subheader("Business highlights")
    top_market = data.groupby("market")["total_amount_inr"].sum().idxmax()
    top_category = data.groupby("category")["total_amount_inr"].sum().idxmax()
    st.write(f"- Highest-revenue market in the current selection: **{top_market}**")
    st.write(f"- Highest-revenue category in the current selection: **{top_category}**")

# -------------------- SALES --------------------
elif page == "Sales":
    st.subheader("📈 Sales performance")
    kpi_row(data)

    trend = monthly_table(data)
    fig = px.line(trend, x="year_month", y="revenue", markers=True,
                  title="Revenue by month",
                  color_discrete_sequence=[PALETTE[0]])
    st.plotly_chart(plot_layout(fig, 420), use_container_width=True)

    a, b = st.columns(2)
    with a:
        st.plotly_chart(bar_chart(data, "market", "total_amount_inr",
                                  "Revenue by market"), use_container_width=True)
    with b:
        st.plotly_chart(bar_chart(data, "channel", "total_amount_inr",
                                  "Revenue by channel"), use_container_width=True)

    a, b = st.columns(2)
    with a:
        st.plotly_chart(bar_chart(data, "platform", "total_amount_inr",
                                  "Revenue by platform"), use_container_width=True)
    with b:
        st.plotly_chart(bar_chart(data, "year_quarter", "total_amount_inr",
                                  "Revenue by year-quarter"), use_container_width=True)

    a, b = st.columns(2)
    with a:
        st.plotly_chart(bar_chart(data, "product", "total_amount_inr",
                                  "Top 10 products by revenue", horizontal=True, top=10),
                        use_container_width=True)
    with b:
        st.plotly_chart(bar_chart(data, "customer", "total_amount_inr",
                                  "Top 10 customers by revenue", horizontal=True, top=10),
                        use_container_width=True)

    market_channel = pd.pivot_table(
        data, index="market", columns="channel",
        values="total_amount_inr", aggfunc="sum", fill_value=0
    )
    st.subheader("Market × channel revenue")
    st.dataframe(market_channel.style.format("₹{:,.0f}"), use_container_width=True)

    heat = data.pivot_table(index="market", columns="month_number",
                            values="total_amount_inr", aggfunc="sum", fill_value=0)
    fig = px.imshow(heat, aspect="auto", title="Revenue intensity: market × month",
                    color_continuous_scale="Tealgrn", labels=dict(x="Month number", y="Market", color="Revenue"))
    st.plotly_chart(plot_layout(fig, 420), use_container_width=True)

# -------------------- MARKETING --------------------
elif page == "Marketing":
    st.subheader("👥 Customer and channel analytics")
    a, b, c = st.columns(3)
    a.metric("Unique customers", f"{data['customer_code'].nunique():,}")
    b.metric("Markets reached", f"{data['market'].nunique():,}")
    c.metric("Sales channels", f"{data['channel'].nunique():,}")

    left, right = st.columns(2)
    with left:
        st.plotly_chart(bar_chart(data, "customer", "total_amount_inr",
                                  "Top 15 customers by revenue", horizontal=True, top=15),
                        use_container_width=True)
    with right:
        channel = data.groupby("channel", as_index=False)["total_amount_inr"].sum()
        fig = px.pie(channel, names="channel", values="total_amount_inr",
                     hole=.5, title="Revenue mix by channel",
                     color_discrete_sequence=PALETTE)
        st.plotly_chart(plot_layout(fig, 420), use_container_width=True)

    left, right = st.columns(2)
    with left:
        platform = data.groupby("platform", as_index=False)["total_amount_inr"].sum()
        fig = px.pie(platform, names="platform", values="total_amount_inr",
                     hole=.5, title="Revenue mix by platform",
                     color_discrete_sequence=PALETTE)
        st.plotly_chart(plot_layout(fig, 420), use_container_width=True)
    with right:
        grouped = data.groupby(["market", "channel"], as_index=False)["total_amount_inr"].sum()
        fig = px.bar(grouped, x="market", y="total_amount_inr", color="channel",
                     barmode="group", title="Channel revenue comparison by market",
                     color_discrete_sequence=PALETTE)
        st.plotly_chart(plot_layout(fig, 420), use_container_width=True)

    st.subheader("Customer revenue distribution")
    fig = px.box(data, x="market", y="total_amount_inr", color="market",
                 title="Sales value distribution by market",
                 color_discrete_sequence=PALETTE, points="outliers")
    st.plotly_chart(plot_layout(fig, 430), use_container_width=True)

    st.subheader("Customer detail")
    customer_summary = (data.groupby(["customer_code", "customer", "market"], as_index=False)
                        .agg(revenue=("total_amount_inr", "sum"),
                             quantity=("sold_quantity", "sum"),
                             sales_records=("total_amount_inr", "size"))
                        .sort_values("revenue", ascending=False))
    st.dataframe(customer_summary, use_container_width=True)

# -------------------- FINANCE --------------------
elif page == "Finance":
    st.subheader("💰 Finance and revenue analytics")
    revenue = data["total_amount_inr"].sum()
    avg_price = data["price_inr"].mean()
    a, b, c = st.columns(3)
    a.metric("Total revenue", money(revenue))
    b.metric("Average unit price", money(avg_price))
    c.metric("Total quantity", f"{data['sold_quantity'].sum():,.0f}")

    quarterly = (data.groupby("quarter_label", as_index=False)
                 .agg(revenue=("total_amount_inr", "sum"))
                 .sort_values("quarter_label"))
    fig = px.bar(quarterly, x="quarter_label", y="revenue",
                 title="Quarterly revenue", text_auto=".2s",
                 color="revenue", color_continuous_scale="Viridis")
    st.plotly_chart(plot_layout(fig, 420), use_container_width=True)

    # Waterfall: change between consecutive quarters
    if len(quarterly) >= 2:
        changes = quarterly["revenue"].diff().iloc[1:]
        labels = quarterly["quarter_label"].iloc[1:].tolist()
        fig = go.Figure(go.Waterfall(
            x=labels,
            y=changes,
            measure=["relative"] * len(changes),
            connector={"line": {"color": "#64748B"}},
            increasing={"marker": {"color": "#34D399"}},
            decreasing={"marker": {"color": "#FB7185"}}
        ))
        fig.update_layout(title="Quarter-over-quarter revenue change",
                          yaxis_title="Change in revenue")
        st.plotly_chart(plot_layout(fig, 400), use_container_width=True)

    left, right = st.columns(2)
    with left:
        fig = px.histogram(data, x="total_amount_inr", nbins=40,
                           title="Sales record revenue distribution",
                           color_discrete_sequence=[PALETTE[1]])
        st.plotly_chart(plot_layout(fig, 400), use_container_width=True)
    with right:
        fig = px.scatter(data, x="price_inr", y="sold_quantity",
                         size="total_amount_inr", color="division",
                         hover_data=["product", "market"],
                         title="Unit price vs quantity (bubble size = revenue)",
                         color_discrete_sequence=PALETTE)
        st.plotly_chart(plot_layout(fig, 400), use_container_width=True)

    st.subheader("Revenue by division")
    st.plotly_chart(bar_chart(data, "division", "total_amount_inr",
                              "Revenue by division"), use_container_width=True)

    st.subheader("Optional revenue target")
    target = st.number_input("Enter a revenue target (INR)", min_value=0.0,
                             value=0.0, step=100000.0)
    if target > 0:
        progress = min(revenue / target, 1.0)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=progress * 100,
            number={"suffix": "%"},
            title={"text": "Revenue target achievement"},
            gauge={"axis": {"range": [0, 100]},
                   "bar": {"color": "#38BDF8"},
                   "steps": [{"range": [0, 50], "color": "#263449"},
                             {"range": [50, 80], "color": "#334155"},
                             {"range": [80, 100], "color": "#14532D"}]}
        ))
        st.plotly_chart(plot_layout(fig, 320), use_container_width=True)
        st.caption(f"Actual revenue: {money(revenue)} | Target: {money(target)}")
    else:
        st.info("Enter a target above to display the revenue achievement gauge. No target is assumed.")

# -------------------- SUPPLY CHAIN --------------------
elif page == "Supply Chain":
    st.subheader("📦 Product and supply analysis")
    a, b, c = st.columns(3)
    a.metric("Quantity sold", f"{data['sold_quantity'].sum():,.0f}")
    b.metric("Product variants", f"{data['variant'].nunique():,}")
    c.metric("Categories", f"{data['category'].nunique():,}")

    left, right = st.columns(2)
    with left:
        st.plotly_chart(bar_chart(data, "division", "sold_quantity",
                                  "Quantity sold by division"), use_container_width=True)
    with right:
        st.plotly_chart(bar_chart(data, "category", "sold_quantity",
                                  "Quantity sold by category"), use_container_width=True)

    hierarchy = (data.groupby(["division", "category", "product"], as_index=False)
                 ["total_amount_inr"].sum())
    fig = px.treemap(hierarchy, path=["division", "category", "product"],
                     values="total_amount_inr", color="total_amount_inr",
                     color_continuous_scale="Tealgrn",
                     title="Product hierarchy by revenue")
    st.plotly_chart(plot_layout(fig, 520), use_container_width=True)

    fig = px.sunburst(hierarchy, path=["division", "category", "product"],
                      values="total_amount_inr",
                      title="Revenue hierarchy: division → category → product",
                      color="total_amount_inr", color_continuous_scale="Viridis")
    st.plotly_chart(plot_layout(fig, 520), use_container_width=True)

    fig = px.violin(data, x="channel", y="sold_quantity", color="channel",
                    box=True, points=False, title="Quantity distribution by channel",
                    color_discrete_sequence=PALETTE)
    st.plotly_chart(plot_layout(fig, 430), use_container_width=True)

    st.subheader("Product detail")
    product_summary = (data.groupby(["division", "category", "product", "variant"], as_index=False)
                       .agg(quantity=("sold_quantity", "sum"),
                            revenue=("total_amount_inr", "sum"),
                            average_price=("price_inr", "mean"))
                       .sort_values("revenue", ascending=False))
    st.dataframe(product_summary, use_container_width=True)

# -------------------- EXPORT + FOOTER --------------------
st.divider()
st.subheader("⬇️ Export filtered data")
csv_bytes = data.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download current filtered data (CSV)",
    data=csv_bytes,
    file_name="ecommerce_filtered_data.csv",
    mime="text/csv"
)
st.caption("E-Commerce Data Engineering Portfolio | Python • Streamlit • Plotly • Databricks")
