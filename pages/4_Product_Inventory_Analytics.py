import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Amazon India Decade Analysis Dashboard", layout="wide")
st.markdown(
    """
    <h3 style='font-size:13px;'>Product Inventory Dashboard</h3>
    """,
    unsafe_allow_html=True
)

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

section = st.sidebar.radio("Select Section", [
    "Q16 Product",
    "Q17 Brand",
    "Q18 Inventory",
    "Q19 Ratings",
    "Q20 Launch"
])
if section == "Q16 Product":
    # 16

    st.header("Product Performance")

    query_product = """
    SELECT 
        product_name,
        category,
        SUM(final_amount_inr) AS revenue,
        SUM(quantity) AS units_sold,
        AVG(product_rating) AS rating,
        SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS return_rate
    FROM transactions_master
    GROUP BY product_name, category
    ORDER BY revenue DESC
    LIMIT 20;
    """

    if "df_q16" not in st.session_state:
        st.session_state.df_q16 = load_data(query_product)

    df = st.session_state.df_q16

    st.subheader("Top 20 Products")
    st.dataframe(df)

    col1, col2 = st.columns(2)
    with col1:
        fig1 = px.bar(df, x="product_name", y="revenue",title="Revenue by Product")
        st.plotly_chart(fig1, width='stretch')
        
    with col2:
        fig2 = px.bar(df, x="product_name", y="units_sold",title="Units Sold")
        st.plotly_chart(fig2, width='stretch')
        
    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.bar(df, x="product_name", y="rating",title="Product Ratings")
        st.plotly_chart(fig3, width='stretch')
        
    with col4:
        fig4 = px.bar(df, x="product_name", y="return_rate",title="Return Rate (%)")
        st.plotly_chart(fig4, width='stretch')
        
    # Category Analysis
    query_category = """
    SELECT 
        category,
        SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY category
    ORDER BY revenue DESC;
    """

    df_cat = load_data(query_category)

    st.subheader("Category-wise Performance")

    fig5 = px.bar(df_cat, x="category", y="revenue",title="Revenue by Category")

    st.plotly_chart(fig5, width='stretch')

    query_life = """
    SELECT 
        product_name,
        order_year,
        SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY product_name, order_year;
    """

    df_life = load_data(query_life)
    st.subheader("Product Lifecycle")

    selected_product = st.selectbox(
        "Select Product",
        df_life["product_name"].unique()
    )
    filtered = df_life[df_life["product_name"] == selected_product]

    fig6 = px.line(
        filtered,
        x="order_year",
        y="revenue",
        title=f"Lifecycle Trend - {selected_product}",
        markers=True
    )

    st.plotly_chart(fig6, width='stretch')
elif section == "Q17 Brand":
    col1,col2=st.columns(2)
    # 17
    # Brand Performance (Revenue)
    with col1:
        
        st.header("Brand Analytics")


        query_brand = """
        SELECT 
            brand,
            SUM(final_amount_inr) AS revenue
        FROM transactions_master
        GROUP BY brand
        ORDER BY revenue DESC
        LIMIT 10;
        """

        df_brand = load_data(query_brand)

        st.subheader("Top Brands by Revenue")

        fig1 = px.bar(df_brand,x="brand",y="revenue",title="Top 10 Brands by Revenue")

        st.plotly_chart(fig1, width='stretch')
    with col2:
        # Market Share
        st.subheader("Market Share")

        fig2 = px.pie(df_brand,names="brand",values="revenue",title="Market Share by Brand")

        st.plotly_chart(fig2, width='stretch')

    # Customer Preference (Units Sold)

    query_units = """
    SELECT 
        brand,
        SUM(quantity) AS units_sold
    FROM transactions_master
    GROUP BY brand
    ORDER BY units_sold DESC
    LIMIT 10;
    """

    df_units = load_data(query_units)

    st.subheader("Customer Preference (Units Sold)")

    fig3 = px.bar(df_units,x="brand",y="units_sold",title="Top Brands by Units Sold")

    st.plotly_chart(fig3, width='stretch')

    # Competitive Positioning
    query_comp = """
    SELECT 
        category,
        brand,
        SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY category, brand;
    """

    df_comp = load_data(query_comp)

    st.subheader(" Competitive Positioning")

    selected_category = st.selectbox(
        "Select Category",
        df_comp["category"].unique()
    )

    filtered = df_comp[df_comp["category"] == selected_category]

    fig4 = px.bar(filtered,x="brand",y="revenue",title=f"Brand Competition in {selected_category}")

    st.plotly_chart(fig4, width='stretch')

    # Market Share Evolution

    query_trend = """
    SELECT 
        order_year,
        brand,
        SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY order_year, brand;
    """

    df_trend = load_data(query_trend)
    selected_brand = st.selectbox(
        "Select Brand",
        df_trend["brand"].unique()
    )
    brand_data = df_trend[df_trend["brand"] == selected_brand]
    fig5 = px.line(brand_data,x="order_year",y="revenue",title=f"Market Share Trend - {selected_brand}",markers=True)

    st.plotly_chart(fig5, width='stretch')
