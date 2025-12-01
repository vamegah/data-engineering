-- Healthcare Database Schema
-- Patient Analytics Project

-- Facilities table
CREATE TABLE IF NOT EXISTS facilities (
    facility_id VARCHAR(50) PRIMARY KEY,
    facility_name VARCHAR(200),
    facility_type VARCHAR(100),
    specialty VARCHAR(100),
    location VARCHAR(100),
    bed_capacity INTEGER,
    established_year INTEGER
);

-- Patients table
CREATE TABLE IF NOT EXISTS patients (
    patient_id VARCHAR(50) PRIMARY KEY,
    age INTEGER,
    gender VARCHAR(20),
    blood_type VARCHAR(10),
    primary_condition VARCHAR(100),
    admission_date DATE,
    discharge_date DATE,
    facility_id VARCHAR(50),
    insurance_type VARCHAR(50),
    readmission_30_days INTEGER,
    FOREIGN KEY (facility_id) REFERENCES facilities(facility_id)
);

-- Treatments table
CREATE TABLE IF NOT EXISTS treatments (
    treatment_id VARCHAR(50) PRIMARY KEY,
    patient_id VARCHAR(50),
    treatment_type VARCHAR(100),
    treatment_date DATE,
    cost DECIMAL(10,2),
    duration_days INTEGER,
    outcome VARCHAR(50),
    medication_prescribed BOOLEAN,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- Create indexes for better performance
CREATE INDEX idx_patients_facility ON patients(facility_id);
CREATE INDEX idx_patients_admission ON patients(admission_date);
CREATE INDEX idx_treatments_patient ON treatments(patient_id);
CREATE INDEX idx_treatments_date ON treatments(treatment_date);
CREATE INDEX idx_treatments_type ON treatments(treatment_type);

-- Create a view for patient readmissions
CREATE OR REPLACE VIEW patient_readmissions AS
SELECT 
    p.patient_id,
    p.age,
    p.gender,
    p.primary_condition,
    p.insurance_type,
    p.readmission_30_days,
    f.facility_name,
    f.specialty
FROM patients p
JOIN facilities f ON p.facility_id = f.facility_id
WHERE p.readmission_30_days = 1;

-- Create a view for treatment effectiveness
CREATE OR REPLACE VIEW treatment_effectiveness AS
SELECT 
    treatment_type,
    outcome,
    COUNT(*) as treatment_count,
    AVG(cost) as avg_cost,
    AVG(duration_days) as avg_duration
FROM treatments
GROUP BY treatment_type, outcome;