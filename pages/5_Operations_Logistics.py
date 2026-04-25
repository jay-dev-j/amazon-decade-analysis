import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st

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

# PAGE SETTINGS
st.set_page_config(page_title="Operations Logistics Dashboard", layout="wide")

section = st.sidebar.radio("Select Dashboard", [
    "Q21 Delivery",
    "Q22 Payment",
    "Q23 Returns",
    "Q24 Customer Service",
    "Q25 Supply Chain"
])


if section == "Q21 Delivery":

    st.title("Delivery Performance Dashboard (Q21)")
    # DELIVERY KPI

    query_delivery = """
    SELECT 
        AVG(delivery_days) AS avg_delivery,
        MIN(delivery_days) AS fastest,
        MAX(delivery_days) AS slowest
    FROM transactions_master
    WHERE delivery_days > 0;
    """

    if "df_delivery" not in st.session_state:
        st.session_state.df_delivery = load_data(query_delivery)

    df_delivery = st.session_state.df_delivery

    # FIX TYPES
    df_delivery = df_delivery.astype(float)

    col1, col2, col3 = st.columns(3)

    col1.metric("Fastest Delivery", f"{df_delivery['fastest'][0]:.0f} days")
    col2.metric("Avg Delivery", f"{df_delivery['avg_delivery'][0]:.2f} days")
    col3.metric("Slowest Delivery", f"{df_delivery['slowest'][0]:.0f} days")

    st.divider()

    # DELIVERY DISTRIBUTION

    query_dist = """
    SELECT delivery_days
    FROM transactions_master
    WHERE delivery_days > 0;
    """

    df_dist = load_data(query_dist)

    df_dist["delivery_days"] = pd.to_numeric(df_dist["delivery_days"], errors="coerce")

    st.subheader("Delivery Time Distribution")

    fig1 = px.histogram(df_dist, x="delivery_days", title="Delivery Days Distribution")

    st.plotly_chart(fig1, width='stretch')

    st.divider()

    # ON-TIME DELIVERY
    
    query_ontime = """
    SELECT 
        SUM(CASE WHEN delivery_days <= 5 THEN 1 ELSE 0 END)*100.0/COUNT(*) AS on_time_rate
    FROM transactions_master
    WHERE delivery_days > 0;
    """

    df_ontime = load_data(query_ontime)
    df_ontime = df_ontime.astype(float)

    col1, col2, col3 = st.columns(3)

    col1.metric("Fastest", f"{df_delivery['fastest'][0]:.0f} days")
    col2.metric("Average", f"{df_delivery['avg_delivery'][0]:.2f} days")
    col3.metric("Slowest", f"{df_delivery['slowest'][0]:.0f} days")
    st.divider()

    # Delivery Distribution

    query_dist = """
    SELECT delivery_days
    FROM transactions_master
    WHERE delivery_days > 0;
    """

    df_dist = load_data(query_dist)
    df_dist["delivery_days"] = pd.to_numeric(df_dist["delivery_days"], errors="coerce")

    st.subheader("Delivery Distribution")

    fig1 = px.histogram(df_dist, x="delivery_days")

    st.plotly_chart(fig1, width='stretch')
    st.divider()

    # On-Time Delivery %
    # On-time = delivery_days <= 5

    query_ontime = """
    SELECT 
        SUM(CASE WHEN delivery_days <= 5 THEN 1 ELSE 0 END)*100.0/COUNT(*) AS on_time_rate
    FROM transactions_master
    WHERE delivery_days > 0;
    """

    df_ontime = load_data(query_ontime)
    df_ontime = df_ontime.astype(float)

    st.subheader("On-Time Delivery")

    st.metric("On-Time %", f"{df_ontime['on_time_rate'][0]:.2f}%")

    # Geographic Performance

    query_geo = """
    SELECT 
        customer_state,
        AVG(delivery_days) AS avg_delivery
    FROM transactions_master
    GROUP BY customer_state
    ORDER BY avg_delivery;
    """
    df_geo = load_data(query_geo)
    df_geo["avg_delivery"] = pd.to_numeric(df_geo["avg_delivery"], errors="coerce")

    st.subheader("State-wise Delivery")

    fig2 = px.bar(df_geo, x="customer_state", y="avg_delivery")

    st.plotly_chart(fig2, width='stretch')
    st.divider()

    # Delivery Type Performance
    col1,col2=st.columns(2)
    with col1:
        query_type = """
        SELECT 
            delivery_type,
            AVG(delivery_days) AS avg_delivery
        FROM transactions_master
        GROUP BY delivery_type;
        """

        df_type = load_data(query_type)
        df_type["avg_delivery"] = pd.to_numeric(df_type["avg_delivery"], errors="coerce")

        st.subheader("Delivery Type Performance")

        fig3 = px.bar(df_type, x="delivery_type", y="avg_delivery")

        st.plotly_chart(fig3, width='stretch')
        st.divider()
    with col2:
        # Operational Efficiency

        query_eff = """
        SELECT 
            delivery_days,
            AVG(customer_rating) AS avg_rating
        FROM transactions_master
        GROUP BY delivery_days
        ORDER BY delivery_days;
        """

        df_eff = load_data(query_eff)

        df_eff["delivery_days"] = pd.to_numeric(df_eff["delivery_days"], errors="coerce")
        df_eff["avg_rating"] = pd.to_numeric(df_eff["avg_rating"], errors="coerce")

        st.subheader("Efficiency (Delivery vs Rating)")

        fig4 = px.scatter(df_eff,x="delivery_days",y="avg_rating",size="avg_rating")

        st.plotly_chart(fig4, width='stretch')
        st.divider()

