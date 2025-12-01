import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings("ignore")

# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .feature-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    """Load all processed data"""
    try:
        transactions = pd.read_csv("../data/processed/enriched_transactions.csv")
        customers = pd.read_csv("../data/processed/customers_clean.csv")
        products = pd.read_csv("../data/processed/products_clean.csv")
        customer_features = pd.read_csv(
            "../data/processed/customer_features_engineered.csv"
        )
        product_features = pd.read_csv(
            "../data/processed/product_features_engineered.csv"
        )
        monthly_sales = pd.read_csv("../data/processed/monthly_sales.csv")

        # Convert date columns
        transactions["date"] = pd.to_datetime(transactions["date"])
        customers["signup_date"] = pd.to_datetime(customers["signup_date"])

        return (
            transactions,
            customers,
            products,
            customer_features,
            product_features,
            monthly_sales,
        )
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None, None, None


def calculate_kpis(transactions, customers, products):
    """Calculate key performance indicators"""
    total_revenue = transactions["revenue"].sum()
    total_profit = transactions["profit"].sum()
    total_customers = customers["customer_id"].nunique()
    total_products = products["product_id"].nunique()
    avg_transaction_value = transactions["revenue"].mean()

    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_customers": total_customers,
        "total_products": total_products,
        "avg_transaction_value": avg_transaction_value,
    }


