import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))
from config.database import DatabaseConfig

# from utils.helpers import setup_plotting

# Page configuration
st.set_page_config(
    page_title="Healthcare Analytics Dashboard",
    page_icon="🏥",
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
        text-align: center;
        margin: 0.5rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e86ab;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Title and description
st.markdown(
    '<div class="main-header">🏥 Healthcare Patient Analytics Dashboard</div>',
    unsafe_allow_html=True,
)
st.markdown(
    "**Comprehensive analysis of patient outcomes, treatment effectiveness, and operational efficiency**"
)


# Load data
@st.cache_data
def load_data():
    try:
        patients = pd.read_csv("../data/processed/patients_clean.csv")
        treatments = pd.read_csv("../data/processed/treatments_clean.csv")
        facilities = pd.read_csv("../data/processed/facilities_clean.csv")
        merged_data = pd.read_csv("../data/processed/healthcare_merged.csv")

        # Convert dates
        patients["admission_date"] = pd.to_datetime(patients["admission_date"])
        treatments["treatment_date"] = pd.to_datetime(treatments["treatment_date"])

        return patients, treatments, facilities, merged_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None, None


patients, treatments, facilities, merged_data = load_data()

if patients is not None:
    # Sidebar filters
    st.sidebar.header("🔧 Filters and Controls")

    # Date range filter
    min_date = patients["admission_date"].min().date()
    max_date = patients["admission_date"].max().date()

    date_range = st.sidebar.date_input(
        "Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date
    )

    # Facility filter
    facility_options = ["All"] + list(facilities["facility_name"].unique())
    selected_facility = st.sidebar.selectbox("Select Facility", facility_options)

    # Condition filter
    condition_options = ["All"] + list(patients["primary_condition"].unique())
    selected_condition = st.sidebar.selectbox("Select Condition", condition_options)

    # Apply filters
    filtered_patients = patients.copy()
    if len(date_range) == 2:
        filtered_patients = filtered_patients[
            (filtered_patients["admission_date"].dt.date >= date_range[0])
            & (filtered_patients["admission_date"].dt.date <= date_range[1])
        ]

    if selected_facility != "All":
        facility_id = facilities[facilities["facility_name"] == selected_facility][
            "facility_id"
        ].iloc[0]
        filtered_patients = filtered_patients[
            filtered_patients["facility_id"] == facility_id
        ]

    if selected_condition != "All":
        filtered_patients = filtered_patients[
            filtered_patients["primary_condition"] == selected_condition
        ]

    # Main content
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_patients = len(filtered_patients)
        st.metric("Total Patients", f"{total_patients:,}")

    with col2:
        readmission_rate = filtered_patients["readmission_30_days"].mean() * 100
        st.metric("Readmission Rate", f"{readmission_rate:.1f}%")

    with col3:
        avg_length_of_stay = filtered_patients["length_of_stay"].mean()
        st.metric("Avg Length of Stay", f"{avg_length_of_stay:.1f} days")

    with col4:
        total_cost = treatments["cost"].sum()
        st.metric("Total Treatment Cost", f"${total_cost:,.2f}")

    # Tabs for different analyses
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "📊 Overview",
            "👥 Patient Analytics",
            "💊 Treatment Analysis",
            "🏢 Facility Performance",
            "💡 Recommendations",
        ]
    )

    with tab1:
        st.markdown(
            '<div class="section-header">Overview Dashboard</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            # Monthly admissions trend
            monthly_admissions = (
                filtered_patients.set_index("admission_date").resample("M").size()
            )
            fig = px.line(monthly_admissions, title="Monthly Patient Admissions")
            fig.update_layout(xaxis_title="Month", yaxis_title="Number of Admissions")
            st.plotly_chart(fig, width="stretch")

            # Age distribution
            fig = px.histogram(
                filtered_patients, x="age", nbins=30, title="Patient Age Distribution"
            )
            st.plotly_chart(fig, width="stretch")

        with col2:
            # Condition distribution
            condition_counts = (
                filtered_patients["primary_condition"].value_counts().head(10)
            )
            fig = px.bar(condition_counts, title="Top 10 Primary Conditions")
            fig.update_layout(xaxis_title="Condition", yaxis_title="Count")
            st.plotly_chart(fig, width="stretch")

            # Insurance type distribution
            insurance_counts = filtered_patients["insurance_type"].value_counts()
            fig = px.pie(
                insurance_counts,
                values=insurance_counts.values,
                names=insurance_counts.index,
                title="Insurance Type Distribution",
            )
            st.plotly_chart(fig, width="stretch")

    with tab2:
        st.markdown(
            '<div class="section-header">Patient Analytics</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            # Readmission analysis by condition
            readmission_by_condition = (
                filtered_patients.groupby("primary_condition")["readmission_30_days"]
                .mean()
                .sort_values(ascending=False)
                .head(10)
            )
            fig = px.bar(
                readmission_by_condition, title="Readmission Rate by Condition (Top 10)"
            )
            fig.update_layout(xaxis_title="Condition", yaxis_title="Readmission Rate")
            st.plotly_chart(fig, width="stretch")

            # Length of stay by age group
            filtered_patients["age_group"] = pd.cut(
                filtered_patients["age"],
                bins=[0, 30, 50, 70, 100],
                labels=["0-30", "31-50", "51-70", "71+"],
            )
            los_by_age = filtered_patients.groupby("age_group")["length_of_stay"].mean()
            fig = px.bar(los_by_age, title="Average Length of Stay by Age Group")
            st.plotly_chart(fig, width="stretch")

        with col2:
            # Gender distribution with readmission
            gender_readmission = filtered_patients.groupby("gender")[
                "readmission_30_days"
            ].mean()
            fig = px.bar(gender_readmission, title="Readmission Rate by Gender")
            fig.update_layout(xaxis_title="Gender", yaxis_title="Readmission Rate")
            st.plotly_chart(fig, width="stretch")

            # Insurance type vs readmission
            insurance_readmission = (
                filtered_patients.groupby("insurance_type")["readmission_30_days"]
                .mean()
                .sort_values(ascending=False)
            )
            fig = px.bar(
                insurance_readmission, title="Readmission Rate by Insurance Type"
            )
            st.plotly_chart(fig, width="stretch")

    with tab3:
        st.markdown(
            '<div class="section-header">Treatment Analysis</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            # Treatment type distribution
            treatment_counts = treatments["treatment_type"].value_counts()
            fig = px.bar(treatment_counts, title="Treatment Type Distribution")
            st.plotly_chart(fig, use_container_width=True)

            # Treatment outcomes
            outcome_counts = treatments["outcome"].value_counts()
            fig = px.pie(
                outcome_counts,
                values=outcome_counts.values,
                names=outcome_counts.index,
                title="Treatment Outcomes",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Cost by treatment type
            cost_by_treatment = (
                treatments.groupby("treatment_type")["cost"]
                .mean()
                .sort_values(ascending=False)
            )
            fig = px.bar(cost_by_treatment, title="Average Cost by Treatment Type")
            fig.update_layout(
                xaxis_title="Treatment Type", yaxis_title="Average Cost ($)"
            )
            st.plotly_chart(fig, use_container_width=True)

            # Treatment duration distribution
            fig = px.histogram(
                treatments,
                x="duration_days",
                nbins=20,
                title="Treatment Duration Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab4:
        st.markdown(
            '<div class="section-header">Facility Performance</div>',
            unsafe_allow_html=True,
        )

        # Facility performance metrics
        facility_performance = filtered_patients.merge(facilities, on="facility_id")
        facility_stats = (
            facility_performance.groupby("facility_name")
            .agg(
                {
                    "patient_id": "count",
                    "length_of_stay": "mean",
                    "readmission_30_days": "mean",
                }
            )
            .round(2)
        )

        facility_stats.columns = [
            "Patient Count",
            "Avg Length of Stay",
            "Readmission Rate",
        ]
        facility_stats["Readmission Rate"] = facility_stats["Readmission Rate"] * 100

        # Convert datetime columns to string for Arrow compatibility
        facility_stats_display = facility_stats.copy()
        for col in facility_stats_display.columns:
            if facility_stats_display[col].dtype == "datetime64[ns]":
                facility_stats_display[col] = facility_stats_display[col].astype(str)
        st.dataframe(
            facility_stats_display.sort_values("Patient Count", ascending=False)
        )

        col1, col2 = st.columns(2)

        with col1:
            # Readmission rate by facility
            fig = px.bar(
                facility_stats.sort_values("Readmission Rate", ascending=False).head(
                    10
                ),
                y="Readmission Rate",
                title="Readmission Rate by Facility (Top 10)",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Patient volume by facility type
            facility_type_volume = facility_performance["facility_type"].value_counts()
            fig = px.pie(
                facility_type_volume,
                values=facility_type_volume.values,
                names=facility_type_volume.index,
                title="Patient Volume by Facility Type",
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab5:
        st.markdown(
            '<div class="section-header">Strategic Recommendations</div>',
            unsafe_allow_html=True,
        )

        # Generate recommendations based on data
        high_readmission_conditions = (
            filtered_patients.groupby("primary_condition")["readmission_30_days"]
            .mean()
            .sort_values(ascending=False)
            .head(3)
        )
        high_cost_treatments = (
            treatments.groupby("treatment_type")["cost"]
            .mean()
            .sort_values(ascending=False)
            .head(3)
        )

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎯 Readmission Reduction")
            st.write("**Focus on conditions with highest readmission rates:**")
            for condition, rate in high_readmission_conditions.items():
                st.write(f"• **{condition}**: {rate*100:.1f}% readmission rate")

            st.subheader("💰 Cost Optimization")
            st.write("**Review high-cost treatments for efficiency:**")
            for treatment, cost in high_cost_treatments.items():
                st.write(f"• **{treatment}**: ${cost:.2f} average cost")

        with col2:
            st.subheader("🏢 Resource Allocation")
            busiest_facility = facility_stats["Patient Count"].idxmax()
            highest_readmission_facility = facility_stats["Readmission Rate"].idxmax()

            st.write(f"• **Busiest facility**: {busiest_facility}")
            st.write(
                f"• **Facility needing quality improvement**: {highest_readmission_facility}"
            )

            st.subheader("📈 Growth Opportunities")
            monthly_growth = (
                filtered_patients.set_index("admission_date")
                .resample("M")
                .size()
                .pct_change()
                .mean()
            )
            st.write(f"• **Monthly growth rate**: {monthly_growth*100:.1f}%")
            st.write(
                f"• **Projected annual growth**: {(1 + monthly_growth)**12 - 1:.1%}"
            )

        # Actionable insights
        st.subheader("🚀 Recommended Actions")
        st.info(
            """
        1. **Implement targeted interventions** for high-readmission conditions
        2. **Review cost structure** of most expensive treatments
        3. **Optimize bed allocation** based on facility utilization
        4. **Expand preventive care programs** for chronic conditions
        5. **Enhance patient education** to reduce readmissions
        """
        )

    # Data summary
    with st.expander("📋 Data Summary"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**Patients Data**")
            # Convert datetime columns to string for Arrow compatibility
            filtered_patients_display = filtered_patients.copy()
            for col in filtered_patients_display.columns:
                if filtered_patients_display[col].dtype == "datetime64[ns]":
                    filtered_patients_display[col] = filtered_patients_display[
                        col
                    ].astype(str)
            st.write(filtered_patients_display.describe())

        with col2:
            st.write("**Treatments Data**")
            treatments_display = treatments.copy()
            for col in treatments_display.columns:
                if treatments_display[col].dtype == "datetime64[ns]":
                    treatments_display[col] = treatments_display[col].astype(str)
            st.write(treatments_display.describe())

        with col3:
            st.write("**Facilities Data**")
            facilities_display = facilities.copy()
            for col in facilities_display.columns:
                if facilities_display[col].dtype == "datetime64[ns]":
                    facilities_display[col] = facilities_display[col].astype(str)
            st.write(facilities_display.describe())

else:
    st.error(
        "❌ Unable to load data. Please ensure the data files exist in the data/processed/ directory."
    )
    st.info("💡 Run the ETL pipeline first: `python scripts/etl_pipeline.py`")

# Footer
st.markdown("---")
st.markdown(
    "**Healthcare Analytics Dashboard** | Built with Streamlit | Data Engineering Portfolio"
)
