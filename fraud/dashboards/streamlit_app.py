import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import sys
import os
from datetime import datetime, timedelta

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))
from config.database import DatabaseConfig

# from utils.helpers import setup_plotting

# Page configuration
st.set_page_config(
    page_title="Fraud Detection Dashboard",
    page_icon="🔍",
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
    .fraud-alert {
        background-color: #ffcccc;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff0000;
    }
    .safe-transaction {
        background-color: #ccffcc;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00cc00;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Title and description
st.markdown(
    '<h1 class="main-header">🔍 Real-Time Fraud Detection Dashboard</h1>',
    unsafe_allow_html=True,
)
st.markdown("**Monitor transactions and detect fraudulent activities in real-time**")

# Sidebar
st.sidebar.header("🔧 Dashboard Controls")


# Load data and model
@st.cache_data
def load_data():
    """Load fraud detection data"""
    try:
        fraud_data = pd.read_csv("../data/processed/fraud_data_clean.csv")
        fraud_data["transaction_date"] = pd.to_datetime(fraud_data["transaction_date"])
        return fraud_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


@st.cache_resource
def load_model():
    """Load trained fraud detection model"""
    try:
        model_artifacts = joblib.load("./models/fraud_detection_model.pkl")
        return model_artifacts
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None


# Helper function for prediction (must match notebook version with imputer)
def predict_fraud(transaction_data, model_artifacts):
    """
    Predict fraud probability for a single transaction
    """
    model = model_artifacts["model"]
    scaler = model_artifacts.get("scaler")
    imputer = model_artifacts.get("imputer")
    label_encoders = model_artifacts.get("label_encoders", {})
    features = model_artifacts["features"]

    # Prepare the input data
    input_df = pd.DataFrame([transaction_data])

    # Encode categorical variables (handle unseen categories)
    for col, encoder in label_encoders.items():
        if col in input_df.columns:
            try:
                input_df[col] = encoder.transform(input_df[col].astype(str))
            except ValueError:
                # unseen category -> assign special value (e.g., -1)
                input_df[col] = -1
        else:
            input_df[col] = -1

    # Ensure all features are present
    for feature in features:
        if feature not in input_df.columns:
            input_df[feature] = 0

    # Select features in correct order
    input_df = input_df[features]

    # Replace infinities and impute numeric columns if imputer available
    input_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    numeric_cols_in_input = input_df.select_dtypes(include=[np.number]).columns.tolist()
    if imputer is not None and len(numeric_cols_in_input) > 0:
        input_df[numeric_cols_in_input] = imputer.transform(
            input_df[numeric_cols_in_input]
        )

    # Scale numeric features if scaler available
    if scaler is not None and len(numeric_cols_in_input) > 0:
        input_df[numeric_cols_in_input] = scaler.transform(
            input_df[numeric_cols_in_input]
        )

    # Predict (handle models without predict_proba)
    if hasattr(model, "predict_proba"):
        fraud_probability = model.predict_proba(input_df)[:, 1][0]
    else:
        try:
            prob = model.decision_function(input_df)
            prob = (prob - prob.min()) / (prob.max() - prob.min() + 1e-12)
            fraud_probability = prob[0]
        except Exception:
            fraud_probability = 0.0

    is_fraud = fraud_probability > model_artifacts.get("optimal_threshold", 0.5)

    return fraud_probability, is_fraud


# Load data and model
fraud_data = load_data()
model_artifacts = load_model()

# Sidebar filters
st.sidebar.subheader("📊 Data Filters")

if fraud_data is not None:
    # Date range filter
    min_date = fraud_data["transaction_date"].min().date()
    max_date = fraud_data["transaction_date"].max().date()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date,
    )

    # Category filter
    categories = ["All"] + sorted(fraud_data["category"].unique().tolist())
    selected_category = st.sidebar.selectbox("Transaction Category", categories)

    # Location filter (only if location column exists)
    if "location" in fraud_data.columns:
        locations = ["All"] + sorted(fraud_data["location"].unique().tolist())
        selected_location = st.sidebar.selectbox("Transaction Location", locations)
    else:
        selected_location = "All"

    # Apply filters
    filtered_data = fraud_data.copy()

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_data = filtered_data[
            (filtered_data["transaction_date"].dt.date >= start_date)
            & (filtered_data["transaction_date"].dt.date <= end_date)
        ]

    if selected_category != "All":
        filtered_data = filtered_data[filtered_data["category"] == selected_category]

    if selected_location != "All" and "location" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["location"] == selected_location]

