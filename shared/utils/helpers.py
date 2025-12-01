"""
Shared Utilities Module
Common helper functions for data validation, visualization, and utilities
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging
import json
import re
from typing import Dict, List, Any, Optional
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings
warnings.filterwarnings("ignore")


class DataValidator:
    """Data validation and quality checks"""

    @staticmethod
    def validate_dataframe(
        df: pd.DataFrame, df_name: str = "DataFrame"
    ) -> Dict[str, Any]:
        """
        Comprehensive DataFrame validation
        Returns validation report
        """
        validation_report = {
            "name": df_name,
            "timestamp": datetime.now().isoformat(),
            "basic_info": {},
            "quality_metrics": {},
            "issues": [],
        }

        try:
            # Basic information
            validation_report["basic_info"] = {
                "shape": df.shape,
                "columns": list(df.columns),
                "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
                "data_types": df.dtypes.astype(str).to_dict(),
            }

            # Data quality metrics
            validation_report["quality_metrics"] = {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "null_values": df.isnull().sum().to_dict(),
                "null_percentage": round(
                    (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100), 2
                ),
                "duplicate_rows": df.duplicated().sum(),
                "duplicate_percentage": round(
                    (df.duplicated().sum() / len(df) * 100), 2
                ),
            }

            # Identify issues
            issues = []

            # Check for high null percentage
            high_null_cols = [
                col for col in df.columns if df[col].isnull().sum() / len(df) > 0.5
            ]
            if high_null_cols:
                issues.append(
                    f"High null percentage (>50%) in columns: {high_null_cols}"
                )

            # Check for constant columns
            constant_cols = [col for col in df.columns if df[col].nunique() <= 1]
            if constant_cols:
                issues.append(f"Constant or single-value columns: {constant_cols}")

            # Check for duplicate rows
            if validation_report["quality_metrics"]["duplicate_percentage"] > 10:
                issues.append(
                    f"High duplicate rows: {validation_report['quality_metrics']['duplicate_percentage']}%"
                )

            validation_report["issues"] = issues
            validation_report["status"] = "PASS" if not issues else "WARNING"

        except Exception as e:
            validation_report["status"] = "ERROR"
            validation_report["error"] = str(e)
            logger.error(f"Validation failed for {df_name}: {e}")

        return validation_report

    @staticmethod
    def print_validation_report(report: Dict[str, Any]):
        """Print formatted validation report"""
        print(f"\n{'='*60}")
        print(f"📊 VALIDATION REPORT: {report['name']}")
        print(f"⏰ Timestamp: {report['timestamp']}")
        print(f"📋 Status: {report.get('status', 'UNKNOWN')}")
        print(f"{'='*60}")

        if report.get("status") == "ERROR":
            print(f"❌ Error: {report.get('error', 'Unknown error')}")
            return

        # Basic Info
        basic = report["basic_info"]
        print(f"\n📈 BASIC INFORMATION:")
        print(f"   Shape: {basic['shape']}")
        print(f"   Memory Usage: {basic['memory_usage_mb']} MB")
        print(f"   Columns: {len(basic['columns'])}")

        # Quality Metrics
        metrics = report["quality_metrics"]
        print(f"\n🎯 DATA QUALITY METRICS:")
        print(f"   Total Rows: {metrics['total_rows']:,}")
        print(f"   Total Columns: {metrics['total_columns']}")
        print(f"   Null Values: {metrics['null_percentage']}%")
        print(
            f"   Duplicate Rows: {metrics['duplicate_rows']} ({metrics['duplicate_percentage']}%)"
        )

        # Issues
        issues = report["issues"]
        if issues:
            print(f"\n⚠️  DATA QUALITY ISSUES:")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print(f"\n✅ No major data quality issues found!")

        print(f"{'='*60}")


class VisualizationHelper:
    """Helper functions for data visualization"""

    @staticmethod
    def setup_plotting(
        style: str = "seaborn", context: str = "notebook", palette: str = "husl"
    ):
        """Setup consistent plotting style"""
        try:
            plt.style.use(style)
            sns.set_palette(palette)
            sns.set_context(context)

            # Set default figure size and font sizes
            plt.rcParams["figure.figsize"] = (12, 8)
            plt.rcParams["font.size"] = 12
            plt.rcParams["axes.titlesize"] = 16
            plt.rcParams["axes.labelsize"] = 14
            plt.rcParams["xtick.labelsize"] = 12
            plt.rcParams["ytick.labelsize"] = 12

            logger.info(f"Plotting style configured: {style}, {context}")
        except Exception as e:
            logger.warning(f"Failed to set plotting style: {e}")

    @staticmethod
    def save_plot(
        plt_obj,
        filename: str,
        project_name: str,
        dpi: int = 300,
        formats: List[str] = ["png", "pdf"],
    ):
        """Save plot in multiple formats"""
        import os

        plot_dir = f"{project_name}/dashboards/plots"
        os.makedirs(plot_dir, exist_ok=True)

        for fmt in formats:
            filepath = f"{plot_dir}/{filename}.{fmt}"
            plt_obj.savefig(filepath, dpi=dpi, bbox_inches="tight", facecolor="white")
            logger.info(f"Plot saved: {filepath}")

    @staticmethod
    def create_correlation_heatmap(
        df: pd.DataFrame, title: str = "Correlation Matrix", figsize: tuple = (12, 10)
    ):
        """Create a correlation heatmap"""
        # Select only numeric columns
        numeric_df = df.select_dtypes(include=[np.number])

        if numeric_df.empty:
            logger.warning("No numeric columns found for correlation heatmap")
            return None

        plt.figure(figsize=figsize)
        correlation_matrix = numeric_df.corr()

        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))

        heatmap = sns.heatmap(
            correlation_matrix,
            mask=mask,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            square=True,
            cbar_kws={"shrink": 0.8},
        )

        plt.title(title, fontsize=16, fontweight="bold")
        plt.tight_layout()

        return plt


class DataProcessor:
    """Data processing and transformation utilities"""

    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Clean column names: lowercase, remove spaces, special characters"""
        df_clean = df.copy()

        def clean_name(name):
            # Convert to lowercase
            name = name.lower()
            # Replace spaces and special characters with underscores
            name = re.sub(r"[^a-z0-9_]", "_", name)
            # Remove multiple underscores
            name = re.sub(r"_+", "_", name)
            # Remove leading/trailing underscores
            name = name.strip("_")
            return name

        df_clean.columns = [clean_name(col) for col in df_clean.columns]
        return df_clean

    @staticmethod
    def handle_missing_values(
        df: pd.DataFrame,
        strategy: str = "auto",
        numeric_fill: Any = None,
        categorical_fill: Any = None,
    ) -> pd.DataFrame:
        """Handle missing values with various strategies"""
        df_clean = df.copy()

        for column in df_clean.columns:
            if df_clean[column].isnull().any():
                if strategy == "auto":
                    # Auto strategy: mean for numeric, mode for categorical
                    if pd.api.types.is_numeric_dtype(df_clean[column]):
                        fill_value = df_clean[column].mean()
                    else:
                        fill_value = (
                            df_clean[column].mode()[0]
                            if not df_clean[column].mode().empty
                            else "Unknown"
                        )
                elif strategy == "drop":
                    df_clean = df_clean.dropna(subset=[column])
                    continue
                elif strategy == "custom":
                    if pd.api.types.is_numeric_dtype(df_clean[column]):
                        fill_value = numeric_fill if numeric_fill is not None else 0
                    else:
                        fill_value = (
                            categorical_fill
                            if categorical_fill is not None
                            else "Unknown"
                        )
                else:
                    fill_value = (
                        0
                        if pd.api.types.is_numeric_dtype(df_clean[column])
                        else "Unknown"
                    )

                df_clean[column] = df_clean[column].fillna(fill_value)
                logger.info(f"Filled missing values in '{column}' with '{fill_value}'")

        return df_clean

    @staticmethod
    def remove_outliers_iqr(
        df: pd.DataFrame, columns: List[str] = None, factor: float = 1.5
    ) -> pd.DataFrame:
        """Remove outliers using IQR method"""
        df_clean = df.copy()

        if columns is None:
            columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()

        outliers_removed = 0
        for column in columns:
            if column in df_clean.columns and pd.api.types.is_numeric_dtype(
                df_clean[column]
            ):
                Q1 = df_clean[column].quantile(0.25)
                Q3 = df_clean[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - factor * IQR
                upper_bound = Q3 + factor * IQR

                before = len(df_clean)
                df_clean = df_clean[
                    (df_clean[column] >= lower_bound)
                    & (df_clean[column] <= upper_bound)
                ]
                after = len(df_clean)
                outliers_removed += before - after

        logger.info(f"Removed {outliers_removed} outliers using IQR method")
        return df_clean


class BusinessMetrics:
    """Common business metrics calculations"""

    @staticmethod
    def calculate_financial_metrics(
        df: pd.DataFrame, amount_col: str, date_col: str = None
    ) -> Dict[str, Any]:
        """Calculate basic financial metrics"""
        metrics = {
            "total_amount": df[amount_col].sum(),
            "average_amount": df[amount_col].mean(),
            "median_amount": df[amount_col].median(),
            "min_amount": df[amount_col].min(),
            "max_amount": df[amount_col].max(),
            "transaction_count": len(df),
        }

        if date_col and date_col in df.columns:
            # Time-based metrics
            df_sorted = df.sort_values(date_col)
            metrics["date_range"] = {
                "start": df_sorted[date_col].min(),
                "end": df_sorted[date_col].max(),
            }

            # Monthly aggregation
            if hasattr(df_sorted[date_col].iloc[0], "month"):
                monthly = df_sorted.groupby(df_sorted[date_col].dt.to_period("M"))[
                    amount_col
                ].sum()
                metrics["monthly_totals"] = monthly.to_dict()

        return metrics

    @staticmethod
    def calculate_growth_metrics(
        current_period: pd.DataFrame,
        previous_period: pd.DataFrame,
        key_metric: str,
        date_col: str,
    ) -> Dict[str, Any]:
        """Calculate growth metrics between periods"""
        current_total = current_period[key_metric].sum()
        previous_total = previous_period[key_metric].sum()

        if previous_total == 0:
            growth_rate = float("inf")
        else:
            growth_rate = ((current_total - previous_total) / previous_total) * 100

        return {
            "current_period_total": current_total,
            "previous_period_total": previous_total,
            "growth_rate_percent": round(growth_rate, 2),
            "absolute_growth": current_total - previous_total,
        }


# Convenience functions
def setup_environment(style: str = "seaborn"):
    """Setup the complete environment for analysis"""
    VisualizationHelper.setup_plotting(style)
    logger.info("Analysis environment setup complete")


def validate_data(df: pd.DataFrame, df_name: str = "DataFrame") -> Dict[str, Any]:
    """Convenience function for data validation"""
    return DataValidator.validate_dataframe(df, df_name)


def print_validation(df: pd.DataFrame, df_name: str = "DataFrame"):
    """Convenience function to print validation report"""
    report = validate_data(df, df_name)
    DataValidator.print_validation_report(report)
    return report


# Initialize plotting style when module is imported
VisualizationHelper.setup_plotting()

if __name__ == "__main__":
    # Test the helper functions
    print("Testing helper functions...")

    # Create test data
    test_df = pd.DataFrame(
        {
            "sales": [100, 200, 300, 400, 500],
            "customers": [10, 20, 30, 40, 50],
            "region": ["North", "South", "North", "East", "West"],
        }
    )

    # Test validation
    report = validate_data(test_df, "Test DataFrame")
    print_validation(test_df)

    # Test metrics
    metrics = BusinessMetrics.calculate_financial_metrics(test_df, "sales")
    print(f"\n📊 Financial Metrics: {metrics}")
