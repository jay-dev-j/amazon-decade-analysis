import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Amazon India Decade Analysis Dashboard", layout="wide")
st.markdown(
    """
    <h3 style='font-size:13px;'>Executive Dashboard</h3>
    """,
    unsafe_allow_html=True
)

@st.cache_data(ttl=300)
def load_data(query):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="amazon_analytics"
    )
    df = pd.read_sql(query, conn)
    conn.close()
    return df
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False

# global data 
query_kpi = """
    SELECT 
        SUM(final_amount_inr) AS total_revenue,
        COUNT(DISTINCT customer_id) AS active_customers,
        AVG(final_amount_inr) AS avg_order_value
    FROM transactions_master;
    """
if not st.session_state.data_loaded:
    with st.spinner("Loading dashboard..."):
        st.session_state.df_kpi = load_data(query_kpi)
    st.session_state.data_loaded = True

section = st.sidebar.radio("Select Section", [
    "Q1 Executive",
    "Q2 Real-time",
    "Q3 Strategic",
    "Q4 Financial",
    "Q5 Growth"
])




if section == "Q1 Executive":
    # 1

    # getting kpi data
    st.header(" Executive Summary (Q1)")
    df_kpi = st.session_state.df_kpi
    

    #  Yearly revenue first 

    # Yearly revenue 

    query_year = """
    SELECT order_year, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY order_year
    ORDER BY order_year;
    """

    if "df_year" not in st.session_state:
        st.session_state.df_year = load_data(query_year)

    df_year = st.session_state.df_year

    df_year['growth'] = df_year['revenue'].pct_change() * 100
    df_year = df_year.dropna()
    df_year['growth'] = df_year['growth'].clip(-100, 200)
    df_year['growth'] = df_year['growth'].round(2)
    
    # Latest growth
    latest_growth = df_year['growth'].dropna().iloc[-1]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(" Total Revenue", f"₹ {df_kpi['total_revenue'][0]:,.0f}")
    col2.metric(" Customers", int(df_kpi['active_customers'][0]))
    col3.metric(" Avg Order Value", f"₹ {df_kpi['avg_order_value'][0]:,.0f}")
    col4.metric(" Growth Rate", f"{latest_growth:.2f}%")


    # Calculate growth %
    df_year['growth'] = df_year['revenue'].pct_change() * 100



    #Revenue Trend (LINE CHART)
    col1, col2 = st.columns(2)
    st.subheader(" Revenue Trend")
    with col1:
        fig = px.line(df_year, x="order_year", y="revenue", title=" Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)


    # Year-over-Year 
    with col2:
        st.subheader(" Growth Analysis")
        df_year['growth'] = df_year['growth'].clip(-100, 200)
        df_year['growth'] = df_year['growth'].round(2)
        df_year['order_year'] = df_year['order_year'].astype(str)
        fig2 = px.bar(df_year, x="order_year", y="growth", title=" Year-over-Year Growth %")
        st.plotly_chart(fig2, use_container_width=True)


    # Top Categories

    query_cat = """
    SELECT subcategory, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY subcategory
    ORDER BY revenue DESC
    LIMIT 5;
    """

    if "df_cat" not in st.session_state:
        st.session_state.df_cat = load_data(query_cat)

    df_cat = st.session_state.df_cat
    df_cat["revenue"] = pd.to_numeric(df_cat["revenue"], errors="coerce")

    st.subheader("Top Subcategories")

    fig3 = px.bar(
        df_cat,
        x="subcategory",
        y="revenue",
        color="subcategory",
        text="revenue",
        title="Top Performing Subcategories"
    )

    fig3.update_traces(textposition="outside")
    fig3.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig3, use_container_width=True, key="top_subcategory")

