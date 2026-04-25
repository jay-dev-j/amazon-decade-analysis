import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px

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

st.set_page_config(page_title="Customer Dashboard", layout="wide")

st.title("Customer Segmentation Dashboard")

section = st.sidebar.radio("Select Section", [
    "Q11 Segmentation",
    "Q12 Journey",
    "Q13 Prime",
    "Q14 Retention",
    "Q15 Demographics"
])
if section == "Q11 Segmentation":
    col1,col2=st.columns(2)
    # 11
    # RFM QUERY
    query_rfm = """
    select 
        customer_id,
        max(order_date) as last_purchase,
        count(*) as frequency,
        sum(final_amount_inr) as monetary
    from transactions_master
    group by customer_id;
    """

    if "df_rfm" not in st.session_state:
        st.session_state.df_rfm = load_data(query_rfm)

    df_rfm = st.session_state.df_rfm
    df_rfm['monetary'] = df_rfm['monetary'].astype(float)


    # recency calculation
    df_rfm['last_purchase'] = pd.to_datetime(df_rfm['last_purchase'])

    today = pd.Timestamp.today()

    df_rfm['recency'] = (today - df_rfm['last_purchase']).dt.days

    # rfm chart
    with col1:
        st.header("RFM analysis")

        fig1 = px.scatter(df_rfm,x="recency",y="monetary",size="frequency",title="RFM distribution")

        st.plotly_chart(fig1, width="stretch", key="rfm_chart")
        st.divider()
    with col2:
        # customer segments

        st.header("customer segments")

        df_rfm['segment'] = pd.qcut(
            df_rfm['monetary'],
            4,
            labels=["low", "medium", "high", "vip"]
        )

        fig3 = px.pie(df_rfm, names="segment", title="customer segments")
        st.plotly_chart(fig3, width="stretch", key="segment_chart")
        st.divider()

    # lifetime value

    st.header("Customer lifetime value")

    fig3 = px.histogram(df_rfm,x="monetary",title="ClV distribution")

    st.plotly_chart(fig3, width="stretch",key="clv_chart")
    st.subheader("recommendations")

    st.info("vip customers → premium offers")
    st.info("low customers → discounts")
    st.divider()
elif section == "Q12 Journey":
    col3,col4=st.columns(2)
    with col3:
        # 12
        # acquisition channels
        st.subheader("acquisition channels")

        query_channel = """
        select payment_method, count(*) as orders
        from transactions_master
        group by payment_method;
        """

        df_channel = load_data(query_channel)

        fig1 = px.pie(df_channel, names="payment_method", values="orders",title="Customer acquisition channels")

        st.plotly_chart(fig1, width="stretch",key="journey_chart")

        st.divider()
    with col4:
        # purchase patterns

        st.subheader("purchase patterns")

        query_pattern = """
        select order_month, sum(final_amount_inr) as revenue
        from transactions_master
        group by order_month
        order by order_month;
        """

        df_pattern = load_data(query_pattern)

        fig2 = px.line(df_pattern, x="order_month", y="revenue",title="Monthly purchase pattern")

        st.plotly_chart(fig2, width="stretch",key="pattern_chart")

        st.divider()
    col5,col6=st.columns(2)
    with col5:
        # category transitions

        st.subheader("Category behavior")

        query_cat = """
        select subcategory, count(*) as orders
        from transactions_master
        group by subcategory
        order by orders desc;
        """

        df_cat = load_data(query_cat)

        fig3 = px.bar(df_cat, x="subcategory", y="orders",title="Category transitions")

        st.plotly_chart(fig3, width="stretch",key="category_chart")
        st.divider()
    with col6:
        # customer evolution

        st.subheader("Customer evolution")

        query_customer = """
        select customer_id, count(*) as orders
        from transactions_master
        group by customer_id;
        """

        df_customer = load_data(query_customer)

        df_customer['type'] = pd.cut(
            df_customer['orders'],
            bins=[0, 2, 6, df_customer['orders'].max()],
            labels=["new", "repeat", "loyal"]
        )
        fig4 = px.pie(df_customer, names="type",title="Customer journey stages")

        st.plotly_chart(fig4, width="stretch",key="evolution_chart")

        st.divider()
