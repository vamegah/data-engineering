import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import sys
import os
from datetime import datetime

# Add shared modules to path

# project_root = os.path.abspath(os.path.join(os.getcwd(), "../.."))
# if project_root not in sys.path:
#     sys.path.insert(0, project_root)
# from shared.config.database import DatabaseConfig
# from shared.utils.helpers import VisualizationHelper

# Page configuration
st.set_page_config(
    page_title="Banking Churn Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .risk-high {
        color: #ff4b4b;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffa500;
        font-weight: bold;
    }
    .risk-low {
        color: #00cc96;
        font-weight: bold;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Title and description
st.markdown(
    '<h1 class="main-header">🏦 Banking Customer Churn Analytics</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    "Monitor customer behavior, predict churn, and take proactive actions to retain customers"
)


@st.cache_data
def load_data():
    """Load processed data"""
    try:
        customers = pd.read_csv("../data/processed/banking_customers_clean.csv")
        transactions = pd.read_csv("../data/processed/banking_transactions_clean.csv")
        return customers, transactions
    except:
        st.error("❌ Could not load data. Please run the ETL pipeline first.")
        return None, None


@st.cache_resource
def load_model():
    """Load trained ML model"""
    try:
        model_data = joblib.load("../models/churn_model.pkl")
        return model_data
    except:
        st.warning("⚠️ ML model not found. Please train the model first.")
        return None


# Load data and model
customers, transactions = load_data()
model_data = load_model()

# Sidebar
st.sidebar.header("🔧 Filters and Controls")

if customers is not None:
    # Country filter
    countries = ["All"] + sorted(customers["country"].unique().tolist())
    selected_country = st.sidebar.selectbox("Select Country", countries)

    # Age range filter
    min_age, max_age = int(customers["age"].min()), int(customers["age"].max())
    age_range = st.sidebar.slider("Age Range", min_age, max_age, (min_age, max_age))

    # Balance range filter
    min_balance, max_balance = int(customers["balance"].min()), int(
        customers["balance"].max()
    )
    balance_range = st.sidebar.slider(
        "Balance Range ($)",
        min_balance,
        max_balance,
        (min_balance, max_balance),
        step=1000,
    )

    # Apply filters
    filtered_customers = customers.copy()
    if selected_country != "All":
        filtered_customers = filtered_customers[
            filtered_customers["country"] == selected_country
        ]
    filtered_customers = filtered_customers[
        (filtered_customers["age"] >= age_range[0])
        & (filtered_customers["age"] <= age_range[1])
        & (filtered_customers["balance"] >= balance_range[0])
        & (filtered_customers["balance"] <= balance_range[1])
    ]

# Main content
if customers is not None:
    st.header("📊 Key Performance Indicators")

    # KPIs
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_customers = len(filtered_customers)
        st.metric("Total Customers", f"{total_customers:,}")

    with col2:
        churn_rate = filtered_customers["churn"].mean()
        st.metric("Churn Rate", f"{churn_rate:.2%}")

    with col3:
        avg_balance = filtered_customers["balance"].mean()
        st.metric("Average Balance", f"${avg_balance:,.2f}")

    with col4:
        avg_credit_score = filtered_customers["credit_score"].mean()
        st.metric("Avg Credit Score", f"{avg_credit_score:.0f}")

    # Additional KPIs
    col5, col6, col7, col8 = st.columns(4)

    with col5:
        active_members = filtered_customers["active_member"].mean()
        st.metric("Active Members", f"{active_members:.2%}")

    with col6:
        avg_products = filtered_customers["products_number"].mean()
        st.metric("Avg Products/Customer", f"{avg_products:.1f}")

    with col7:
        total_balance = filtered_customers["balance"].sum()
        st.metric("Total Balance", f"${total_balance:,.0f}")

    with col8:
        high_risk = len(filtered_customers[filtered_customers["churn"] == 1])
        st.metric("Churned Customers", f"{high_risk}")

    # Charts and Analysis
    st.header("📈 Customer Analytics")

    # Create tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Churn Analysis",
            "Customer Segments",
            "Transaction Patterns",
            "Churn Prediction",
            "Business Impact",
        ]
    )

    with tab1:
        st.subheader("Churn Rate Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Churn by country
            country_churn = (
                filtered_customers.groupby("country")["churn"]
                .mean()
                .sort_values(ascending=False)
            )
            fig = px.bar(
                country_churn,
                title="Churn Rate by Country",
                labels={"value": "Churn Rate", "country": "Country"},
                color=country_churn.values,
                color_continuous_scale="Reds",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Churn by products
            product_churn = filtered_customers.groupby("products_number")[
                "churn"
            ].mean()
            fig = px.line(
                product_churn,
                title="Churn Rate by Number of Products",
                labels={"value": "Churn Rate", "products_number": "Number of Products"},
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)

        # Correlation heatmap
        st.subheader("Feature Correlation with Churn")
        numerical_cols = [
            "credit_score",
            "age",
            "balance",
            "estimated_salary",
            "tenure",
            "products_number",
            "txn_count",
            "churn",
        ]
        corr_matrix = filtered_customers[numerical_cols].corr()

        fig = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            title="Correlation Matrix",
            color_continuous_scale="RdBu_r",
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Customer Segmentation")

        col1, col2 = st.columns(2)

        with col1:
            # Age distribution by churn
            fig = px.histogram(
                filtered_customers,
                x="age",
                color="churn",
                barmode="overlay",
                title="Age Distribution by Churn Status",
                opacity=0.7,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Balance vs Credit Score
            fig = px.scatter(
                filtered_customers,
                x="credit_score",
                y="balance",
                color="churn",
                title="Balance vs Credit Score",
                opacity=0.6,
                hover_data=["country", "products_number"],
            )
            st.plotly_chart(fig, use_container_width=True)

        # Tenure analysis
        st.subheader("Customer Tenure Analysis")
        tenure_distribution = filtered_customers["tenure"].value_counts().sort_index()
        fig = px.bar(
            tenure_distribution,
            title="Customer Distribution by Tenure (Years)",
            labels={"value": "Number of Customers", "tenure": "Tenure (Years)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Transaction Patterns")

        if transactions is not None:
            # Merge with transactions
            customer_txns = transactions.merge(
                filtered_customers[["customer_id", "churn"]], on="customer_id"
            )

            # Convert date column to datetime
            customer_txns["date"] = pd.to_datetime(customer_txns["date"])

            col1, col2 = st.columns(2)

            with col1:
                # Transaction types by churn
                txn_type_churn = (
                    customer_txns.groupby(["transaction_type", "churn"])
                    .size()
                    .reset_index(name="count")
                )
                fig = px.bar(
                    txn_type_churn,
                    x="transaction_type",
                    y="count",
                    color="churn",
                    title="Transaction Types by Churn Status",
                    barmode="group",
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Fraud analysis
                fraud_analysis = (
                    customer_txns.groupby("churn")["is_fraudulent"].mean().reset_index()
                )
                fraud_analysis["churn"] = fraud_analysis["churn"].map(
                    {0: "Retained", 1: "Churned"}
                )
                fig = px.bar(
                    fraud_analysis,
                    x="churn",
                    y="is_fraudulent",
                    title="Fraudulent Transaction Rate by Churn Status",
                    labels={"is_fraudulent": "Fraud Rate"},
                )
                st.plotly_chart(fig, use_container_width=True)

            # Monthly transaction volume
            st.subheader("Transaction Volume Over Time")
            customer_txns["month"] = customer_txns["date"].dt.to_period("M")
            monthly_txns = (
                customer_txns.groupby(["month", "churn"])
                .size()
                .reset_index(name="count")
            )
            monthly_txns["month"] = monthly_txns["month"].astype(str)

            fig = px.line(
                monthly_txns,
                x="month",
                y="count",
                color="churn",
                title="Monthly Transaction Volume by Churn Status",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Transaction data not available")

    with tab4:
        st.subheader("Churn Prediction")

        if model_data is not None:
            st.success("✅ ML Model Loaded Successfully")

            # Model information
            st.write("**Model Details:**")
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"- Model Type: {type(model_data['model']).__name__}")
                st.write(f"- Features Used: {len(model_data['features'])}")
                st.write(f"- Optimal Threshold: {model_data['optimal_threshold']:.3f}")

            with col2:
                st.write(f"- Training Date: {datetime.now().strftime('%Y-%m-%d')}")
                st.write(f"- Model Version: 1.0")
                st.write(f"- Last Updated: {datetime.now().strftime('%Y-%m-%d')}")

            # Prediction interface
            st.subheader("Predict Churn for New Customer")

            with st.form("prediction_form"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    credit_score = st.slider("Credit Score", 300, 850, 650)
                    age = st.slider("Age", 18, 80, 35)
                    tenure = st.slider("Tenure (years)", 0, 10, 5)
                    balance = st.number_input("Balance", value=50000.0, step=1000.0)

                with col2:
                    products_number = st.slider("Number of Products", 1, 5, 2)
                    credit_card = st.selectbox(
                        "Has Credit Card",
                        [0, 1],
                        format_func=lambda x: "Yes" if x == 1 else "No",
                    )
                    active_member = st.selectbox(
                        "Active Member",
                        [0, 1],
                        format_func=lambda x: "Yes" if x == 1 else "No",
                    )
                    estimated_salary = st.number_input(
                        "Estimated Salary", value=100000.0, step=1000.0
                    )

                with col3:
                    txn_count = st.slider("Transaction Count", 0, 100, 25)
                    days_since_last_txn = st.slider(
                        "Days Since Last Transaction", 0, 365, 30
                    )
                    country = st.selectbox(
                        "Country",
                        [
                            "Germany",
                            "France",
                            "Spain",
                            "United States",
                            "United Kingdom",
                        ],
                    )
                    gender = st.selectbox("Gender", ["Male", "Female"])

                submitted = st.form_submit_button("Predict Churn Probability")

                if submitted:
                    # Prepare customer data
                    customer_data = {
                        "credit_score": credit_score,
                        "age": age,
                        "tenure": tenure,
                        "balance": balance,
                        "products_number": products_number,
                        "credit_card": credit_card,
                        "active_member": active_member,
                        "estimated_salary": estimated_salary,
                        "txn_count": txn_count,
                        "days_since_last_txn": days_since_last_txn,
                        "country": country,
                        "gender": gender,
                    }

                    # Make prediction
                    try:
                        # Encode categorical variables
                        customer_df = pd.DataFrame([customer_data])
                        customer_df["country_encoded"] = model_data["label_encoders"][
                            "country"
                        ].transform([country])[0]
                        customer_df["gender_encoded"] = model_data["label_encoders"][
                            "gender"
                        ].transform([gender])[0]

                        # Select features and scale
                        X_new = customer_df[model_data["features"]]
                        X_new_scaled = model_data["scaler"].transform(X_new)

                        # Predict
                        probability = model_data["model"].predict_proba(X_new_scaled)[
                            0, 1
                        ]
                        prediction = probability >= model_data["optimal_threshold"]

                        # Display results
                        st.subheader("Prediction Results")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Churn Probability", f"{probability:.2%}")

                        with col2:
                            risk_level = "High" if prediction else "Low"
                            risk_color = "risk-high" if prediction else "risk-low"
                            st.markdown(
                                f"<div class='{risk_color}'>Risk Level: {risk_level}</div>",
                                unsafe_allow_html=True,
                            )

                        with col3:
                            recommendation = (
                                "Immediate retention actions needed"
                                if prediction
                                else "Monitor regularly"
                            )
                            st.write(f"Recommendation: {recommendation}")

                        # Probability gauge
                        fig = go.Figure(
                            go.Indicator(
                                mode="gauge+number+delta",
                                value=probability * 100,
                                domain={"x": [0, 1], "y": [0, 1]},
                                title={"text": "Churn Probability"},
                                delta={
                                    "reference": model_data["optimal_threshold"] * 100
                                },
                                gauge={
                                    "axis": {"range": [None, 100]},
                                    "bar": {"color": "darkblue"},
                                    "steps": [
                                        {"range": [0, 30], "color": "lightgray"},
                                        {"range": [30, 70], "color": "yellow"},
                                        {"range": [70, 100], "color": "red"},
                                    ],
                                    "threshold": {
                                        "line": {"color": "red", "width": 4},
                                        "thickness": 0.75,
                                        "value": model_data["optimal_threshold"] * 100,
                                    },
                                },
                            )
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    except Exception as e:
                        st.error(f"Prediction failed: {e}")

        else:
            st.warning("Please train the ML model first to enable predictions")

    with tab5:
        st.subheader("Business Impact Analysis")

        # Calculate business metrics
        total_customers = len(filtered_customers)
        churned_customers = filtered_customers["churn"].sum()
        total_balance_at_risk = filtered_customers[filtered_customers["churn"] == 1][
            "balance"
        ].sum()
        avg_customer_value = 500  # Annual revenue per customer
        acquisition_cost = 1000  # Cost to acquire new customer

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Revenue at Risk", f"${churned_customers * avg_customer_value:,.0f}"
            )

        with col2:
            st.metric(
                "Acquisition Cost to Replace",
                f"${churned_customers * acquisition_cost:,.0f}",
            )

        with col3:
            st.metric("Balance at Risk", f"${total_balance_at_risk:,.0f}")

        with col4:
            potential_savings = churned_customers * (
                acquisition_cost - 100
            )  # Assuming $100 retention cost
            st.metric("Potential Savings", f"${potential_savings:,.0f}")

        # Retention strategy recommendations
        st.subheader("Retention Strategy Recommendations")

        # High-value at-risk customers
        high_value_at_risk = filtered_customers[
            (filtered_customers["churn"] == 1) & (filtered_customers["balance"] > 10000)
        ].sort_values("balance", ascending=False)

        if len(high_value_at_risk) > 0:
            st.write("**High-Value Customers at Risk:**")
            st.dataframe(
                high_value_at_risk[
                    ["customer_id", "balance", "credit_score", "country"]
                ].head(10)
            )

        # Inactive members with high balances
        inactive_high_balance = filtered_customers[
            (filtered_customers["active_member"] == 0)
            & (filtered_customers["churn"] == 0)
            & (filtered_customers["balance"] > 5000)
        ].sort_values("balance", ascending=False)

        if len(inactive_high_balance) > 0:
            st.write("**Inactive Members (Retention Opportunities):**")
            st.dataframe(
                inactive_high_balance[
                    ["customer_id", "balance", "country", "products_number"]
                ].head(10)
            )

else:
    st.error("❌ No data available. Please run the ETL pipeline to generate data.")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit | Banking Churn Analytics Dashboard")

# Run instructions
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 How to Run")
st.sidebar.markdown(
    """
1. Generate data: `python scripts/setup.py`
2. Run ETL: `python scripts/etl_pipeline.py`
3. Train model: Run `03_churn_prediction.ipynb`
4. Launch: `streamlit run dashboards/streamlit_app.py`
"""
)