elif section == "Q22 Payment":

    # 22
    query_payment = """
    SELECT 
        payment_method,
        COUNT(*) AS total_transactions
    FROM transactions_master
    GROUP BY payment_method
    ORDER BY total_transactions DESC;
    """
    df_payment = load_data(query_payment)

    st.subheader("Payment Method Preference")

    fig1 = px.pie(df_payment,names="payment_method",values="total_transactions",title="Payment Method Usage")

    st.plotly_chart(fig1, width='stretch')
    st.divider()


    # Transaction Success Rate

    # Success = return_status != 'Returned'

    query_success = """
    SELECT 
        SUM(CASE WHEN return_status != 'Returned' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS success_rate
    FROM transactions_master;
    """
    df_success = load_data(query_success)
    df_success = df_success.astype(float)

    st.subheader("Transaction Success Rate")

    st.metric("Success Rate", f"{df_success['success_rate'][0]:.2f}%")
    st.divider()

    col4,col5,col6=st.columns(3)
    with col4:
        # Payment Trends

        query_trend = """
        SELECT 
            order_year,
            payment_method,
            COUNT(*) AS transactions
        FROM transactions_master
        GROUP BY order_year, payment_method
        ORDER BY order_year;
        """

        df_trend = load_data(query_trend)

        st.subheader("Payment Trends Over Time")

        fig2 = px.line(df_trend,x="order_year",y="transactions",color="payment_method",markers=True)

        st.plotly_chart(fig2, width='stretch')
        st.divider()
    with col5:
        # Revenue by Payment Method

        query_revenue="""
        select payment_method,sum(final_amount_inr) as revenue
        from transactions_master group by payment_method order by revenue desc;
        """
        df_revenue=load_data(query_revenue)
        df_revenue["revenue"]=pd.to_numeric(df_revenue["revenue"],errors="coerce")

        st.subheader("Revenue by Payment Method")

        fig3=px.bar(df_revenue,x="payment_method",y="revenue",title="Revenue Contribution")
        st.plotly_chart(fig3, width='stretch')
        st.divider()

    with col6:
        # Average Order Value by Payment Method
        query_aov = """
        SELECT 
            payment_method,
            AVG(final_amount_inr) AS avg_value
        FROM transactions_master
        GROUP BY payment_method;
        """
        df_aov = load_data(query_aov)
        df_aov["avg_value"] = pd.to_numeric(df_aov["avg_value"], errors="coerce")

        st.subheader("Avg Order Value by Payment Method")

        fig4 = px.bar(df_aov, x="payment_method", y="avg_value")

        st.plotly_chart(fig4, width='stretch')
        st.divider()