elif section == "Q13 Prime":
    col7,col8=st.columns(2)
    with col7:
        ## 13
        # prime vs non prime revenue
        query_prime = """
        select is_prime_member, sum(final_amount_inr) as revenue
        from transactions_master
        group by is_prime_member;
        """

        df_prime = load_data(query_prime)

        df_prime['revenue'] = df_prime['revenue'].astype(float)

        df_prime['type'] = df_prime['is_prime_member'].map({
            1: "prime",
            0: "non-prime"
        })

        fig1 = px.bar(df_prime, x="type", y="revenue",title="prime vs non-prime revenue")
        st.plotly_chart(fig1, width="stretch", key="prime_revenue")
    with col8:
        # oreder behaviour

        query_orders = """
        select is_prime_member, count(*) as orders
        from transactions_master
        group by is_prime_member;
        """

        df_orders = load_data(query_orders)

        df_orders['orders'] = df_orders['orders'].astype(float)

        df_orders['type'] = df_orders['is_prime_member'].map({
            1: "prime",
            0: "non-prime"
        })

        fig2 = px.pie(df_orders, names="type", values="orders",title="order distribution")
        st.plotly_chart(fig2, width="stretch", key="prime_orders")
    col9,col10=st.columns(2)
    with col9:
        # average order value

        query_aov = """
        select is_prime_member, avg(final_amount_inr) as avg_value
        from transactions_master
        group by is_prime_member;
        """

        df_aov = load_data(query_aov)

        df_aov['avg_value'] = df_aov['avg_value'].astype(float)

        df_aov['type'] = df_aov['is_prime_member'].map({
            1: "prime",
            0: "non-prime"
        })

        fig3 = px.bar(df_aov, x="type", y="avg_value",title="average order value")

        st.plotly_chart(fig3, width="stretch", key="prime_aov")
        st.divider()
    st.subheader("insights")

    st.info("prime users generate higher revenue")
    st.info("prime users have better retention")
    st.divider()
        
    with col10:
        # retenation

        query_retention = """
        select customer_id, is_prime_member, count(*) as orders
        from transactions_master
        group by customer_id, is_prime_member;
        """

        df_retention = load_data(query_retention)

        df_retention['type'] = df_retention['is_prime_member'].map({
            1: "prime",
            0: "non-prime"
        })

        df_retention['segment'] = df_retention['orders'].apply(lambda x: "repeat" if x > 1 else "new")

        fig4 = px.histogram(df_retention, x="type", color="segment",barmode="group",title="retention comparison")

        st.plotly_chart(fig4, width="stretch", key="prime_retention")

        st.divider() 
