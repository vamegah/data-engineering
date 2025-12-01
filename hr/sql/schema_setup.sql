-- HR Analytics Database Schema
-- Employee attrition analysis tables

-- Employees table
CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR(50) PRIMARY KEY,
    department VARCHAR(100),
    job_role VARCHAR(100),
    education VARCHAR(50),
    education_field VARCHAR(100),
    gender VARCHAR(20),
    age INTEGER,
    tenure INTEGER,
    salary DECIMAL(10,2),
    bonus DECIMAL(10,2),
    job_satisfaction INTEGER,
    performance_rating INTEGER,
    overtime VARCHAR(10),
    marital_status VARCHAR(20),
    distance_from_home DECIMAL(5,1),
    attrition VARCHAR(10)
);

-- Exit interviews table
CREATE TABLE IF NOT EXISTS exit_interviews (
    employee_id VARCHAR(50) PRIMARY KEY,
    exit_date DATE,
    reason VARCHAR(100),
    satisfaction_score INTEGER,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department);
CREATE INDEX IF NOT EXISTS idx_employees_attrition ON employees(attrition);
CREATE INDEX IF NOT EXISTS idx_employees_tenure ON employees(tenure);
CREATE INDEX IF NOT EXISTS idx_exit_interviews_date ON exit_interviews(exit_date);

-- Create a view for attrition analysis
CREATE OR REPLACE VIEW attrition_analysis AS
SELECT 
    e.*,
    ei.exit_date,
    ei.reason as exit_reason,
    ei.satisfaction_score as exit_satisfaction,
    CASE 
        WHEN e.attrition = 'Yes' THEN 1 
        ELSE 0 
    END as attrition_flag
FROM employees e
LEFT JOIN exit_interviews ei ON e.employee_id = ei.employee_id;