elif section == "Q23 Returns":

    st.title("Return Dashboard (Q23)")
    # 23
    query_return_rate = """
    SELECT 
        SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS return_rate
    FROM transactions_master;
    """

    df_return_rate = load_data(query_return_rate)
    df_return_rate = df_return_rate.astype(float)

    st.subheader("Return Rate")

    st.metric("Return %", f"{df_return_rate['return_rate'][0]:.2f}%")
    st.divider()

    # Return Status Breakdown

    query_status = """
    SELECT 
        return_status,
        COUNT(*) AS count
    FROM transactions_master
    GROUP BY return_status;
    """

    df_status = load_data(query_status)

    st.subheader("Return Status Breakdown")

    fig1 = px.pie(df_status, names="return_status", values="count")

    st.plotly_chart(fig1, width='stretch')
    st.divider()

    # Cost Impact of Returns

    query_cost = """
    SELECT 
        SUM(final_amount_inr) AS total_revenue,
        SUM(CASE WHEN return_status = 'Returned' THEN final_amount_inr ELSE 0 END) AS return_loss
    FROM transactions_master;
    """

    df_cost = load_data(query_cost)

    df_cost["total_revenue"] = pd.to_numeric(df_cost["total_revenue"], errors="coerce")
    df_cost["return_loss"] = pd.to_numeric(df_cost["return_loss"], errors="coerce")

    loss_percent = (df_cost["return_loss"][0] / df_cost["total_revenue"][0]) * 100

    col1, col2 = st.columns(2)

    col1.metric("Total Revenue", f"₹ {df_cost['total_revenue'][0]:,.0f}")
    col2.metric("Return Loss", f"₹ {df_cost['return_loss'][0]:,.0f}", f"{loss_percent:.2f}%")
    st.divider()
    col7,col8=st.columns(2)
    with col7:
        # Category-wise Return Analysis

        query_category = """
        SELECT 
            subcategory,
            SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END) AS returns,
            COUNT(*) AS total_orders,
            SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS return_rate
        FROM transactions_master
        GROUP BY subcategory
        ORDER BY return_rate DESC;
        """

        df_cat = load_data(query_category)

        df_cat["return_rate"] = pd.to_numeric(df_cat["return_rate"], errors="coerce")

        fig2 = px.bar(df_cat,x="subcategory",y="return_rate",color="subcategory",title="Subcategory-wise Return Rate")

        st.plotly_chart(fig2, width='stretch')

        st.divider()

    with col8:
        query_product = """
        SELECT 
            product_name,
            SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END) AS returns
        FROM transactions_master
        GROUP BY product_name
        ORDER BY returns DESC
        LIMIT 10;
        """

        df_prod = load_data(query_product)

        st.subheader("Top Returned Products")

        fig3 = px.bar(df_prod, x="product_name", y="returns")

        st.plotly_chart(fig3, width='stretch')
        st.divider()

    # Quality Insight (Rating vs Returns)

    query_quality = """
    SELECT 
        ROUND(product_rating) AS rating,
        SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END) AS returns
    FROM transactions_master
    GROUP BY ROUND(product_rating)
    ORDER BY rating;
    """

    df_quality = load_data(query_quality)

    st.subheader("Rating vs Returns")

    fig4 = px.line(df_quality, x="rating", y="returns", markers=True)

    st.plotly_chart(fig4, width='stretch')
    st.divider()

elif section == "Q24 Customer Service":

    st.title("Customer Service Dashboard (Q24)")
    #24

    query_rating = """
    SELECT 
        AVG(customer_rating) AS avg_rating
    FROM transactions_master;
    """

    df_rating = load_data(query_rating)
    df_rating["avg_rating"] = pd.to_numeric(df_rating["avg_rating"], errors="coerce")

    st.subheader("Customer Satisfaction")

    st.metric("Avg Rating", f"{df_rating['avg_rating'][0]:.2f} / 5")
    st.divider()
    col9,col10=st.columns(2)
    with col9:
        # Satisfaction Distribution

        query_dist = """
        SELECT 
            ROUND(customer_rating) AS rating,
            COUNT(*) AS count
        FROM transactions_master
        GROUP BY ROUND(customer_rating)
        ORDER BY rating;
        """

        df_dist = load_data(query_dist)

        st.subheader("Rating Distribution")

        fig1 = px.bar(df_dist, x="rating", y="count")

        st.plotly_chart(fig1, width='stretch')
        st.divider()
    with col10:
        # Complaint Categories

        query_complaint = """
        SELECT 
            return_status,
            COUNT(*) AS complaints
        FROM transactions_master
        GROUP BY return_status;
        """

        df_complaint = load_data(query_complaint)

        st.subheader("Complaint Categories")

        fig2 = px.pie(df_complaint, names="return_status", values="complaints")

        st.plotly_chart(fig2, width='stretch')
        st.divider()

    # Resolution Time Analysis

    query_resolution = """
    SELECT 
        AVG(delivery_days) AS avg_resolution,
        MAX(delivery_days) AS max_resolution
    FROM transactions_master
    WHERE delivery_days > 0;
    """

    df_res = load_data(query_resolution)
    df_res = df_res.astype(float)

    st.subheader("Resolution Time")

    col1, col2 = st.columns(2)

    col1.metric("Avg Resolution", f"{df_res['avg_resolution'][0]:.2f} days")
    col2.metric("Max Resolution", f"{df_res['max_resolution'][0]:.0f} days")
    st.divider()
    col11,col12=st.columns(2)
    with col11:
        # Service Quality vs Delivery Time

        query_quality = """
        SELECT 
            delivery_days,
            AVG(customer_rating) AS rating
        FROM transactions_master
        GROUP BY delivery_days
        ORDER BY delivery_days;
        """

        df_quality = load_data(query_quality)

        df_quality["delivery_days"] = pd.to_numeric(df_quality["delivery_days"], errors="coerce")
        df_quality["rating"] = pd.to_numeric(df_quality["rating"], errors="coerce")

        st.subheader("Service Quality vs Delivery Time")

        fig3 = px.line(df_quality, x="delivery_days", y="rating", markers=True)

        st.plotly_chart(fig3, width='stretch')
        st.divider()
    with col12:
        # Service Improvement Trend

        query_trend = """
        SELECT 
            order_year,
            AVG(customer_rating) AS rating
        FROM transactions_master
        GROUP BY order_year
        ORDER BY order_year;
        """

        df_trend = load_data(query_trend)

        df_trend["rating"] = pd.to_numeric(df_trend["rating"], errors="coerce")

        st.subheader("Service Improvement Trend")

        fig4 = px.line(df_trend, x="order_year", y="rating", markers=True)

        st.plotly_chart(fig4, width='stretch')
        st.divider()

