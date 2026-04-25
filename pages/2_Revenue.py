import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import json

# Database connector
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

st.set_page_config(page_title="Revenue Dashboard", layout="wide")

st.title(" Revenue Dashboard")

section = st.sidebar.radio("Select Section", [
    "Q6 Revenue Trend",
    "Q7 Category",
    "Q8 Geographic",
    "Q9 Festival",
    "Q10 Price Optimization"
])

if section == "Q6 Revenue Trend":
    st.header("Revenue Trend (Q6)")

    time_view = st.selectbox("Select Time Period", ["Yearly", "Quarterly", "Monthly"])

    if time_view == "Yearly":
        query = """
        SELECT order_year AS time, SUM(final_amount_inr) AS revenue
        FROM transactions_master
        GROUP BY order_year
        ORDER BY order_year;
        """
    elif time_view == "Quarterly":
        query = """
        SELECT CONCAT(order_year, '-Q', order_quarter) AS time,
        SUM(final_amount_inr) AS revenue
        FROM transactions_master
        GROUP BY order_year, order_quarter
        ORDER BY order_year, order_quarter;
        """
    else:
        query = """
        SELECT CONCAT(order_year, '-', order_month) AS time,
        SUM(final_amount_inr) AS revenue
        FROM transactions_master
        GROUP BY order_year, order_month
        ORDER BY order_year, order_month;
        """

    df_time = load_data(query)

    fig = px.line(df_time, x="time", y="revenue", title="Revenue Trend")

    df_time['time'] = df_time['time'].astype(str)
    df_time['growth'] = df_time['revenue'].pct_change() * 100
    df_time = df_time.dropna()
    df_time['growth'] = df_time['growth'].clip(-100, 200).round(2)

    fig2 = px.bar(df_time, x="time", y="growth", title="Growth Rate (%)")

    fig4 = px.line(df_time, x="time", y="revenue", title="Forecast Trend")

    # Layout
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    if time_view == "Monthly":
        df_time['month'] = df_time['time'].str.split('-').str[1]
        fig3 = px.box(df_time, x="month", y="revenue", title="Seasonal Variation")

        with col3:
            st.plotly_chart(fig3, use_container_width=True)
        with col4:
            st.plotly_chart(fig4, use_container_width=True)
    else:
        with col3:
            st.plotly_chart(fig4, use_container_width=True)

elif section == "Q7 Category":
    st.header("Category Performance (Q7)")

    # Category Revenue
    query_cat = """
    SELECT category, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY category
    ORDER BY revenue DESC;
    """
    if "df_cat_q7" not in st.session_state:
        st.session_state.df_cat_q7 = load_data(query_cat)

    df_cat = st.session_state.df_cat_q7

    fig1 = px.bar(df_cat, x="category", y="revenue", title="Category Revenue")

    query_growth = """
    SELECT order_year, category, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY order_year, category;
    """
    df_growth = load_data(query_growth)

    fig2 = px.line(df_growth, x="order_year", y="revenue", color="category")

    # Subcategory Pie 
    query_subcat = """
    SELECT subcategory, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY subcategory
    ORDER BY revenue DESC;
    """
    df_subcat = load_data(query_subcat)

    fig3 = px.pie(
        df_subcat,
        names="subcategory",
        values="revenue",
        title="Market Share by Subcategory"
    )

    fig3.update_traces(textinfo='percent+label')

    # Profit
    query_profit = """
    SELECT category, SUM(final_amount_inr - original_price_inr) AS profit
    FROM transactions_master
    GROUP BY category;
    """
    df_profit = load_data(query_profit)

    fig4 = px.bar(df_profit, x="category", y="profit")

    # Layout
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True, key="cat_bar")
    with col2:
        st.plotly_chart(fig2, use_container_width=True, key="cat_growth")

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(fig3, use_container_width=True, key="subcat_pie")
    with col4:
        st.plotly_chart(fig4, use_container_width=True, key="profit_bar")

elif section == "Q8 Geographic":
    st.header("Geographic Analysis (Q8)")

    query_state = """
    SELECT customer_state, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY customer_state;
    """
    df_state = load_data(query_state)

    fig1 = px.bar(df_state, x="customer_state", y="revenue")

    query_city = """
    SELECT customer_city, SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY customer_city LIMIT 10;
    """
    df_city = load_data(query_city)

    fig2 = px.bar(df_city, x="customer_city", y="revenue")

    query_tier = """
    SELECT customer_tier, SUM(final_amount_inr) AS revenue
    FROM transactions_master GROUP BY customer_tier;
    """
    df_tier = load_data(query_tier)

    fig3 = px.pie(df_tier, names="customer_tier", values="revenue")

    # Layout
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(fig3, use_container_width=True)

elif section == "Q9 Festival":
    st.header("Festival Analysis (Q9)")

    query_festival = """
    SELECT is_festival_sale, SUM(final_amount_inr) AS revenue
    FROM transactions_master GROUP BY is_festival_sale;
    """
    df_festival = load_data(query_festival)

    df_festival['type'] = df_festival['is_festival_sale'].map({1: "Festival", 0: "Normal"})
    fig1 = px.bar(df_festival, x="type", y="revenue")

    query_month = """
    SELECT order_month, SUM(final_amount_inr) AS revenue
    FROM transactions_master WHERE is_festival_sale=1 GROUP BY order_month;
    """
    df_month = load_data(query_month)

    fig2 = px.line(df_month, x="order_month", y="revenue")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

elif section == "Q10 Price Optimization":
    st.header("Price Optimization (Q10)")

    query_discount = """
    SELECT discount_percent, SUM(final_amount_inr) AS revenue
    FROM transactions_master GROUP BY discount_percent;
    """
    df_discount = load_data(query_discount)

    fig2 = px.line(df_discount, x="discount_percent", y="revenue")

    query_brand_price = """
    SELECT brand, AVG(discounted_price_inr) AS avg_price
    FROM transactions_master GROUP BY brand;
    """
    df_brand_price = load_data(query_brand_price)

    fig3 = px.bar(df_brand_price, x="brand", y="avg_price")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.plotly_chart(fig3, use_container_width=True)