elif section == "Q2 Real-time":
    # 2

    # Current Month Sales

    st.header(" Real-time Business Monitor (Q2)")

    query_current = """
    SELECT SUM(final_amount_inr) AS current_sales
    FROM transactions_master
    WHERE order_year = 2025 AND order_month = 4;
    """

    df_current = load_data(query_current)

    current_sales = df_current['current_sales'][0]


    target = 5000000   #random value

    # Row 1 → Target vs Actual
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(" Target vs Actual")
        st.metric(" Target Sales", f"₹ {target:,.0f}")

    with col2:
        st.subheader(" ")
        st.metric(
            " Current Sales",
            f"₹ {current_sales:,.0f}",
            delta=f"{current_sales - target:,.0f}"
        )


    # Revenue Run Rate
    days_passed = 15
    total_days = 30
    run_rate = (current_sales / days_passed) * total_days


    # Customer Acquisition
    query_customers = """
    SELECT COUNT(DISTINCT customer_id) AS customers
    FROM transactions_master
    WHERE order_year = 2025 AND order_month = 4;
    """
    df_cust = load_data(query_customers)


    # Row 2 → Run Rate + Customers (SIDE BY SIDE)
    col3, col4 = st.columns(2)

    with col3:
        st.subheader(" Run Rate")
        st.metric(" Run Rate", f"₹ {run_rate:,.0f}")

    with col4:
        st.subheader(" Customer Acquisition")
        st.metric(" New Customers", df_cust['customers'][0])


    # Alert System
    if current_sales < target:
        st.error(" Sales are below target!")
    else:
        st.success("Target achieved!")
        
    # Target vs Actual Chart
    df_compare = pd.DataFrame({
        "Type": ["Target", "Actual"],
        "Value": [target, current_sales]
    })

    fig4 = px.bar(df_compare, x="Type", y="Value", title=" Target vs Actual")

    st.plotly_chart(fig4, use_container_width=True)
    st.divider()

elif section == "Q3 Strategic":
    # 3
    
    
    st.header(" Strategic Overview (Q3)")

    query_category = """
    SELECT subcategory, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY subcategory
    ORDER BY revenue DESC;
    """

    df_category = load_data(query_category)
    df_category["revenue"] = pd.to_numeric(df_category["revenue"], errors="coerce")

    st.subheader("Market Share")

    fig_cat = px.pie(
        df_category,
        names="subcategory",
        values="revenue",
        title="Market Share by Subcategory"
    )

    st.plotly_chart(fig_cat, use_container_width=True, key="market_share_subcat")

    # Competitive Position (Brand)

    query_brand = """
    SELECT brand, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY brand
    ORDER BY revenue DESC
    LIMIT 10;
    """

    df_brand = load_data(query_brand)
    col5,col6=st.columns(2)
    with col5:
        st.subheader("Brand Performance")

        fig_brand = px.bar(df_brand, x="brand", y="revenue",title="Top Brands Performance")

        st.plotly_chart(fig_brand, use_container_width=True)

    # Geographic Expansion

    query_geo = """
    SELECT customer_state, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY customer_state
    ORDER BY revenue DESC;
    """

    df_geo = load_data(query_geo)
    with col6:
        st.subheader(" Geographic Performance")

        fig_geo = px.bar(df_geo, x="customer_state", y="revenue", title="Revenue by State")

        st.plotly_chart(fig_geo, use_container_width=True)
        
    # Business Health Indicators
    df_kpi = st.session_state.df_kpi
    col1, col2 = st.columns(2)

    col1.metric(" Total Revenue", f"₹ {df_kpi['total_revenue'][0]:,.0f}")
    col2.metric(" Customers", int(df_kpi['active_customers'][0]))
    st.divider()

