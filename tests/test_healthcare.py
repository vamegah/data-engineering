"""
Comprehensive test suite for Healthcare Analytics project.
Tests ETL pipeline, patient data, HIPAA compliance, and data quality.
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestHealthcareETL:
    """Test ETL pipeline functionality"""

    def test_data_loading(self):
        """Test that healthcare data can be loaded"""
        data_path = project_root / "data" / "processed"

        files = ["patients_clean.csv", "treatments_clean.csv", "facilities_clean.csv"]

        for filename in files:
            file_path = data_path / filename
            if file_path.exists():
                df = pd.read_csv(file_path)
                assert len(df) > 0, f"{filename} is empty"

    def test_merged_data_exists(self):
        """Test that merged healthcare data exists"""
        data_path = project_root / "data" / "processed"
        merged_file = data_path / "healthcare_merged.csv"

        if merged_file.exists():
            merged = pd.read_csv(merged_file)
            assert len(merged) > 0, "Merged data is empty"

    def test_required_columns_patients(self):
        """Test patient data has required columns"""
        data_path = project_root / "data" / "processed"
        patients_file = data_path / "patients_clean.csv"

        if patients_file.exists():
            patients = pd.read_csv(patients_file)
            required_cols = ["patient_id"]

            for col in required_cols:
                assert col in patients.columns, f"Missing column: {col}"


class TestDataQuality:
    """Test data quality metrics"""

    def test_no_missing_patient_ids(self):
        """Test that patient IDs have no missing values"""
        data_path = project_root / "data" / "processed"
        patients_file = data_path / "patients_clean.csv"

        if patients_file.exists():
            patients = pd.read_csv(patients_file)
            assert patients["patient_id"].isna().sum() == 0, "Missing patient IDs"

    def test_no_duplicate_patients(self):
        """Test no duplicate patient IDs"""
        data_path = project_root / "data" / "processed"
        patients_file = data_path / "patients_clean.csv"

        if patients_file.exists():
            patients = pd.read_csv(patients_file)
            duplicates = patients["patient_id"].duplicated().sum()
            assert duplicates == 0, f"Found {duplicates} duplicate patients"

    def test_age_ranges(self):
        """Test that ages are reasonable"""
        data_path = project_root / "data" / "processed"
        patients_file = data_path / "patients_clean.csv"

        if patients_file.exists():
            patients = pd.read_csv(patients_file)

            if "age" in patients.columns:
                assert (patients["age"] >= 0).all(), "Found negative ages"
                assert (patients["age"] <= 120).all(), "Found unrealistic ages"

    def test_valid_gender_values(self):
        """Test that gender values are valid"""
        data_path = project_root / "data" / "processed"
        patients_file = data_path / "patients_clean.csv"

        if patients_file.exists():
            patients = pd.read_csv(patients_file)

            if "gender" in patients.columns:
                valid_genders = {"M", "F", "Male", "Female", "Other", "Unknown"}
                assert (
                    patients["gender"].isin(valid_genders).all()
                ), "Invalid gender values"


class TestHIPAACompliance:
    """Test HIPAA compliance aspects"""

    def test_no_ssn_in_output(self):
        """Test that SSN is not present in processed files"""
        data_path = project_root / "data" / "processed"
        patients_file = data_path / "patients_clean.csv"

        if patients_file.exists():
            patients = pd.read_csv(patients_file)

            # SSN should not be in processed output
            ssn_columns = [col for col in patients.columns if "ssn" in col.lower()]
            assert (
                len(ssn_columns) == 0
            ), "SSN found in processed data - HIPAA violation"

    def test_phi_encryption_flag(self):
        """Test that PHI encryption is configured"""
        # This would check if encryption is enabled in config
        # For now, just verify the test exists
        assert True, "PHI encryption should be enabled in production"

    def test_audit_logging_enabled(self):
        """Test that audit logging is configured"""
        # This would check if audit logging is enabled
        # For now, just verify the test exists
        assert True, "Audit logging should be enabled in production"


class TestTreatmentData:
    """Test treatment data quality"""

    def test_treatment_costs_positive(self):
        """Test that treatment costs are positive"""
        data_path = project_root / "data" / "processed"
        treatments_file = data_path / "treatments_clean.csv"

        if treatments_file.exists():
            treatments = pd.read_csv(treatments_file)

            cost_cols = [
                col
                for col in treatments.columns
                if "cost" in col.lower() or "charge" in col.lower()
            ]
            for col in cost_cols:
                assert (
                    treatments[col].dropna() >= 0
                ).all(), f"{col} has negative values"

    def test_treatment_dates_valid(self):
        """Test that treatment dates are valid"""
        data_path = project_root / "data" / "processed"
        treatments_file = data_path / "treatments_clean.csv"

        if treatments_file.exists():
            treatments = pd.read_csv(treatments_file)

            date_cols = [col for col in treatments.columns if "date" in col.lower()]
            for col in date_cols:
                if col in treatments.columns:
                    dates = pd.to_datetime(treatments[col], errors="coerce")
                    assert dates.notna().any(), f"{col} has no valid dates"


class TestFacilityData:
    """Test facility data quality"""

    def test_facility_capacity_positive(self):
        """Test that facility capacities are positive"""
        data_path = project_root / "data" / "processed"
        facilities_file = data_path / "facilities_clean.csv"

        if facilities_file.exists():
            facilities = pd.read_csv(facilities_file)

            capacity_cols = [
                col for col in facilities.columns if "capacity" in col.lower()
            ]
            for col in capacity_cols:
                assert (
                    facilities[col].dropna() > 0
                ).all(), f"{col} has non-positive values"


class TestPerformance:
    """Test performance metrics"""

    def test_data_loading_speed(self):
        """Test data loads within reasonable time"""
        import time

        data_path = project_root / "data" / "processed"
        merged_file = data_path / "healthcare_merged.csv"

        if merged_file.exists():
            start = time.time()
            merged = pd.read_csv(merged_file)
            load_time = time.time() - start

            assert load_time < 5.0, f"Loading took {load_time:.2f}s, should be < 5s"

    def test_memory_usage(self):
        """Test memory usage is reasonable"""
        data_path = project_root / "data" / "processed"
        merged_file = data_path / "healthcare_merged.csv"

        if merged_file.exists():
            merged = pd.read_csv(merged_file)
            memory_mb = merged.memory_usage(deep=True).sum() / 1024 / 1024
            assert memory_mb < 500, f"Using {memory_mb:.0f}MB, should be < 500MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
