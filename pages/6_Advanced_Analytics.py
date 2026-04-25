import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Amazon India Decade Analysis Dashboard", layout="wide")
st.markdown(
    """
    <h3 style='font-size:13px;'>Advanced Analytics Dashboard</h3>
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

st.sidebar.title("Advanced Analytics")

section = st.sidebar.radio("Select Dashboard", [
    "Q26 Predictive",
    "Q27 Market Intelligence",
    "Q28 Cross-selling",
    "Q29 Seasonal Planning",
    "Q30 Command Center"
])

if section == "Q26 Predictive":

    st.header("Predictive Analytics")
    # 26
    # Sales Forecasting

    query_sales = """
    SELECT 
        order_year,
        SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY order_year
    ORDER BY order_year;
    """

    if "df_sales" not in st.session_state:
        st.session_state.df_sales = load_data(query_sales)

    df_sales = st.session_state.df_sales
    df_sales["revenue"] = pd.to_numeric(df_sales["revenue"], errors="coerce")

    # Calculate growth rate
    growth_rate = df_sales["revenue"].pct_change().mean()

    last_year = df_sales["order_year"].max()
    last_value = df_sales["revenue"].iloc[-1]

    forecast_value = last_value * (1 + growth_rate)

    # Add forecast row
    df_forecast = pd.DataFrame({
        "order_year": [last_year + 1],
        "revenue": [forecast_value]
    })

    df_sales_full = pd.concat([df_sales, df_forecast])

    st.subheader("Sales Forecast")

    fig1 = px.line(df_sales_full, x="order_year", y="revenue", markers=True)

    st.plotly_chart(fig1,width="stretch")
    st.divider()

    # Customer Churn Prediction

    # Low rating + return = churn risk

    query_churn = """
    SELECT 
        COUNT(*) AS total_customers,
        SUM(CASE 
            WHEN customer_rating < 3 AND return_status = 'Returned' 
            THEN 1 ELSE 0 END) AS churn_risk
    FROM transactions_master;
    """

    df_churn = load_data(query_churn)

    df_churn = df_churn.astype(float)

    churn_rate = (df_churn["churn_risk"][0] / df_churn["total_customers"][0]) * 100

    st.subheader("Customer Churn Risk")

    st.metric("Churn Risk %", f"{churn_rate:.2f}%")

    st.divider()
    col1,col2=st.columns(2)
    with col1:
        # Demand Planning

        query_demand = """
        SELECT 
            product_name,
            SUM(quantity) AS demand
        FROM transactions_master
        GROUP BY product_name
        ORDER BY demand DESC
        LIMIT 10;
        """

        df_demand = load_data(query_demand)

        df_demand["demand"] = pd.to_numeric(df_demand["demand"], errors="coerce")

        st.subheader("Demand Planning")

        fig2 = px.bar(df_demand, x="product_name", y="demand")

        st.plotly_chart(fig2, width="stretch")
        st.divider()

    with col2:
        # Business Scenario Analysis

        base = last_value

        scenario_df = pd.DataFrame({
            "Scenario": ["Low Growth (5%)", "Medium Growth (10%)", "High Growth (20%)"],
            "Revenue": [
                base * 1.05,
                base * 1.10,
                base * 1.20
            ]
        })

        st.subheader("Business Scenarios")

        fig3 = px.bar(scenario_df, x="Scenario", y="Revenue")

        st.plotly_chart(fig3, width="stretch")

    col1, col2, col3 = st.columns(3)

    col1.metric("Last Revenue", f"₹ {last_value:,.0f}")
    col2.metric("Forecast Revenue", f"₹ {forecast_value:,.0f}")
    col3.metric("Growth Rate", f"{growth_rate*100:.2f}%")

    st.divider()
elif section == "Q27 Market Intelligence":
    st.header("Market Intelligence")

    col3,col4=st.columns(2)
    with col3:
        # 27
        # Competitor Tracking

        query_comp = """
        SELECT 
            brand,
            SUM(final_amount_inr) AS revenue
        FROM transactions_master
        GROUP BY brand
        ORDER BY revenue DESC
        LIMIT 10;
        """

        df_comp = load_data(query_comp)
        df_comp["revenue"] = pd.to_numeric(df_comp["revenue"], errors="coerce")
    with col3:
        st.subheader("Competitor Tracking (Top Brands)")

        fig1 = px.bar(df_comp, x="brand", y="revenue")

        st.plotly_chart(fig1, width='stretch')

        st.divider()
    with col4:
        # Market Trends

        query_trend = """
        SELECT 
            order_year,
            SUM(final_amount_inr) AS revenue
        FROM transactions_master
        GROUP BY order_year
        ORDER BY order_year;
        """

        df_trend = load_data(query_trend)
        df_trend["revenue"] = pd.to_numeric(df_trend["revenue"], errors="coerce")

        st.subheader("Market Trend")

        fig2 = px.line(df_trend, x="order_year", y="revenue", markers=True)

        st.plotly_chart(fig2, width='stretch')

        st.divider()
    col5,col6=st.columns(2)
    with col5:
        # Pricing Intelligence

        query_price = """
        SELECT 
            brand,
            AVG(original_price_inr) AS original_price,
            AVG(discount_percent) AS discount,
            AVG(discounted_price_inr) AS final_price
        FROM transactions_master
        GROUP BY brand;
        """

        df_price = load_data(query_price)

        df_price["original_price"] = pd.to_numeric(df_price["original_price"], errors="coerce")
        df_price["discount"] = pd.to_numeric(df_price["discount"], errors="coerce")
        df_price["final_price"] = pd.to_numeric(df_price["final_price"], errors="coerce")

        st.subheader("Pricing Intelligence")

        fig3 = px.scatter(df_price,x="original_price",y="final_price",size="discount",hover_name="brand",title="Price vs Discount Analysis")

        st.plotly_chart(fig3, width='stretch')
        st.divider()
    with col6:
        query_position = """
        SELECT 
            brand,
            SUM(final_amount_inr) AS revenue,
            AVG(product_rating) AS rating
        FROM transactions_master
        GROUP BY brand;
        """

        df_pos = load_data(query_position)

        df_pos["revenue"] = pd.to_numeric(df_pos["revenue"], errors="coerce")
        df_pos["rating"] = pd.to_numeric(df_pos["rating"], errors="coerce")

        st.subheader("Strategic Positioning")

        fig4 = px.scatter(df_pos,x="rating",y="revenue",size="revenue",hover_name="brand",title="Brand Positioning (Rating vs Revenue)")

        st.plotly_chart(fig4, width='stretch')
        st.divider()

    top_brand = df_comp.iloc[0]["brand"]
    top_revenue = df_comp.iloc[0]["revenue"]

    avg_discount = df_price["discount"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric("Top Brand", top_brand)
    col2.metric("Top Revenue", f"₹ {top_revenue:,.0f}")
    col3.metric("Avg Discount", f"{avg_discount:.2f}%")

    st.divider()
elif section == "Q28 Cross-selling":

    st.header("Cross-selling & Upselling")
    col7,col8=st.columns(2)
    with col7:
        #28
        # Product Associations

        st.subheader("Product Associations")

        query_alt = """
        SELECT 
            subcategory,
            COUNT(*) AS frequency
        FROM transactions_master
        GROUP BY subcategory
        ORDER BY frequency DESC
        LIMIT 10;
        """

        df_alt = load_data(query_alt)

        fig1 = px.bar(df_alt,x="subcategory",y="frequency",color="subcategory",title="Top Subcategories (Cross-sell Insight)")

        st.plotly_chart(fig1, width='stretch', key="alt_assoc")

    with col8:
        # Recommendation Effectiveness

        st.subheader("Recommendation Effectiveness")

        fig2 = px.bar(df_alt,x="subcategory",y="frequency",title="Recommendation Strength")

        st.plotly_chart(fig2, width='stretch', key="alt_recommend")
    col9,col10=st.columns(2)
    with col9:
        # Bundle Opportunities

        query_bundle = """
        SELECT 
            brand,
            subcategory,
            COUNT(*) AS frequency
        FROM transactions_master
        GROUP BY brand, subcategory
        ORDER BY frequency DESC
        LIMIT 10;
        """

        df_bundle = load_data(query_bundle)

        fig3 = px.bar(df_bundle,x="brand",y="frequency",color="subcategory",title="Bundle Opportunities")

        st.plotly_chart(fig3, width='stretch', key="bundle_chart")
        st.divider()
    with col10:
        # Upselling (Revenue Optimization)

        query_upsell = """
        SELECT 
            product_name,
            AVG(final_amount_inr) AS avg_price,
            SUM(quantity) AS demand
        FROM transactions_master
        GROUP BY product_name
        ORDER BY avg_price DESC
        LIMIT 10;
        """
        df_upsell = load_data(query_upsell)

        df_upsell["avg_price"] = pd.to_numeric(df_upsell["avg_price"], errors="coerce")
        df_upsell["demand"] = pd.to_numeric(df_upsell["demand"], errors="coerce")

        st.subheader("Upselling Opportunities")

        fig4 = px.scatter(df_upsell,x="avg_price",y="demand",size="demand",hover_name="product_name",title="High Value Products")

        st.plotly_chart(fig4, width='stretch')

    query_bundle = """
    SELECT 
        subcategory,
        COUNT(*) AS frequency
    FROM transactions_master
    GROUP BY subcategory
    ORDER BY frequency DESC
    LIMIT 10;
    """
    df_bundle = load_data(query_bundle)

    st.subheader("Popular Subcategories (Bundle Insight)")

    fig = px.bar(df_bundle, x="subcategory", y="frequency")

    st.plotly_chart(fig, width='stretch')  
elif section == "Q29 Seasonal Planning":

    st.header("Seasonal Planning")
    col11,col12=st.columns(2)
    with col11:
        # 29

        # Monthly Demand

        query_month = """
        SELECT 
            order_month,
            SUM(quantity) AS demand
        FROM transactions_master
        GROUP BY order_month
        ORDER BY order_month;
        """

        df_month = load_data(query_month)
        df_month["demand"] = pd.to_numeric(df_month["demand"], errors="coerce")

        month_map = {
            1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
            7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"
        }

        df_month["month"] = df_month["order_month"].map(month_map)

        st.subheader("Monthly Demand")

        fig1 = px.line(df_month, x="month", y="demand", markers=True)

        st.plotly_chart(fig1, width='stretch')

        st.divider()
    with col12:
        query_inventory = """
        SELECT 
            product_name,
            SUM(quantity) AS demand
        FROM transactions_master
        GROUP BY product_name
        ORDER BY demand DESC
        LIMIT 10;
        """

        df_inventory = load_data(query_inventory)
        df_inventory["demand"] = pd.to_numeric(df_inventory["demand"], errors="coerce")

        st.subheader("Inventory Planning (Top Products)")

        fig2 = px.bar(df_inventory, x="product_name", y="demand")

        st.plotly_chart(fig2, width='stretch', key="inventory_chart")

        st.divider()
    col13,col14=st.columns(2)
    with col13:
        # Promotional Analysis

        query_festival = """
        SELECT 
            is_festival_sale,
            SUM(final_amount_inr) AS revenue
        FROM transactions_master
        GROUP BY is_festival_sale;
        """

        df_festival = load_data(query_festival)

        df_festival["revenue"] = pd.to_numeric(df_festival["revenue"], errors="coerce")

        # Rename for clarity
        df_festival["sale_type"] = df_festival["is_festival_sale"].map({
            0: "Normal",
            1: "Festival"
        })

        st.subheader("Festival vs Normal Sales")

        fig3 = px.pie(df_festival, names="sale_type", values="revenue")

        st.plotly_chart(fig3, width='stretch')

        st.divider()
    with col14:
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
        df_year["demand"] = pd.to_numeric(df_year["demand"], errors="coerce")

        st.subheader("Seasonal Growth Trend")

        fig4 = px.line(df_year, x="order_year", y="demand", markers=True)

        st.plotly_chart(fig4, width='stretch')

        st.divider()

    peak_month = df_month.loc[df_month["demand"].idxmax(), "month"]
    peak_value = df_month["demand"].max()

    col1, col2 = st.columns(2)

    col1.metric("Peak Month", peak_month)
    col2.metric("Peak Demand", f"{peak_value:,}")

    top_months = df_month.sort_values(by="demand", ascending=False).head(3)

    st.subheader("Resource Allocation (Top Months)")

    fig5 = px.bar(top_months, x="month", y="demand")

    st.plotly_chart(fig5, width='stretch')
elif section == "Q30 Command Center":

    st.header("Business Intelligence Command Center")
    # 30

    query_kpi = """
    SELECT 
        SUM(final_amount_inr) AS revenue,
        SUM(quantity) AS total_sales,
        AVG(customer_rating) AS avg_rating,
        SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS return_rate
    FROM transactions_master;
    """

    df_kpi = load_data(query_kpi)

    df_kpi["revenue"] = pd.to_numeric(df_kpi["revenue"], errors="coerce")
    df_kpi["total_sales"] = pd.to_numeric(df_kpi["total_sales"], errors="coerce")
    df_kpi["avg_rating"] = pd.to_numeric(df_kpi["avg_rating"], errors="coerce")
    df_kpi["return_rate"] = pd.to_numeric(df_kpi["return_rate"], errors="coerce")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Revenue", f"₹ {df_kpi['revenue'][0]:,.0f}")
    col2.metric("Sales", f"{df_kpi['total_sales'][0]:,}")
    col3.metric("Rating", f"{df_kpi['avg_rating'][0]:.2f}")
    col4.metric("Return %", f"{df_kpi['return_rate'][0]:.2f}%")
    
    col15,col16=st.columns(2)
    with col15:
        # PERFORMANCE MONITORING

        query_trend = """
        SELECT 
            order_year,
            SUM(final_amount_inr) AS revenue
        FROM transactions_master
        GROUP BY order_year
        ORDER BY order_year;
        """

        df_trend = load_data(query_trend)
        df_trend["revenue"] = pd.to_numeric(df_trend["revenue"], errors="coerce")

        st.subheader("Business Performance Trend")

        fig1 = px.line(df_trend, x="order_year", y="revenue", markers=True)

        st.plotly_chart(fig1, width='stretch', key="business_trend_chart")
    with col16:
        # CATEGORY PERFORMANCE

        query_cat = """
        SELECT 
            subcategory,
            SUM(final_amount_inr) AS revenue
        FROM transactions_master
        GROUP BY subcategory
        ORDER BY revenue DESC;
        """

        df_cat = load_data(query_cat)
        df_cat["revenue"] = pd.to_numeric(df_cat["revenue"], errors="coerce")

        st.subheader("Subcategory Performance")

        fig2 = px.bar(df_cat,x="subcategory",y="revenue",color="subcategory",text="revenue")

        fig2.update_traces(textposition="outside")
        fig2.update_layout(xaxis_tickangle=-45)

        st.plotly_chart(fig2, width='stretch', key="subcategory_perf")
        
    # AUTOMATED ALERTS

    st.subheader("Alerts & Insights")

    if df_kpi["return_rate"][0] > 10:
        st.error("High Return Rate Detected!")

    if df_kpi["avg_rating"][0] < 3.5:
        st.warning("Customer Satisfaction Low!")

    if df_kpi["revenue"][0] < 1000000:
        st.info("Revenue below target")
        
    # TOP PRODUCTS

    query_top = """
    SELECT 
        product_name,
        SUM(final_amount_inr) AS revenue
    FROM transactions_master
    GROUP BY product_name
    ORDER BY revenue DESC
    LIMIT 10;
    """

    df_top = load_data(query_top)
    df_top["revenue"] = pd.to_numeric(df_top["revenue"], errors="coerce")

    st.subheader("Top Products")

    fig3 = px.bar(df_top, x="product_name", y="revenue")

    st.plotly_chart(fig3, width='stretch',key="TOP_PRODUCTS")

    # DECISION SUPPORT

    st.subheader("Strategic Insights")

    if df_kpi["return_rate"][0] > 10:
        st.write("Improve product quality to reduce returns")

    if df_kpi["avg_rating"][0] < 4:
        st.write("Focus on customer experience")

    if df_kpi["revenue"][0] > 5000000:
        st.write("Expand high-performing categories")