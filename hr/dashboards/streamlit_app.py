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
from datetime import datetime

# Add shared modules to path
# sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))
# from config.database import DatabaseConfig
# from utils.helpers import VisualizationHelper

# Page configuration
st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="📊",
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


class HRAnalyticsDashboard:
    """HR Analytics Dashboard Class"""

    def __init__(self):
        self.employees = None
        self.exit_interviews = None
        self.risk_scores = None
        self.load_data()

    def load_data(self):
        """Load data from processed files"""
        try:
            self.employees = pd.read_csv("../data/processed/employees_clean.csv")
            self.exit_interviews = pd.read_csv(
                "../data/processed/exit_interviews_clean.csv"
            )

            # Try to load risk scores if available
            try:
                self.risk_scores = pd.read_csv(
                    "../data/processed/employee_risk_scores.csv"
                )
                self.employees = self.employees.merge(
                    self.risk_scores, on="employee_id", how="left"
                )
            except FileNotFoundError:
                st.warning("⚠️ Risk scores not found. Run the predictive model first.")

        except FileNotFoundError:
            st.error("❌ Processed data not found. Please run the ETL pipeline first.")
            st.stop()

    def display_header(self):
        """Display dashboard header"""
        st.markdown(
            '<h1 class="main-header">🏢 HR Analytics Dashboard</h1>',
            unsafe_allow_html=True,
        )
        st.markdown("**Employee Attrition Analysis and Predictive Insights**")

        # Overall metrics
        col1, col2, col3, col4 = st.columns(4)

        total_employees = len(self.employees)
        attrition_count = (self.employees["attrition"] == "Yes").sum()
        attrition_rate = (attrition_count / total_employees) * 100
        avg_salary = self.employees["salary"].mean()
        avg_satisfaction = self.employees["job_satisfaction"].mean()

        with col1:
            st.metric("Total Employees", f"{total_employees:,}")

        with col2:
            st.metric("Employees Left", f"{attrition_count:,}")

        with col3:
            st.metric("Attrition Rate", f"{attrition_rate:.1f}%")

        with col4:
            st.metric("Avg Salary", f"${avg_salary:,.0f}")

    def sidebar_filters(self):
        """Create sidebar filters"""
        st.sidebar.header("🔍 Filters")

        # Department filter
        departments = ["All"] + sorted(self.employees["department"].unique().tolist())
        selected_dept = st.sidebar.selectbox("Department", departments)

        # Job Role filter
        job_roles = ["All"] + sorted(self.employees["job_role"].unique().tolist())
        selected_role = st.sidebar.selectbox("Job Role", job_roles)

        # Attrition status filter
        attrition_status = st.sidebar.selectbox(
            "Attrition Status", ["All", "Yes", "No"]
        )

        return selected_dept, selected_role, attrition_status

    def apply_filters(self, selected_dept, selected_role, attrition_status):
        """Apply filters to data"""
        filtered_data = self.employees.copy()

        if selected_dept != "All":
            filtered_data = filtered_data[filtered_data["department"] == selected_dept]

        if selected_role != "All":
            filtered_data = filtered_data[filtered_data["job_role"] == selected_role]

        if attrition_status != "All":
            filtered_data = filtered_data[
                filtered_data["attrition"] == attrition_status
            ]

        return filtered_data

    def display_demographic_insights(self, filtered_data):
        """Display demographic insights"""
        st.header("👥 Demographic Insights")

        col1, col2 = st.columns(2)

        with col1:
            # Attrition by Department
            dept_attrition = (
                filtered_data.groupby("department")["attrition"]
                .apply(lambda x: (x == "Yes").mean() * 100)
                .reset_index()
            )

            fig = px.bar(
                dept_attrition,
                x="department",
                y="attrition",
                title="Attrition Rate by Department",
                labels={"attrition": "Attrition Rate (%)", "department": "Department"},
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Attrition by Age Group
            age_attrition = (
                pd.crosstab(
                    filtered_data["age_group"],
                    filtered_data["attrition"],
                    normalize="index",
                )
                * 100
            )
            age_attrition = age_attrition.reset_index().melt(
                id_vars=["age_group"], value_name="percentage", var_name="attrition"
            )

            fig = px.bar(
                age_attrition,
                x="age_group",
                y="percentage",
                color="attrition",
                title="Attrition Distribution by Age Group",
                barmode="group",
            )
            st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            # Gender Analysis
            gender_analysis = (
                pd.crosstab(
                    filtered_data["gender"],
                    filtered_data["attrition"],
                    normalize="index",
                )
                * 100
            )
            gender_analysis = gender_analysis.reset_index().melt(
                id_vars=["gender"], value_name="percentage", var_name="attrition"
            )

            fig = px.bar(
                gender_analysis,
                x="gender",
                y="percentage",
                color="attrition",
                title="Attrition Rate by Gender",
                barmode="group",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col4:
            # Marital Status
            marital_analysis = (
                pd.crosstab(
                    filtered_data["marital_status"],
                    filtered_data["attrition"],
                    normalize="index",
                )
                * 100
            )
            marital_analysis = marital_analysis.reset_index().melt(
                id_vars=["marital_status"],
                value_name="percentage",
                var_name="attrition",
            )

            fig = px.bar(
                marital_analysis,
                x="marital_status",
                y="percentage",
                color="attrition",
                title="Attrition Rate by Marital Status",
                barmode="group",
            )
            st.plotly_chart(fig, use_container_width=True)

    def display_job_factors(self, filtered_data):
        """Display job-related factors"""
        st.header("💼 Job-Related Factors")

        col1, col2 = st.columns(2)

        with col1:
            # Salary vs Attrition
            fig = px.box(
                filtered_data,
                x="attrition",
                y="salary",
                title="Salary Distribution by Attrition Status",
                color="attrition",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Job Satisfaction
            satisfaction_attrition = (
                pd.crosstab(
                    filtered_data["job_satisfaction"],
                    filtered_data["attrition"],
                    normalize="index",
                )
                * 100
            )
            satisfaction_attrition = satisfaction_attrition.reset_index().melt(
                id_vars=["job_satisfaction"],
                value_name="percentage",
                var_name="attrition",
            )

            fig = px.line(
                satisfaction_attrition,
                x="job_satisfaction",
                y="percentage",
                color="attrition",
                title="Attrition Rate by Job Satisfaction Level",
                markers=True,
            )
            st.plotly_chart(fig, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            # Overtime Impact
            overtime_impact = (
                pd.crosstab(
                    filtered_data["overtime"],
                    filtered_data["attrition"],
                    normalize="index",
                )
                * 100
            )
            overtime_impact = overtime_impact.reset_index().melt(
                id_vars=["overtime"], value_name="percentage", var_name="attrition"
            )

            fig = px.bar(
                overtime_impact,
                x="overtime",
                y="percentage",
                color="attrition",
                title="Overtime Impact on Attrition",
                barmode="group",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col4:
            # Tenure Analysis
            tenure_attrition = (
                pd.crosstab(
                    filtered_data["tenure_group"],
                    filtered_data["attrition"],
                    normalize="index",
                )
                * 100
            )
            tenure_attrition = tenure_attrition.reset_index().melt(
                id_vars=["tenure_group"], value_name="percentage", var_name="attrition"
            )

            fig = px.bar(
                tenure_attrition,
                x="tenure_group",
                y="percentage",
                color="attrition",
                title="Attrition Rate by Tenure Group",
                barmode="group",
            )
            st.plotly_chart(fig, use_container_width=True)

    def display_predictive_insights(self, filtered_data):
        """Display predictive modeling insights"""
        st.header("🔮 Predictive Insights")

        if "attrition_probability" not in filtered_data.columns:
            st.warning(
                "⚠️ Predictive model results not available. Run the attrition analysis notebook first."
            )
            return

        col1, col2 = st.columns(2)

        with col1:
            # Risk Distribution
            risk_distribution = filtered_data["risk_level"].value_counts().reset_index()
            risk_distribution.columns = ["risk_level", "count"]

            fig = px.pie(
                risk_distribution,
                values="count",
                names="risk_level",
                title="Employee Attrition Risk Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Risk by Department
            risk_dept = (
                pd.crosstab(
                    filtered_data["department"],
                    filtered_data["risk_level"],
                    normalize="index",
                )
                * 100
            )
            fig = px.imshow(
                risk_dept,
                title="Attrition Risk Heatmap by Department",
                labels=dict(x="Risk Level", y="Department", color="Percentage"),
            )
            st.plotly_chart(fig, use_container_width=True)

        # High-risk employees table
        st.subheader("🔴 High-Risk Employees")
        high_risk = filtered_data[
            filtered_data["risk_level"].isin(["High", "Very High"])
        ]

        if len(high_risk) > 0:
            # Display key information about high-risk employees
            display_columns = [
                "employee_id",
                "department",
                "job_role",
                "salary",
                "job_satisfaction",
                "attrition_probability",
                "risk_level",
            ]
            st.dataframe(
                high_risk[display_columns].sort_values(
                    "attrition_probability", ascending=False
                )
            )

            st.metric("High/Very High Risk Employees", len(high_risk))
        else:
            st.info("🎉 No high-risk employees found in the filtered data!")

    def display_exit_analysis(self):
        """Display exit interview analysis"""
        if len(self.exit_interviews) == 0:
            return

        st.header("🎤 Exit Interview Analysis")

        col1, col2 = st.columns(2)

        with col1:
            # Exit reasons
            exit_reasons = self.exit_interviews["reason"].value_counts().reset_index()
            exit_reasons.columns = ["reason", "count"]

            fig = px.pie(
                exit_reasons,
                values="count",
                names="reason",
                title="Primary Reasons for Leaving",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Satisfaction scores
            satisfaction_dist = (
                self.exit_interviews["satisfaction_score"].value_counts().sort_index()
            )
            fig = px.bar(
                x=satisfaction_dist.index,
                y=satisfaction_dist.values,
                title="Exit Satisfaction Scores Distribution",
                labels={"x": "Satisfaction Score", "y": "Count"},
            )
            st.plotly_chart(fig, use_container_width=True)

    def display_recommendations(self, filtered_data):
        """Display business recommendations"""
        st.header("💡 Business Recommendations")

        # Calculate key metrics for recommendations
        attrition_rate = (filtered_data["attrition"] == "Yes").mean() * 100
        avg_salary = filtered_data["salary"].mean()
        low_satisfaction = (filtered_data["job_satisfaction"] <= 2).mean() * 100
        overtime_rate = (filtered_data["overtime"] == "Yes").mean() * 100

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🎯 Immediate Actions")

            if attrition_rate > 15:
                st.error(
                    f"**High Priority**: Attrition rate is {attrition_rate:.1f}% - Implement retention programs"
                )
            elif attrition_rate > 10:
                st.warning(
                    f"**Medium Priority**: Attrition rate is {attrition_rate:.1f}% - Monitor closely"
                )
            else:
                st.success(
                    f"**Low Priority**: Attrition rate is {attrition_rate:.1f}% - Maintain current practices"
                )

            if low_satisfaction > 30:
                st.error(
                    f"**Employee Satisfaction**: {low_satisfaction:.1f}% have low satisfaction - Improve workplace environment"
                )

            if overtime_rate > 40:
                st.warning(
                    f"**Work-Life Balance**: {overtime_rate:.1f}% work overtime - Address workload issues"
                )

        with col2:
            st.subheader("📈 Strategic Initiatives")

            recommendations = [
                "✅ Implement mentorship programs for employees with <2 years tenure",
                "✅ Review compensation for high-performing, underpaid employees",
                "✅ Develop department-specific retention strategies",
                "✅ Enhance career development and growth opportunities",
                "✅ Conduct stay interviews with high-risk employees",
                "✅ Improve work-life balance initiatives",
            ]

            for rec in recommendations:
                st.write(rec)

        # Department-specific recommendations
        st.subheader("🏢 Department-Specific Focus")

        dept_analysis = (
            filtered_data.groupby("department")
            .agg(
                {
                    "attrition": lambda x: (x == "Yes").mean() * 100,
                    "salary": "mean",
                    "job_satisfaction": "mean",
                }
            )
            .round(2)
        )

        st.dataframe(
            dept_analysis.style.highlight_max(axis=0, color="#ffcccc").highlight_min(
                axis=0, color="#ccffcc"
            )
        )

    def run_dashboard(self):
        """Run the complete dashboard"""
        self.display_header()

        # Sidebar filters
        selected_dept, selected_role, attrition_status = self.sidebar_filters()

        # Apply filters
        filtered_data = self.apply_filters(
            selected_dept, selected_role, attrition_status
        )

        # Display insights in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [
                "📊 Demographics",
                "💼 Job Factors",
                "🔮 Predictive",
                "🎤 Exit Analysis",
                "💡 Recommendations",
            ]
        )

        with tab1:
            self.display_demographic_insights(filtered_data)

        with tab2:
            self.display_job_factors(filtered_data)

        with tab3:
            self.display_predictive_insights(filtered_data)

        with tab4:
            self.display_exit_analysis()

        with tab5:
            self.display_recommendations(filtered_data)

        # Footer
        st.markdown("---")
        st.markdown(
            "**HR Analytics Dashboard** | Built with Streamlit | Data Engineering Portfolio"
        )


# Run the dashboard
if __name__ == "__main__":
    dashboard = HRAnalyticsDashboard()
    dashboard.run_dashboard()