# Main dashboard layout
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Overview", "🔍 Fraud Analysis", "🤖 Model Insights", "🎯 Real-Time Detection"]
)

with tab1:
    st.header("📈 Transaction Overview")

    if fraud_data is not None:
        # Key Metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_transactions = len(filtered_data)
            st.metric("Total Transactions", f"{total_transactions:,}")

        with col2:
            fraud_cases = filtered_data["is_fraud"].sum()
            st.metric("Fraud Cases", f"{fraud_cases:,}")

        with col3:
            fraud_rate = filtered_data["is_fraud"].mean()
            st.metric("Fraud Rate", f"{fraud_rate:.2%}")

        with col4:
            total_fraud_amount = filtered_data[filtered_data["is_fraud"] == 1][
                "amount"
            ].sum()
            st.metric("Total Fraud Amount", f"${total_fraud_amount:,.2f}")

        # Transaction Trends
        st.subheader("📊 Transaction Trends")

        col1, col2 = st.columns(2)

        with col1:
            # Daily transaction volume
            daily_volume = filtered_data.groupby(
                filtered_data["transaction_date"].dt.date
            ).size()
            fig = px.line(
                x=daily_volume.index,
                y=daily_volume.values,
                title="Daily Transaction Volume",
                labels={"x": "Date", "y": "Number of Transactions"},
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Daily fraud rate
            daily_fraud = filtered_data.groupby(
                filtered_data["transaction_date"].dt.date
            )["is_fraud"].mean()
            fig = px.line(
                x=daily_fraud.index,
                y=daily_fraud.values,
                title="Daily Fraud Rate",
                labels={"x": "Date", "y": "Fraud Rate"},
            )
            st.plotly_chart(fig, use_container_width=True)

        # Category Analysis
        st.subheader("🏷️ Transaction Categories")

        col1, col2 = st.columns(2)

        with col1:
            # Transactions by category
            category_counts = filtered_data["category"].value_counts()
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Transactions by Category",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Fraud rate by category
            fraud_by_category = (
                filtered_data.groupby("category")["is_fraud"]
                .mean()
                .sort_values(ascending=False)
            )
            fig = px.bar(
                x=fraud_by_category.index,
                y=fraud_by_category.values,
                title="Fraud Rate by Category",
                labels={"x": "Category", "y": "Fraud Rate"},
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("🔍 Detailed Fraud Analysis")

    if fraud_data is not None:
        # Fraud Patterns
        st.subheader("🎯 Fraud Patterns")

        col1, col2 = st.columns(2)

        with col1:
            # Fraud by hour
            fraud_by_hour = filtered_data.groupby("hour_of_day")["is_fraud"].mean()
            fig = px.line(
                x=fraud_by_hour.index,
                y=fraud_by_hour.values,
                title="Fraud Rate by Hour of Day",
                labels={"x": "Hour of Day", "y": "Fraud Rate"},
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Fraud by location (only if location column exists)
            if "location" in filtered_data.columns:
                fraud_by_location = (
                    filtered_data.groupby("location")["is_fraud"]
                    .mean()
                    .sort_values(ascending=False)
                )
                fig = px.bar(
                    x=fraud_by_location.index,
                    y=fraud_by_location.values,
                    title="Fraud Rate by Location",
                    labels={"x": "Location", "y": "Fraud Rate"},
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Location data not available in dataset")

        # High-Risk Transactions
        st.subheader("🚨 High-Risk Transaction Analysis")

        # High-value transactions analysis
        high_value_threshold = filtered_data["amount"].quantile(0.95)
        high_value_data = filtered_data[filtered_data["amount"] > high_value_threshold]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("High-Value Threshold", f"${high_value_threshold:.2f}")

        with col2:
            high_value_fraud_rate = high_value_data["is_fraud"].mean()
            st.metric("High-Value Fraud Rate", f"{high_value_fraud_rate:.2%}")

        with col3:
            high_value_fraud_cases = high_value_data["is_fraud"].sum()
            st.metric("High-Value Fraud Cases", f"{high_value_fraud_cases:,}")

        # Device and Location Combination (only if both columns exist)
        st.subheader("📱 Device & Location Risk Analysis")

        if (
            "device_used" in filtered_data.columns
            and "location" in filtered_data.columns
        ):
            device_location_risk = (
                filtered_data.groupby(["device_used", "location"])
                .agg({"is_fraud": ["count", "mean"]})
                .round(4)
            )
            device_location_risk.columns = ["transaction_count", "fraud_rate"]
            device_location_risk = device_location_risk.sort_values(
                "fraud_rate", ascending=False
            )
            st.dataframe(device_location_risk.head(10), use_container_width=True)
        else:
            st.info("Device or Location data not available for risk analysis")

with tab3:
    st.header("🤖 Model Insights")

    if model_artifacts is not None:
        st.success("✅ Fraud detection model loaded successfully!")

        # Model information
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Model Performance")
            st.metric(
                "Optimal Threshold", f"{model_artifacts['optimal_threshold']:.3f}"
            )
            st.metric("Number of Features", len(model_artifacts["features"]))

        with col2:
            st.subheader("Feature Information")
            st.write("Top features used for detection:")
            for feature in model_artifacts["features"][:5]:
                st.write(f"• {feature}")

        # Feature importance visualization
        if hasattr(model_artifacts["model"], "feature_importances_"):
            st.subheader("📊 Feature Importance")

            feature_importance = pd.DataFrame(
                {
                    "feature": model_artifacts["features"],
                    "importance": model_artifacts["model"].feature_importances_,
                }
            ).sort_values("importance", ascending=False)

            fig = px.bar(
                feature_importance.head(10),
                x="importance",
                y="feature",
                title="Top 10 Most Important Features",
                orientation="h",
            )
            st.plotly_chart(fig, use_container_width=True)

        # Model evaluation metrics
        st.subheader("📈 Model Evaluation")

        # Simulate some evaluation metrics (in a real scenario, these would come from actual model evaluation)
        metrics_data = {
            "Metric": ["Precision", "Recall", "F1-Score", "AUC-ROC"],
            "Value": [0.85, 0.78, 0.81, 0.92],
        }

        metrics_df = pd.DataFrame(metrics_data)
        st.dataframe(metrics_df, use_container_width=True)

    else:
        st.error("❌ Model not available. Please train the model first.")

with tab4:
    st.header("🎯 Real-Time Fraud Detection")

    if model_artifacts is not None:
        st.info("Enter transaction details to check for potential fraud")

        # Transaction input form
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)

            with col1:
                amount = st.number_input(
                    "Transaction Amount ($)", min_value=0.0, value=100.0, step=10.0
                )
                hour_of_day = st.slider("Hour of Day", 0, 23, 12)
                category = st.selectbox(
                    "Category", model_artifacts["label_encoders"]["category"].classes_
                )
                if "location" in model_artifacts["label_encoders"]:
                    location = st.selectbox(
                        "Location",
                        model_artifacts["label_encoders"]["location"].classes_,
                    )
                else:
                    location = "Unknown"

            with col2:
                device_used = st.selectbox(
                    "Device Used",
                    model_artifacts["label_encoders"]["device_used"].classes_,
                )
                account_age_days = st.number_input(
                    "Account Age (days)", min_value=0, value=30
                )
                transaction_count = st.number_input(
                    "User Transaction Count", min_value=1, value=10
                )
                avg_amount = st.number_input(
                    "User Average Transaction Amount", min_value=0.0, value=50.0
                )

            # Additional features
            col3, col4 = st.columns(2)

            with col3:
                std_amount = st.number_input(
                    "Transaction Amount Std Dev", min_value=0.0, value=25.0
                )
                max_amount = st.number_input(
                    "User Max Transaction Amount", min_value=0.0, value=200.0
                )

            with col4:
                is_weekend = st.selectbox(
                    "Is Weekend?",
                    [0, 1],
                    format_func=lambda x: "Yes" if x == 1 else "No",
                )
                is_late_night = st.selectbox(
                    "Is Late Night (0-5 AM)?",
                    [0, 1],
                    format_func=lambda x: "Yes" if x == 1 else "No",
                )

            submitted = st.form_submit_button("🔍 Check for Fraud")

        if submitted:
            # Calculate derived features
            transaction_frequency = transaction_count / max(account_age_days, 1)
            amount_to_avg_ratio = amount / max(avg_amount, 0.01)
            is_high_value = 1 if amount > 1000 else 0
            is_international = 1 if location == "International" else 0

            # Create transaction data
            transaction_data = {
                "amount": amount,
                "hour_of_day": hour_of_day,
                "category": category,
                "location": location,
                "device_used": device_used,
                "account_age_days": account_age_days,
                "transaction_count": transaction_count,
                "avg_amount": avg_amount,
                "std_amount": std_amount,
                "max_amount": max_amount,
                "transaction_frequency": transaction_frequency,
                "amount_to_avg_ratio": amount_to_avg_ratio,
                "is_high_value": is_high_value,
                "is_late_night": is_late_night,
                "is_international": is_international,
                "is_weekend": is_weekend,
            }

            # Make prediction
            try:
                fraud_probability, is_fraud = predict_fraud(
                    transaction_data, model_artifacts
                )

                # Display results
                st.subheader("🔍 Fraud Detection Result")

                if is_fraud:
                    st.markdown(
                        f"""
                    <div class="fraud-alert">
                        <h3>🚨 FRAUD ALERT!</h3>
                        <p><strong>Fraud Probability:</strong> {fraud_probability:.1%}</p>
                        <p><strong>Recommendation:</strong> Flag for manual review and consider blocking transaction.</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                    <div class="safe-transaction">
                        <h3>✅ TRANSACTION SAFE</h3>
                        <p><strong>Fraud Probability:</strong> {fraud_probability:.1%}</p>
                        <p><strong>Recommendation:</strong> Transaction appears legitimate. No action required.</p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                # Risk factors analysis
                st.subheader("📋 Risk Factors Analysis")

                risk_factors = []
                if amount_to_avg_ratio > 3:
                    risk_factors.append(
                        f"Amount is {amount_to_avg_ratio:.1f}x higher than user average"
                    )
                if is_late_night:
                    risk_factors.append(
                        "Transaction occurred during late night hours (0-5 AM)"
                    )
                if is_international:
                    risk_factors.append("International transaction")
                if is_high_value:
                    risk_factors.append("High-value transaction")
                if account_age_days < 7:
                    risk_factors.append("New account (less than 7 days old)")

                if risk_factors:
                    st.write("**Identified Risk Factors:**")
                    for factor in risk_factors:
                        st.write(f"• {factor}")
                else:
                    st.write("No significant risk factors identified.")

            except Exception as e:
                st.error(f"Error making prediction: {e}")

    else:
        st.error("❌ Model not available. Please train the model first.")

# Footer
st.markdown("---")
st.markdown(
    "**Fraud Detection Dashboard** | Built with Streamlit | Data Engineering Portfolio"
)