elif section == "Q18 Inventory":
    col5,col6=st.columns(2)
    with col5:
        st.header("Inventory Optimization")
        # 18
        # Product Demand Patterns
        query_demand = """
        SELECT 
            product_name,
            SUM(quantity) AS total_demand
        FROM transactions_master
        GROUP BY product_name
        ORDER BY total_demand DESC
        LIMIT 10;
        """

        df_demand = load_data(query_demand)

        st.subheader("Top Product Demand")

        fig1 = px.bar(df_demand,x="product_name",y="total_demand",title="Top 10 Products by Demand")

        st.plotly_chart(fig1, width='stretch')
    with col6:
        # Seasonal Trends (Monthly)

        query_month = """
        SELECT 
            order_month,
            SUM(quantity) AS demand
        FROM transactions_master
        GROUP BY order_month
        ORDER BY order_month;
        """

        df_month = load_data(query_month)

        st.subheader("Monthly Demand Trend")

        fig2 = px.line(df_month,x="order_month",y="demand",title="Monthly Demand Pattern",markers=True
        )

        st.plotly_chart(fig2, width='stretch')
    col7,col8=st.columns(2)
    with col7:
        # Yearly Seasonal Trend

        query_year = """
        SELECT 
            order_year,
            SUM(quantity) AS demand
        FROM transactions_master
        GROUP BY order_year
        ORDER BY order_year;
        """

        df_year = load_data(query_year)

        st.subheader("Yearly Demand Trend")

        fig3 = px.line(df_year,x="order_year",y="demand",title="Yearly Demand Growth",markers=True)

        st.plotly_chart(fig3, width='stretch')
    with col8:
        # Inventory Turnover

        # Inventory Turnover ≈ Total Units Sold / Number of Orders

        query_turnover = """
        SELECT 
            product_name,
            SUM(quantity) AS total_units,
            COUNT(transaction_id) AS total_orders,
            SUM(quantity)/COUNT(transaction_id) AS turnover_ratio
        FROM transactions_master
        GROUP BY product_name
        ORDER BY turnover_ratio DESC
        LIMIT 10;
        """

        df_turnover = load_data(query_turnover)

        st.subheader("Inventory Turnover")

        fig4 = px.bar(df_turnover,x="product_name",y="turnover_ratio",title="Top Products by Turnover Ratio")

        st.plotly_chart(fig4, width='stretch')
    col9,col10=st.columns(2)
    with col9:
        # Category Demand Analysis

        query_category = """
        SELECT 
            category,
            SUM(quantity) AS demand
        FROM transactions_master
        GROUP BY category
        ORDER BY demand DESC;
        """

        df_cat = load_data(query_category)

        st.subheader("Demand by Category")

        fig5 = px.bar(df_cat,x="category",y="demand",title="Category Demand")

        st.plotly_chart(fig5, width='stretch')
    with col10:
        # Demand Forecasting

        st.subheader("Demand Forecasting")

        fig6 = px.line(df_year,x="order_year",y="demand",title="Demand Forecast (Trend)")

        st.plotly_chart(fig6, width='stretch')
elif section == "Q19 Ratings":
    col11,col12=st.columns(2)
    with col11:
        # 19
        # Rating Distribution
        st.header(" Ratings & Reviews")

        query_rating_dist = """
        SELECT 
            ROUND(product_rating) AS rating,
            COUNT(*) AS count
        FROM transactions_master
        GROUP BY ROUND(product_rating)
        ORDER BY rating;
        """

        df_rating = load_data(query_rating_dist)

        st.subheader("Rating Distribution")

        fig1 = px.bar(df_rating,x="rating",y="count",title="Distribution of Ratings")

        st.plotly_chart(fig1, width='stretch')
    with col12:
        # Review Sentiment Analysis

        query_sentiment = """
        SELECT 
            CASE 
                WHEN product_rating >= 4 THEN 'Positive'
                WHEN product_rating = 3 THEN 'Neutral'
                ELSE 'Negative'
            END AS sentiment,
            COUNT(*) AS count
        FROM transactions_master
        GROUP BY sentiment;
        """

        df_sentiment = load_data(query_sentiment)

        st.subheader("Review Sentiment")

        fig2 = px.pie(df_sentiment,names="sentiment",values="count",title="Sentiment Analysis")

        st.plotly_chart(fig2, width='stretch')
    col13,col14=st.columns(2)
    with col13:
        # Rating vs Sales

        query_corr = """
        SELECT 
            ROUND(product_rating) AS rating,
            SUM(quantity) AS total_sales
        FROM transactions_master
        GROUP BY ROUND(product_rating)
        ORDER BY rating;
        """

        df_corr = load_data(query_corr)

        st.subheader("Rating vs Sales")
        df_corr["total_sales"] = pd.to_numeric(df_corr["total_sales"], errors="coerce")
        fig3 = px.scatter(df_corr,x="rating",y="total_sales",size="total_sales",title="Rating vs Sales Relationship")

        st.plotly_chart(fig3, width='stretch')
    with col14:
        # Product Quality Insights (Rating vs Returns)

        query_quality = """
        SELECT 
            ROUND(product_rating) AS rating,
            SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END) AS returns,
            COUNT(*) AS total_orders,
            SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS return_rate
        FROM transactions_master
        GROUP BY ROUND(product_rating)
        ORDER BY rating;
        """

        df_quality = load_data(query_quality)

        st.subheader("Rating vs Return Rate")

        fig4 = px.line(df_quality,x="rating",y="return_rate",title="Return Rate by Rating",markers=True)

        st.plotly_chart(fig4, width='stretch')

    # Top Rated Products

    query_top = """
    SELECT 
        product_name,
        AVG(product_rating) AS avg_rating,
        SUM(quantity) AS sales
    FROM transactions_master
    GROUP BY product_name
    HAVING avg_rating >= 4
    ORDER BY avg_rating DESC
    LIMIT 10;
    """

    df_top = load_data(query_top)

    st.subheader("Top Rated Products")

    fig5 = px.bar(df_top,x="product_name",y="avg_rating",title="Top Rated Products")

    st.plotly_chart(fig5, width='stretch')