def create_overview_tab(transactions, customers, products, kpis):
    """Create overview tab with KPIs and high-level insights"""

    st.header("📈 Business Overview")

    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Total Revenue",
            f"${kpis['total_revenue']:,.0f}",
            help="Sum of all transaction revenues",
        )

    with col2:
        st.metric(
            "Total Profit",
            f"${kpis['total_profit']:,.0f}",
            help="Sum of all transaction profits",
        )

    with col3:
        st.metric(
            "Total Customers",
            f"{kpis['total_customers']:,}",
            help="Number of unique customers",
        )

    with col4:
        st.metric(
            "Total Products",
            f"{kpis['total_products']:,}",
            help="Number of unique products",
        )

    with col5:
        st.metric(
            "Avg Transaction",
            f"${kpis['avg_transaction_value']:.2f}",
            help="Average revenue per transaction",
        )

    # Revenue Trends and Distribution
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Monthly Revenue Trend")

        # Create monthly revenue data
        monthly_revenue = (
            transactions.groupby(transactions["date"].dt.to_period("M"))["revenue"]
            .sum()
            .reset_index()
        )
        monthly_revenue["date"] = monthly_revenue["date"].astype(str)

        fig = px.line(
            monthly_revenue,
            x="date",
            y="revenue",
            title="Monthly Revenue Trend",
            labels={"date": "Month", "revenue": "Revenue ($)"},
        )
        fig.update_traces(line=dict(color="#1f77b4", width=3))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Revenue by Category")

        category_revenue = (
            transactions.groupby("category")["revenue"]
            .sum()
            .sort_values(ascending=False)
        )

        fig = px.pie(
            values=category_revenue.values,
            names=category_revenue.index,
            title="Revenue Distribution by Category",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Top Products and Customer Segments
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Products by Revenue")

        top_products = (
            transactions.groupby(["product_name", "category"])["revenue"]
            .sum()
            .nlargest(10)
            .reset_index()
        )

        fig = px.bar(
            top_products,
            y="product_name",
            x="revenue",
            color="category",
            orientation="h",
            title="Top 10 Products by Revenue",
            labels={"revenue": "Revenue ($)", "product_name": "Product"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Customer Tier Performance")

        tier_performance = (
            transactions.groupby("customer_tier")
            .agg({"revenue": "sum", "customer_id": "nunique"})
            .reset_index()
        )
        tier_performance["revenue_per_customer"] = (
            tier_performance["revenue"] / tier_performance["customer_id"]
        )

        fig = px.bar(
            tier_performance,
            x="customer_tier",
            y="revenue_per_customer",
            color="customer_tier",
            title="Revenue per Customer by Tier",
            labels={
                "revenue_per_customer": "Revenue per Customer ($)",
                "customer_tier": "Customer Tier",
            },
        )
        st.plotly_chart(fig, use_container_width=True)


def create_customer_analytics_tab(customer_features, transactions):
    """Create customer analytics tab"""

    st.header("👥 Customer Analytics")

    # Customer Segmentation
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Segments Distribution")

        segment_dist = customer_features["customer_segment"].value_counts()

        fig = px.pie(
            values=segment_dist.values,
            names=segment_dist.index,
            title="Customer Segments Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Customer Value Tiers")

        value_tier_dist = customer_features["value_tier"].value_counts()

        fig = px.bar(
            x=value_tier_dist.index,
            y=value_tier_dist.values,
            color=value_tier_dist.index,
            title="Customer Value Tiers Distribution",
            labels={"x": "Value Tier", "y": "Number of Customers"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # RFM Analysis
    st.subheader("RFM Analysis")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Recency distribution
        fig = px.histogram(
            customer_features,
            x="days_since_last_purchase",
            nbins=20,
            title="Customer Recency Distribution",
            labels={"days_since_last_purchase": "Days Since Last Purchase"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Frequency distribution
        fig = px.histogram(
            customer_features,
            x="transaction_count",
            nbins=20,
            title="Purchase Frequency Distribution",
            labels={"transaction_count": "Number of Transactions"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        # Monetary distribution
        fig = px.histogram(
            customer_features,
            x="total_revenue",
            nbins=20,
            title="Customer Lifetime Value Distribution",
            labels={"total_revenue": "Total Revenue ($)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # Customer Behavior Insights
    st.subheader("Customer Behavior Insights")

    # Top segments by average revenue
    segment_performance = (
        customer_features.groupby("customer_segment")
        .agg(
            {
                "total_revenue": "mean",
                "transaction_count": "mean",
                "purchase_frequency": "mean",
            }
        )
        .round(2)
        .reset_index()
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            segment_performance,
            x="customer_segment",
            y="total_revenue",
            color="customer_segment",
            title="Average Revenue by Customer Segment",
            labels={
                "total_revenue": "Average Revenue ($)",
                "customer_segment": "Customer Segment",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.scatter(
            customer_features,
            x="transaction_count",
            y="total_revenue",
            color="customer_segment",
            size="total_revenue",
            title="Transaction Count vs Total Revenue",
            labels={
                "transaction_count": "Number of Transactions",
                "total_revenue": "Total Revenue ($)",
            },
        )
        st.plotly_chart(fig, use_container_width=True)


def create_product_analytics_tab(product_features, transactions):
    """Create product analytics tab"""

    st.header("📦 Product Analytics")

    # Product Performance Overview
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Product Performance Tiers")

        performance_tier_dist = product_features["performance_tier"].value_counts()

        fig = px.pie(
            values=performance_tier_dist.values,
            names=performance_tier_dist.index,
            title="Product Performance Tiers Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Price Segments Performance")

        price_segment_perf = (
            product_features.groupby("price_segment")
            .agg({"total_revenue": "sum", "total_quantity": "sum"})
            .reset_index()
        )

        fig = px.bar(
            price_segment_perf,
            x="price_segment",
            y="total_revenue",
            color="price_segment",
            title="Revenue by Price Segment",
            labels={
                "total_revenue": "Total Revenue ($)",
                "price_segment": "Price Segment",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    # Top Products Analysis
    st.subheader("Top Performing Products")

    # Let user select metric for top products
    metric_options = {
        "total_revenue": "Total Revenue",
        "total_quantity": "Total Quantity Sold",
        "popularity_score": "Popularity Score",
        "profit_margin_actual": "Profit Margin",
    }

    selected_metric = st.selectbox(
        "Select metric for ranking:",
        options=list(metric_options.keys()),
        format_func=lambda x: metric_options[x],
    )

    top_n = st.slider("Number of top products to show:", 5, 20, 10)

    top_products = product_features.nlargest(top_n, selected_metric)[
        [
            "product_name",
            "category",
            "price_segment",
            "total_revenue",
            "total_quantity",
            "popularity_score",
            "profit_margin_actual",
        ]
    ]

    # Display top products table
    st.dataframe(
        top_products.style.format(
            {
                "total_revenue": "${:,.2f}",
                "profit_margin_actual": "{:.2f}%",
                "popularity_score": "{:.2f}",
            }
        ).background_gradient(subset=["total_revenue", "popularity_score"]),
        use_container_width=True,
    )

    # Product Category Analysis
    st.subheader("Category Performance Analysis")

    col1, col2 = st.columns(2)

    with col1:
        category_performance = (
            transactions.groupby("category")
            .agg({"revenue": "sum", "profit": "sum", "quantity": "sum"})
            .reset_index()
        )
        category_performance["profit_margin"] = (
            category_performance["profit"] / category_performance["revenue"]
        ) * 100

        fig = px.bar(
            category_performance,
            x="category",
            y="profit_margin",
            color="category",
            title="Profit Margin by Category",
            labels={"profit_margin": "Profit Margin (%)", "category": "Category"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Revenue vs Quantity scatter
        fig = px.scatter(
            product_features,
            x="total_quantity",
            y="total_revenue",
            color="category",
            size="price",
            hover_data=["product_name"],
            title="Revenue vs Quantity Sold",
            labels={
                "total_quantity": "Total Quantity Sold",
                "total_revenue": "Total Revenue ($)",
            },
        )
        st.plotly_chart(fig, use_container_width=True)


def create_geographic_analytics_tab(transactions):
    """Create geographic analytics tab"""

    st.header("🌎 Geographic Analytics")

    # Regional Performance
    regional_performance = (
        transactions.groupby("region")
        .agg(
            {
                "revenue": "sum",
                "profit": "sum",
                "transaction_id": "count",
                "customer_id": "nunique",
                "quantity": "sum",
            }
        )
        .reset_index()
    )

    regional_performance["revenue_per_customer"] = (
        regional_performance["revenue"] / regional_performance["customer_id"]
    )
    regional_performance["avg_transaction_value"] = (
        regional_performance["revenue"] / regional_performance["transaction_id"]
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by Region")

        fig = px.bar(
            regional_performance,
            x="region",
            y="revenue",
            color="region",
            title="Total Revenue by Region",
            labels={"revenue": "Total Revenue ($)", "region": "Region"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Customer Distribution by Region")

        fig = px.pie(
            regional_performance,
            values="customer_id",
            names="region",
            title="Customer Distribution by Region",
        )
        st.plotly_chart(fig, use_container_width=True)

    # Regional Efficiency Metrics
    st.subheader("Regional Efficiency Metrics")

    metrics_to_show = st.multiselect(
        "Select metrics to compare:",
        options=[
            "revenue",
            "profit",
            "transaction_id",
            "customer_id",
            "revenue_per_customer",
            "avg_transaction_value",
        ],
        default=["revenue", "profit", "customer_id"],
        format_func=lambda x: {
            "revenue": "Total Revenue",
            "profit": "Total Profit",
            "transaction_id": "Transaction Count",
            "customer_id": "Customer Count",
            "revenue_per_customer": "Revenue per Customer",
            "avg_transaction_value": "Avg Transaction Value",
        }[x],
    )

    if metrics_to_show:
        # Create subplots for selected metrics
        fig = make_subplots(
            rows=1,
            cols=len(metrics_to_show),
            subplot_titles=[
                {
                    "revenue": "Total Revenue",
                    "profit": "Total Profit",
                    "transaction_id": "Transaction Count",
                    "customer_id": "Customer Count",
                    "revenue_per_customer": "Revenue per Customer",
                    "avg_transaction_value": "Avg Transaction Value",
                }[metric]
                for metric in metrics_to_show
            ],
        )

        for i, metric in enumerate(metrics_to_show, 1):
            fig.add_trace(
                go.Bar(
                    x=regional_performance["region"],
                    y=regional_performance[metric],
                    name=metric,
                    marker_color=px.colors.qualitative.Set1[i - 1],
                ),
                row=1,
                col=i,
            )

        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Regional Performance Table
    st.subheader("Regional Performance Details")

    display_regional = regional_performance.copy()
    display_regional = display_regional.round(2)

    st.dataframe(
        display_regional.style.format(
            {
                "revenue": "${:,.2f}",
                "profit": "${:,.2f}",
                "revenue_per_customer": "${:,.2f}",
                "avg_transaction_value": "${:,.2f}",
            }
        ).background_gradient(subset=["revenue", "profit", "revenue_per_customer"]),
        use_container_width=True,
    )


def create_feature_analytics_tab():
    """Create feature engineering analytics tab"""

    st.header("🔧 Feature Engineering Insights")

    try:
        # Load engineered features
        feature_importance = pd.read_csv("../data/processed/feature_importance.csv")
        ml_features = pd.read_csv("../data/processed/ml_ready_features.csv")

        st.subheader("Feature Importance for Customer Value Prediction")

        # Show top features
        top_n = st.slider("Number of top features to show:", 5, 20, 10)
        top_features = feature_importance.head(top_n)

        fig = px.bar(
            top_features,
            x="importance",
            y="feature",
            orientation="h",
            title=f"Top {top_n} Most Important Features",
            labels={"importance": "Absolute Correlation", "feature": "Feature"},
        )
        st.plotly_chart(fig, use_container_width=True)

        # Feature distributions
        st.subheader("Feature Distributions")

        # Select features to visualize
        available_features = ml_features.select_dtypes(
            include=[np.number]
        ).columns.tolist()
        available_features = [
            f
            for f in available_features
            if f not in ["customer_id", "is_high_value", "churn_risk"]
        ]

        selected_features = st.multiselect(
            "Select features to visualize distributions:",
            options=available_features,
            default=(
                available_features[:3]
                if len(available_features) >= 3
                else available_features
            ),
        )

        if selected_features:
            col1, col2 = st.columns(2)

            with col1:
                # Histograms
                fig = px.histogram(
                    ml_features,
                    x=selected_features[0],
                    title=f"Distribution of {selected_features[0]}",
                    nbins=20,
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                if len(selected_features) > 1:
                    # Box plot
                    fig = px.box(
                        ml_features,
                        y=selected_features[1],
                        title=f"Box Plot of {selected_features[1]}",
                    )
                    st.plotly_chart(fig, use_container_width=True)

        # Correlation heatmap
        st.subheader("Feature Correlation Heatmap")

        # Select features for correlation
        corr_features = st.multiselect(
            "Select features for correlation analysis:",
            options=available_features,
            default=(
                available_features[:8]
                if len(available_features) >= 8
                else available_features
            ),
        )

        if len(corr_features) > 1:
            corr_matrix = ml_features[corr_features].corr()

            fig = px.imshow(
                corr_matrix,
                title="Feature Correlation Heatmap",
                aspect="auto",
                color_continuous_scale="RdBu_r",
            )
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading feature data: {e}")
        st.info(
            "Please run the feature engineering notebook first to generate the feature data."
        )


def create_insights_tab(transactions, customer_features, product_features):
    """Create business insights and recommendations tab"""

    st.header("💡 Business Insights & Recommendations")

    # Executive Summary
    st.subheader("📊 Executive Summary")

    total_revenue = transactions["revenue"].sum()
    total_customers = customer_features["customer_id"].nunique()
    avg_customer_value = customer_features["total_revenue"].mean()
    top_category = transactions.groupby("category")["revenue"].sum().idxmax()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Business Value", f"${total_revenue:,.0f}")

    with col2:
        st.metric("Customer Base", f"{total_customers:,}")

    with col3:
        st.metric("Avg Customer Value", f"${avg_customer_value:.2f}")

    with col4:
        st.metric("Top Category", top_category)

    # Key Insights
    st.subheader("🎯 Key Business Insights")

    insights = [
        {
            "title": "Customer Segmentation Opportunities",
            "content": f"• {customer_features[customer_features['customer_segment'] == 'Champions'].shape[0]} Champion customers driving significant revenue\n"
            f"• {customer_features[customer_features['customer_segment'] == 'At Risk'].shape[0]} customers at risk of churn\n"
            f"• Focus on Loyal Customers and Potential Loyalists for growth",
        },
        {
            "title": "Product Performance Highlights",
            "content": f"• {product_features[product_features['performance_tier'] == 'Premium'].shape[0]} premium products generating top revenue\n"
            f"• {product_features[product_features['popularity_score'] > 80].shape[0]} high-popularity products\n"
            f"• Opportunity to optimize underperforming product categories",
        },
        {
            "title": "Geographic Expansion Potential",
            "content": "• Identify regions with highest revenue per customer\n"
            "• Target underperforming regions with marketing campaigns\n"
            "• Optimize regional inventory based on demand patterns",
        },
        {
            "title": "Seasonal & Temporal Patterns",
            "content": "• Analyze peak shopping seasons and days\n"
            "• Optimize marketing spend based on temporal patterns\n"
            "• Plan inventory for seasonal demand fluctuations",
        },
    ]

    for insight in insights:
        with st.expander(insight["title"]):
            st.write(insight["content"])

    # Actionable Recommendations
    st.subheader("🚀 Strategic Recommendations")

    recommendations = [
        {
            "area": "Customer Retention & Growth",
            "actions": [
                "Implement loyalty programs for Champion customers",
                "Create targeted campaigns for At Risk customers",
                "Develop onboarding programs for New Customers",
                "Personalize marketing for each customer segment",
            ],
        },
        {
            "area": "Product Strategy",
            "actions": [
                "Promote high-margin products more aggressively",
                "Review pricing for low-performing categories",
                "Expand product offerings in top categories",
                "Optimize inventory based on sales velocity",
            ],
        },
        {
            "area": "Geographic Optimization",
            "actions": [
                "Increase marketing in high-potential regions",
                "Optimize shipping and logistics by region",
                "Develop region-specific product assortments",
                "Analyze regional customer preferences",
            ],
        },
        {
            "area": "Operational Efficiency",
            "actions": [
                "Leverage temporal patterns for staffing",
                "Optimize marketing spend based on seasonal trends",
                "Implement predictive inventory management",
                "Develop cross-selling strategies",
            ],
        },
    ]

    for rec in recommendations:
        st.write(f"**{rec['area']}:**")
        for action in rec["actions"]:
            st.write(f"• {action}")
        st.write("")


def main():
    """Main dashboard function"""

    # Title and description
    st.markdown(
        '<h1 class="main-header">🏪 E-commerce Analytics Dashboard</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Comprehensive business intelligence and analytics for e-commerce performance monitoring"
    )

    # Load data
    with st.spinner("Loading data..."):
        data = load_data()

    if data[0] is None:
        st.error(
            "Failed to load data. Please ensure the data processing pipeline has been run."
        )
        return

    (
        transactions,
        customers,
        products,
        customer_features,
        product_features,
        monthly_sales,
    ) = data

    # Calculate KPIs
    kpis = calculate_kpis(transactions, customers, products)

    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "📈 Overview",
            "👥 Customer Analytics",
            "📦 Product Analytics",
            "🌎 Geographic Analytics",
            "🔧 Feature Insights",
            "💡 Recommendations",
        ]
    )

    with tab1:
        create_overview_tab(transactions, customers, products, kpis)

    with tab2:
        create_customer_analytics_tab(customer_features, transactions)

    with tab3:
        create_product_analytics_tab(product_features, transactions)

    with tab4:
        create_geographic_analytics_tab(transactions)

    with tab5:
        create_feature_analytics_tab()

    with tab6:
        create_insights_tab(transactions, customer_features, product_features)

    # Footer
    st.markdown("---")
    st.markdown(
        "**E-commerce Analytics Dashboard** | "
        "Built with Streamlit | "
        "Data Engineering Portfolio Project"
    )


if __name__ == "__main__":
    main()