elif section == "Q14 Retention":

    #14
    # Cohort Analysis (Customer by First Purchase Year)
    col11,col12=st.columns(2)
    query_cohort = """
    select customer_id, min(order_year) as first_year
    from transactions_master
    group by customer_id;
    """

    df_cohort = load_data(query_cohort)
    with col11:
        fig1 = px.histogram(df_cohort, x="first_year",title="customer acquisition cohorts")

        st.plotly_chart(fig1, width="stretch", key="cohort_chart")

    # Retention Trend (Repeat Customers)

    query_repeat = """
    select order_year, count(distinct customer_id) as customers
    from transactions_master
    group by order_year
    order by order_year;
    """

    df_repeat = load_data(query_repeat)
    with col12:
        fig2 = px.line(df_repeat, x="order_year", y="customers",title="customer retention trend")

        st.plotly_chart(fig2, width="stretch", key="retention_trend")
    col13,col14=st.columns(2)
    # Churn Analysis
    # churn = customers who purchased only once

    query_churn = """
    select customer_id, count(*) as orders
    from transactions_master
    group by customer_id;
    """

    df_churn = load_data(query_churn)

    df_churn['type'] = df_churn['orders'].apply(
        lambda x: "churned" if x == 1 else "retained"
    )
    with col13:
        fig3 = px.pie(df_churn, names="type",title="churn vs retained customers")

        st.plotly_chart(fig3, width="stretch", key="churn_chart")
        st.divider()
    # Retention Effectiveness
    query_effect = """
    select order_year, avg(final_amount_inr) as avg_value
    from transactions_master
    group by order_year
    order by order_year;
    """

    df_effect = load_data(query_effect)

    df_effect['avg_value'] = df_effect['avg_value'].astype(float)
    with col14:
        fig4 = px.bar(df_effect, x="order_year", y="avg_value",title="retention effectiveness (avg spend)")

        st.plotly_chart(fig4, width="stretch", key="retention_effect")

    # customer life cycle

    query_lifecycle = """
    select customer_id, count(*) as orders
    from transactions_master
    group by customer_id;
    """

    df_life = load_data(query_lifecycle)

    df_life['stage'] = pd.cut(
        df_life['orders'],
        bins=[0, 2, 5, df_life['orders'].max()],
        labels=["new", "growing", "loyal"]
    )

    fig5 = px.pie(df_life, names="stage",title="customer lifecycle stages")

    st.plotly_chart(fig5, width="stretch", key="lifecycle_chart")
    
    st.subheader("retention insights")
    st.info("reduce churn with offers")
    st.info("engage new customers early")
    st.divider() 
elif section == "Q15 Demographics":
    col15,col16=st.columns(2)
    # AGE ANALYSIS
    with col15:
        st.subheader("Age Group Preferences")

        query_age = """
        select customer_age_group, sum(final_amount_inr) as revenue
        from transactions_master
        group by customer_age_group;
        """

        df_age = load_data(query_age)
        df_age['revenue'] = df_age['revenue'].astype(float)
    
        fig_age = px.bar(df_age,x="customer_age_group",y="revenue",title="Age Group Preferences")

        st.plotly_chart(fig_age, width="stretch", key="age_chart")

        st.divider()
    with col16:
        # SPENDING PATTERN
        st.subheader("Spending Patterns")

        query_spend = """
        select order_month, sum(final_amount_inr) as revenue
        from transactions_master
        group by order_month
        order by order_month;
        """

        df_spend = load_data(query_spend)
        df_spend['revenue'] = df_spend['revenue'].astype(float)
    
        fig2 = px.line(df_spend, x="order_month", y="revenue",title="Monthly Spending Pattern")

        st.plotly_chart(fig2, width="stretch", key="spend_chart")

        st.divider()
    col17,col18=st.columns(2)
    with col17:

        # GEOGRAPHIC BEHAVIOR
        st.subheader("Geographic Behavior")

        query_geo = """
        select customer_state, sum(final_amount_inr) as revenue
        from transactions_master
        group by customer_state
        order by revenue desc;
        """

        df_geo = load_data(query_geo)
        df_geo['revenue'] = df_geo['revenue'].astype(float)
        fig3 = px.bar(df_geo, x="customer_state", y="revenue",title="State-wise Revenue")

        st.plotly_chart(fig3, width="stretch", key="geo_chart")

        st.divider()
    with col18:
        # CATEGORY PREFERENCES
        st.subheader("Category Preferences")

        query_cat = """
        select subcategory, sum(final_amount_inr) as revenue
        from transactions_master
        group by subcategory
        order by revenue desc;
        """

        df_cat = load_data(query_cat)
        df_cat['revenue'] = df_cat['revenue'].astype(float)
    
        fig4 = px.bar(df_cat, x="subcategory", y="revenue",title="Category Preferences")

        st.plotly_chart(fig4, width="stretch", key="demo_cat_chart")

        st.divider()

    # INSIGHTS (VERY IMPORTANT)
    st.subheader("Insights")

    st.info("young customers contribute more revenue")
    st.info("sales vary across months")
    st.info("top states drive business growth")
    st.info("popular categories influence marketing strategy")

