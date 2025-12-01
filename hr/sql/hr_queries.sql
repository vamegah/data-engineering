-- HR Analytics - Business Intelligence Queries
-- Comprehensive SQL queries for HR attrition analysis

-- 1. BASIC ATTRIITION OVERVIEW
SELECT 
    COUNT(*) as total_employees,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) as employees_left,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as attrition_rate,
    AVG(salary) as avg_salary,
    AVG(tenure) as avg_tenure
FROM employees;

-- 2. ATTRITION BY DEPARTMENT WITH KEY METRICS
SELECT 
    department,
    COUNT(*) as total_employees,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) as employees_left,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as attrition_rate,
    ROUND(AVG(salary), 2) as avg_salary,
    ROUND(AVG(job_satisfaction), 2) as avg_job_satisfaction,
    ROUND(AVG(performance_rating), 2) as avg_performance,
    SUM(CASE WHEN overtime = 'Yes' THEN 1 ELSE 0 END) as overtime_count
FROM employees
GROUP BY department
ORDER BY attrition_rate DESC;

-- 3. EMPLOYEE TENURE ANALYSIS
SELECT 
    tenure_group,
    COUNT(*) as total_employees,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) as employees_left,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as attrition_rate,
    ROUND(AVG(salary), 2) as avg_salary
FROM (
    SELECT *,
        CASE 
            WHEN tenure <= 2 THEN '0-2 years'
            WHEN tenure <= 5 THEN '3-5 years' 
            WHEN tenure <= 10 THEN '6-10 years'
            ELSE '10+ years'
        END as tenure_group
    FROM employees
) grouped
GROUP BY tenure_group
ORDER BY MIN(tenure);

-- 4. SALARY ANALYSIS BY ATTRITION STATUS
SELECT 
    salary_category,
    COUNT(*) as total_employees,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) as employees_left,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as attrition_rate
FROM (
    SELECT *,
        CASE 
            WHEN salary < 50000 THEN 'Low (<50k)'
            WHEN salary < 80000 THEN 'Medium (50-80k)'
            WHEN salary < 120000 THEN 'High (80-120k)'
            ELSE 'Very High (>120k)'
        END as salary_category
    FROM employees
) salary_groups
GROUP BY salary_category
ORDER BY MIN(salary);

-- 5. JOB SATISFACTION AND PERFORMANCE CORRELATION
SELECT 
    job_satisfaction,
    performance_rating,
    COUNT(*) as employee_count,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) as employees_left,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as attrition_rate,
    ROUND(AVG(salary), 2) as avg_salary
FROM employees
GROUP BY job_satisfaction, performance_rating
ORDER BY job_satisfaction, performance_rating;

-- 6. OVERTIME IMPACT ANALYSIS
SELECT 
    overtime,
    COUNT(*) as total_employees,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) as employees_left,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as attrition_rate,
    ROUND(AVG(salary), 2) as avg_salary,
    ROUND(AVG(job_satisfaction), 2) as avg_satisfaction
FROM employees
GROUP BY overtime;

-- 7. EDUCATION AND ATTRITION ANALYSIS
SELECT 
    education,
    education_field,
    COUNT(*) as total_employees,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) as employees_left,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as attrition_rate,
    ROUND(AVG(salary), 2) as avg_salary
FROM employees
GROUP BY education, education_field
ORDER BY education, attrition_rate DESC;

-- 8. MONTHLY ATTRITION TREND (Using exit interviews)
SELECT 
    TO_CHAR(exit_date, 'YYYY-MM') as exit_month,
    COUNT(*) as employees_left,
    reason,
    ROUND(AVG(satisfaction_score), 2) as avg_satisfaction
FROM exit_interviews
GROUP BY TO_CHAR(exit_date, 'YYYY-MM'), reason
ORDER BY exit_month, employees_left DESC;