elif section == "Q25 Supply Chain":
    col13,col14=st.columns(2)
    with col13:
        # 25

        # Supplier Performance (Revenue)

        query_supplier = """
        SELECT 
            brand,
            SUM(final_amount_inr) AS revenue,
            SUM(quantity) AS units_sold
        FROM transactions_master
        GROUP BY brand
        ORDER BY revenue DESC
        LIMIT 10;
        """

        df_supplier = load_data(query_supplier)

        df_supplier["revenue"] = pd.to_numeric(df_supplier["revenue"], errors="coerce")
        df_supplier["units_sold"] = pd.to_numeric(df_supplier["units_sold"], errors="coerce")

        st.subheader("Top Suppliers")

        fig1 = px.bar(df_supplier, x="brand", y="revenue", title="Top Suppliers by Revenue")

        st.plotly_chart(fig1, width='stretch')
        st.divider()
    with col14:
        # Delivery Reliability

        query_delivery = """
        SELECT 
            brand,
            AVG(delivery_days) AS avg_delivery
        FROM transactions_master
        GROUP BY brand
        ORDER BY avg_delivery;
        """

        df_delivery = load_data(query_delivery)
        df_delivery["avg_delivery"] = pd.to_numeric(df_delivery["avg_delivery"], errors="coerce")

        st.subheader("Delivery Reliability")

        fig2 = px.bar(df_delivery, x="brand", y="avg_delivery",title="Avg Delivery Time by Supplier")

        st.plotly_chart(fig2, width='stretch')
        st.divider()
    col15,col16=st.columns(2)
    with col15:
        # Return Rate by Supplier

        query_return = """
        SELECT 
            brand,
            SUM(CASE WHEN return_status = 'Returned' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS return_rate
        FROM transactions_master
        GROUP BY brand
        ORDER BY return_rate DESC;
        """

        df_return = load_data(query_return)
        df_return["return_rate"] = pd.to_numeric(df_return["return_rate"], errors="coerce")

        st.subheader("Return Rate by Supplier")

        fig3 = px.bar(df_return, x="brand", y="return_rate")

        st.plotly_chart(fig3, width='stretch')
        st.divider()
    with col16:
        # Cost Analysis

        query_cost = """
        SELECT 
            brand,
            AVG(original_price_inr) AS cost_price,
            AVG(final_amount_inr) AS selling_price
        FROM transactions_master
        GROUP BY brand;
        """

        df_cost = load_data(query_cost)

        df_cost["cost_price"] = pd.to_numeric(df_cost["cost_price"], errors="coerce")
        df_cost["selling_price"] = pd.to_numeric(df_cost["selling_price"], errors="coerce")

        st.subheader("Cost vs Selling Price")

        fig4 = px.scatter(df_cost,x="cost_price",y="selling_price",size="selling_price",hover_name="brand",title="Cost vs Selling Price")

        st.plotly_chart(fig4, width='stretch')
        st.divider()

    # Vendor Efficiency

    query_eff = """
    SELECT 
        brand,
        AVG(delivery_days) AS delivery_time,
        AVG(product_rating) AS rating
    FROM transactions_master
    GROUP BY brand;
    """

    df_eff = load_data(query_eff)

    df_eff["delivery_time"] = pd.to_numeric(df_eff["delivery_time"], errors="coerce")
    df_eff["rating"] = pd.to_numeric(df_eff["rating"], errors="coerce")

    st.subheader("Supplier Efficiency")

    fig5 = px.scatter(df_eff,x="delivery_time",y="rating",size="rating",hover_name="brand",title="Delivery vs Rating")

    st.plotly_chart(fig5, width='stretch')
    st.divider()

    total_suppliers = df_supplier["brand"].nunique()
    avg_delivery = df_delivery["avg_delivery"].mean()
    avg_return = df_return["return_rate"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric("Suppliers", total_suppliers)
    col2.metric("Avg Delivery", f"{avg_delivery:.2f} days")
    col3.metric("Avg Return %", f"{avg_return:.2f}%")
    st.divider()