elif section == "Q20 Launch":
    # 20
    # Identify Launch Year
    st.header("Product Launch")


    query_launch = """
    SELECT 
        product_name,
        MIN(order_year) AS launch_year
    FROM transactions_master
    GROUP BY product_name;
    """

    df_launch = load_data(query_launch)

    selected_year = st.selectbox(
        "Select Launch Year",
        sorted(df_launch["launch_year"].unique())
    )

    # Filter New Products
    new_products = df_launch[df_launch["launch_year"] == selected_year]

    query_perf = f"""
    SELECT 
        product_name,
        SUM(final_amount_inr) AS revenue,
        SUM(quantity) AS units_sold,
        AVG(product_rating) AS rating
    FROM transactions_master
    WHERE product_name IN (
        SELECT product_name 
        FROM (
            SELECT product_name, MIN(order_year) AS launch_year
            FROM transactions_master
            GROUP BY product_name
        ) t
        WHERE launch_year = {selected_year}
    )
    GROUP BY product_name
    ORDER BY revenue DESC;
    """

    df_perf = load_data(query_perf)

    st.subheader("Launch Performance")

    fig1 = px.bar(df_perf,x="product_name",y="revenue",title="Revenue of Newly Launched Products")

    st.plotly_chart(fig1, width='stretch')
    col15,col16=st.columns(2)
    with col15:
        # Market Acceptance
        st.subheader("Market Acceptance")

        df_perf["revenue"] = pd.to_numeric(df_perf["revenue"], errors="coerce")
        df_perf["units_sold"] = pd.to_numeric(df_perf["units_sold"], errors="coerce")
        df_perf["rating"] = pd.to_numeric(df_perf["rating"], errors="coerce")
        
        fig2 = px.scatter(df_perf,x="units_sold",y="rating",size="revenue",title="Sales vs Rating (Acceptance)")

        st.plotly_chart(fig2, width='stretch')
    with col16:
        # Competitive Analysis

        query_all = """
        SELECT 
            product_name,
            SUM(final_amount_inr) AS revenue
        FROM transactions_master
        GROUP BY product_name
        ORDER BY revenue DESC
        LIMIT 20;
        """

        df_all = load_data(query_all)

        st.subheader("Competitive Position")

        fig3 = px.bar(df_all,x="product_name",y="revenue",title="Top Products in Market")

        st.plotly_chart(fig3, width='stretch')

    # Success Metrics

    total_revenue = df_perf["revenue"].sum()
    avg_rating = df_perf["rating"].mean()
    total_units = df_perf["units_sold"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Revenue", f"₹ {total_revenue:,.0f}")
    col2.metric("Avg Rating", f"{avg_rating:.2f}")
    col3.metric("Units Sold", f"{total_units:,}")

    # Growth Trend (Lifecycle of New Products)

    query_growth = f"""
    SELECT 
        order_year,
        SUM(final_amount_inr) AS revenue
    FROM transactions_master
    WHERE product_name IN (
        SELECT product_name 
        FROM (
            SELECT product_name, MIN(order_year) AS launch_year
            FROM transactions_master
            GROUP BY product_name
        ) t
        WHERE launch_year = {selected_year}
    )
    GROUP BY order_year
    ORDER BY order_year;
    """

    df_growth = load_data(query_growth)

    st.subheader("Growth Trend")

    fig4 = px.line(df_growth,x="order_year",y="revenue",title="Growth of New Products",markers=True)

    st.plotly_chart(fig4, width='stretch')

