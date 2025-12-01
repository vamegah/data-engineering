-- Healthcare Business Intelligence Queries
-- Comprehensive analysis for patient outcomes and operational efficiency

-- 1. PATIENT DEMOGRAPHICS AND READMISSION ANALYSIS

-- Patient demographics summary
SELECT 
    COUNT(*) as total_patients,
    AVG(age) as average_age,
    MIN(age) as min_age,
    MAX(age) as max_age,
    gender,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM patients) as percentage
FROM patients
GROUP BY gender
ORDER BY percentage DESC;

-- Readmission analysis by demographic factors
SELECT 
    gender,
    AVG(age) as average_age,
    AVG(length_of_stay) as avg_length_of_stay,
    AVG(readmission_30_days) * 100 as readmission_rate,
    COUNT(*) as patient_count
FROM patients
GROUP BY gender
ORDER BY readmission_rate DESC;

-- Readmission rate by primary condition
SELECT 
    primary_condition,
    COUNT(*) as total_patients,
    SUM(readmission_30_days) as readmissions,
    AVG(readmission_30_days) * 100 as readmission_rate,
    AVG(length_of_stay) as avg_length_of_stay
FROM patients
GROUP BY primary_condition
HAVING COUNT(*) >= 10  -- Only consider conditions with sufficient data
ORDER BY readmission_rate DESC
LIMIT 10;

-- 2. TREATMENT EFFECTIVENESS AND COST ANALYSIS