-- 9. DEPARTMENT PERFORMANCE vs ATTRITION
SELECT 
    department,
    ROUND(AVG(performance_rating), 2) as avg_performance,
    ROUND(AVG(job_satisfaction), 2) as avg_satisfaction,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) as employees_left,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as attrition_rate,
    -- Performance-Attrition Ratio (higher is better)
    ROUND(AVG(performance_rating) / NULLIF(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 0), 2) as performance_attrition_ratio
FROM employees
GROUP BY department
ORDER BY performance_attrition_ratio DESC;

-- 10. EMPLOYEE SEGMENTATION FOR TARGETED INTERVENTIONS
SELECT 
    segment,
    COUNT(*) as employee_count,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) as employees_left,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as attrition_rate,
    ROUND(AVG(salary), 2) as avg_salary
FROM (
    SELECT *,
        CASE 
            WHEN tenure < 2 AND job_satisfaction <= 2 THEN 'New & Unhappy'
            WHEN tenure >= 5 AND salary < 60000 THEN 'Experienced & Underpaid'
            WHEN overtime = 'Yes' AND job_satisfaction <= 2 THEN 'Overworked & Unhappy'
            WHEN performance_rating >= 4 AND salary < 80000 THEN 'High Performer & Underpaid'
            ELSE 'Stable'
        END as segment
    FROM employees
) segmented
GROUP BY segment
ORDER BY attrition_rate DESC;

-- 11. EXIT REASON ANALYSIS
SELECT 
    reason,
    COUNT(*) as exit_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM exit_interviews), 2) as percentage,
    ROUND(AVG(satisfaction_score), 2) as avg_satisfaction,
    ROUND(AVG((SELECT tenure FROM employees e WHERE e.employee_id = exit_interviews.employee_id)), 2) as avg_tenure
FROM exit_interviews
GROUP BY reason
ORDER BY exit_count DESC;

-- 12. COST OF ATTRITION ESTIMATION
SELECT 
    department,
    COUNT(*) as total_employees,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) as employees_left,
    ROUND(AVG(salary), 2) as avg_salary,
    -- Estimated cost: 50% of annual salary per employee (recruitment, training, lost productivity)
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN salary * 0.5 ELSE 0 END), 2) as estimated_attrition_cost
FROM employees
GROUP BY department
ORDER BY estimated_attrition_cost DESC;

-- 13. RETENTION OPPORTUNITY ANALYSIS
-- Employees at high risk of leaving (based on predictive model factors)
SELECT 
    'High Risk' as risk_category,
    COUNT(*) as employee_count,
    ROUND(AVG(salary), 2) as avg_salary,
    ROUND(AVG(job_satisfaction), 2) as avg_satisfaction,
    SUM(CASE WHEN overtime = 'Yes' THEN 1 ELSE 0 END) as overtime_count,
    ROUND(SUM(CASE WHEN overtime = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as overtime_percentage
FROM employees
WHERE 
    job_satisfaction <= 2 
    OR (tenure < 2 AND performance_rating <= 2)
    OR (overtime = 'Yes' AND job_satisfaction <= 2)
    OR salary < (SELECT AVG(salary) * 0.8 FROM employees);

-- 14. MANAGERIAL INSIGHTS QUERY
SELECT 
    department,
    job_role,
    COUNT(*) as team_size,
    SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) as turnover_count,
    ROUND(SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as turnover_rate,
    ROUND(AVG(performance_rating), 2) as team_performance,
    ROUND(AVG(job_satisfaction), 2) as team_satisfaction,
    ROUND(AVG(salary), 2) as avg_salary,
    -- Flag departments needing attention
    CASE 
        WHEN SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) > 15 THEN 'HIGH PRIORITY'
        WHEN SUM(CASE WHEN attrition = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) > 10 THEN 'MEDIUM PRIORITY'
        ELSE 'LOW PRIORITY'
    END as priority_level
FROM employees
GROUP BY department, job_role
HAVING COUNT(*) >= 5  -- Only show roles with meaningful team sizes
ORDER BY turnover_rate DESC, team_size DESC;