elif section == "Q4 Financial":
   
    # 4
    st.header("Financial Performance (Q4)")

    query_cat = """
    SELECT subcategory, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY subcategory
    ORDER BY revenue DESC;
    """

    df_cat = load_data(query_cat)
    df_cat["revenue"] = pd.to_numeric(df_cat["revenue"], errors="coerce")

    st.subheader("Revenue Breakdown")

    fig1 = px.bar(
        df_cat,
        x="subcategory",
        y="revenue",
        color="subcategory",
        text="revenue",
        title="Revenue by Subcategory"
    )

    fig1.update_traces(textposition="outside")
    fig1.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig1, use_container_width=True, key="financial_subcat")

    # Profit Margin Analysis

    # Profit = final_amount_inr - original_price_inr

    query_profit = """
    SELECT 
        SUM(final_amount_inr - original_price_inr) AS profit,
        SUM(final_amount_inr) AS revenue
    FROM transactions_master;
    """

    df_profit = load_data(query_profit)

    profit = df_profit['profit'][0]
    revenue = df_profit['revenue'][0]

    margin = (profit / revenue) * 100
    st.subheader("Profit Margin")
    st.metric(" Profit Margin", f"{margin:.2f}%")

    # Cost Structure Visualization

    query_cost = """
    SELECT 
        SUM(original_price_inr) AS original_price,
        SUM(discounted_price_inr) AS discounted_price,
        SUM(final_amount_inr) AS final_price
    FROM transactions_master;
    """

    df_cost = load_data(query_cost)

    df_cost_chart = pd.DataFrame({
        "Type": ["Original", "Discounted", "Final"],
        "Amount": [
            df_cost['original_price'][0],
            df_cost['discounted_price'][0],
            df_cost['final_price'][0]
        ]
    })
    
    col7,col8=st.columns(2)
    with col7:
        st.subheader("Cost Structure")
        fig2 = px.bar(df_cost_chart, x="Type", y="Amount",title="Cost Structure")

        st.plotly_chart(fig2, use_container_width=True)


    # Financial Forecasting (Simple)

    query_forecast = """
    SELECT order_year, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY order_year
    ORDER BY order_year;
    """

    df_forecast = load_data(query_forecast)
    with col8:
        st.subheader("Revenue Forecast")

        fig3 = px.line(df_forecast, x="order_year", y="revenue",
                    title="Revenue Forecast Trend")

        st.plotly_chart(fig3, use_container_width=True)
    st.divider()

elif section == "Q5 Growth":
    # 5
    st.header(" Growth Analytics (Q5)")
    # Customer Growth

    query_customer_growth = """
    SELECT order_year, COUNT(DISTINCT customer_id) AS customers
    FROM transactions_master
    GROUP BY order_year
    ORDER BY order_year;
    """

    df_customer = load_data(query_customer_growth)
    col9,col10=st.columns(2)
    with col9:
        st.subheader("Customer Growth")
        fig1 = px.line(df_customer, x="order_year", y="customers",title="Customer Growth")

        st.plotly_chart(fig1, use_container_width=True)

    # Market Penetration (States)

    query_state = """
    SELECT customer_state, COUNT(DISTINCT customer_id) AS customers
    FROM transactions_master
    GROUP BY customer_state
    ORDER BY customers DESC;
    """

    df_state = load_data(query_state)
    with col10:
        st.subheader("Market Penetration")
        fig2 = px.bar(df_state, x="customer_state", y="customers",title="Market Penetration by State")

        st.plotly_chart(fig2, use_container_width=True)

    # Product Portfolio Expansion

    query_product = """
    SELECT order_year, COUNT(DISTINCT product_id) AS products
    FROM transactions_master
    GROUP BY order_year
    ORDER BY order_year;
    """

    df_product = load_data(query_product)
    col11,col12=st.columns(2)
    with col11:
        st.subheader("Product Growth")
        fig3 = px.line(df_product, x="order_year", y="products",title="Product Portfolio Growth")

        st.plotly_chart(fig3, use_container_width=True)

    # Strategic Performance (Prime vs Non-Prime)

    query_prime = """
    SELECT is_prime_member, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY is_prime_member;
    """

    df_prime = load_data(query_prime)

    df_prime['type'] = df_prime['is_prime_member'].map({1: "Prime", 0: "Non-Prime"})

    with col12:
        st.subheader(" Prime Performance")

        fig4 = px.bar(df_prime, x="type", y="revenue",title="Prime vs Non-Prime Revenue")

        st.plotly_chart(fig4, use_container_width=True)

    # Predictive Insight (Trend)

    fig5 = px.line(df_customer, x="order_year", y="customers",title="Customer Growth Trend (Prediction View)")

    st.plotly_chart(fig5, use_container_width=True)
    st.divider()