-- Treatment effectiveness by type
SELECT 
    treatment_type,
    COUNT(*) as total_treatments,
    AVG(cost) as average_cost,
    AVG(duration_days) as average_duration,
    SUM(CASE WHEN outcome = 'Successful' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate,
    SUM(CASE WHEN outcome = 'Improved' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as improvement_rate
FROM treatments
GROUP BY treatment_type
ORDER BY success_rate DESC;

-- Cost analysis by treatment type and outcome
SELECT 
    treatment_type,
    outcome,
    COUNT(*) as treatment_count,
    AVG(cost) as average_cost,
    MIN(cost) as min_cost,
    MAX(cost) as max_cost,
    SUM(cost) as total_cost
FROM treatments
GROUP BY treatment_type, outcome
ORDER BY treatment_type, total_cost DESC;

-- Monthly treatment cost trends
SELECT 
    DATE_TRUNC('month', treatment_date) as month,
    treatment_type,
    COUNT(*) as treatment_count,
    AVG(cost) as avg_cost,
    SUM(cost) as total_cost
FROM treatments
GROUP BY DATE_TRUNC('month', treatment_date), treatment_type
ORDER BY month, total_cost DESC;

-- 3. FACILITY PERFORMANCE METRICS

-- Facility performance summary
SELECT 
    f.facility_name,
    f.facility_type,
    f.specialty,
    f.bed_capacity,
    COUNT(p.patient_id) as total_patients,
    AVG(p.length_of_stay) as avg_length_of_stay,
    AVG(p.readmission_30_days) * 100 as readmission_rate,
    AVG(t.cost) as avg_treatment_cost
FROM facilities f
LEFT JOIN patients p ON f.facility_id = p.facility_id
LEFT JOIN treatments t ON p.patient_id = t.patient_id
GROUP BY f.facility_id, f.facility_name, f.facility_type, f.specialty, f.bed_capacity
ORDER BY total_patients DESC;

-- Readmission rates by facility type and specialty
SELECT 
    facility_type,
    specialty,
    COUNT(*) as total_patients,
    AVG(readmission_30_days) * 100 as readmission_rate,
    AVG(length_of_stay) as avg_length_of_stay
FROM patients p
JOIN facilities f ON p.facility_id = f.facility_id
GROUP BY facility_type, specialty
HAVING COUNT(*) >= 5
ORDER BY readmission_rate DESC;

-- 4. INSURANCE AND COST ANALYSIS

-- Insurance type analysis
SELECT 
    insurance_type,
    COUNT(*) as patient_count,
    AVG(age) as avg_age,
    AVG(length_of_stay) as avg_length_of_stay,
    AVG(readmission_30_days) * 100 as readmission_rate,
    (SELECT AVG(cost) FROM treatments t 
     JOIN patients p2 ON t.patient_id = p2.patient_id 
     WHERE p2.insurance_type = p.insurance_type) as avg_treatment_cost
FROM patients p
GROUP BY insurance_type
ORDER BY patient_count DESC;

-- Cost by insurance type and condition
SELECT 
    p.insurance_type,
    p.primary_condition,
    COUNT(*) as patient_count,
    AVG(t.cost) as avg_treatment_cost,
    SUM(t.cost) as total_cost
FROM patients p
JOIN treatments t ON p.patient_id = t.patient_id
GROUP BY p.insurance_type, p.primary_condition
HAVING COUNT(*) >= 5
ORDER BY total_cost DESC;

-- 5. OPERATIONAL EFFICIENCY QUERIES

-- Monthly patient volume and metrics
SELECT 
    DATE_TRUNC('month', admission_date) as month,
    COUNT(*) as admission_count,
    AVG(length_of_stay) as avg_length_of_stay,
    AVG(readmission_30_days) * 100 as readmission_rate,
    (SELECT COUNT(*) FROM treatments t 
     WHERE DATE_TRUNC('month', t.treatment_date) = DATE_TRUNC('month', p.admission_date)) as treatment_count
FROM patients p
GROUP BY DATE_TRUNC('month', admission_date)
ORDER BY month;

-- Facility utilization analysis
SELECT 
    f.facility_name,
    f.bed_capacity,
    COUNT(p.patient_id) as total_patients,
    COUNT(p.patient_id) * 100.0 / f.bed_capacity as utilization_rate,
    AVG(p.length_of_stay) as avg_length_of_stay
FROM facilities f
LEFT JOIN patients p ON f.facility_id = p.facility_id
GROUP BY f.facility_id, f.facility_name, f.bed_capacity
ORDER BY utilization_rate DESC;

-- 6. HIGH-RISK PATIENT IDENTIFICATION

-- Patients with multiple risk factors
SELECT 
    p.patient_id,
    p.age,
    p.primary_condition,
    p.insurance_type,
    p.readmission_30_days,
    COUNT(t.treatment_id) as treatment_count,
    AVG(t.cost) as avg_treatment_cost,
    p.length_of_stay
FROM patients p
JOIN treatments t ON p.patient_id = t.patient_id
WHERE p.readmission_30_days = 1
    OR p.length_of_stay > 30
    OR (SELECT AVG(cost) FROM treatments t2 WHERE t2.patient_id = p.patient_id) > 10000
GROUP BY p.patient_id, p.age, p.primary_condition, p.insurance_type, p.readmission_30_days, p.length_of_stay
ORDER BY treatment_count DESC
LIMIT 20;

-- 7. TREATMENT OUTCOME PREDICTORS

-- Factors affecting treatment success
SELECT 
    p.age_group,
    p.primary_condition,
    t.treatment_type,
    COUNT(*) as total_treatments,
    SUM(CASE WHEN t.outcome = 'Successful' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate,
    AVG(t.cost) as avg_cost,
    AVG(t.duration_days) as avg_duration
FROM treatments t
JOIN (
    SELECT 
        patient_id,
        primary_condition,
        CASE 
            WHEN age < 30 THEN 'Under 30'
            WHEN age BETWEEN 30 AND 50 THEN '30-50'
            WHEN age BETWEEN 51 AND 70 THEN '51-70'
            ELSE 'Over 70'
        END as age_group
    FROM patients
) p ON t.patient_id = p.patient_id
GROUP BY p.age_group, p.primary_condition, t.treatment_type
HAVING COUNT(*) >= 5
ORDER BY success_rate DESC;

-- 8. COST OPTIMIZATION OPPORTUNITIES

-- High-cost treatments with poor outcomes
SELECT 
    treatment_type,
    outcome,
    COUNT(*) as treatment_count,
    AVG(cost) as average_cost,
    AVG(duration_days) as average_duration,
    SUM(cost) as total_cost
FROM treatments
WHERE cost > (SELECT AVG(cost) * 1.5 FROM treatments)  -- 50% above average cost
GROUP BY treatment_type, outcome
HAVING outcome IN ('No Change', 'Worsened')
ORDER BY total_cost DESC;

-- Facilities with highest treatment costs
SELECT 
    f.facility_name,
    f.facility_type,
    COUNT(t.treatment_id) as treatment_count,
    AVG(t.cost) as avg_treatment_cost,
    SUM(t.cost) as total_cost,
    AVG(t.duration_days) as avg_duration
FROM facilities f
JOIN patients p ON f.facility_id = p.facility_id
JOIN treatments t ON p.patient_id = t.patient_id
GROUP BY f.facility_id, f.facility_name, f.facility_type
HAVING COUNT(t.treatment_id) >= 10
ORDER BY avg_treatment_cost DESC
LIMIT 10;