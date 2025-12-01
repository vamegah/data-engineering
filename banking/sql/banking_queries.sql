-- Banking Business Intelligence Queries
-- Essential SQL queries for customer churn analysis and business insights

-- 1. OVERVIEW AND KEY METRICS
-- Overall churn rate and key metrics
SELECT 
    COUNT(*) as total_customers,
    SUM(churn) as churned_customers,
    ROUND(AVG(churn) * 100, 2) as churn_rate,
    ROUND(AVG(credit_score), 2) as avg_credit_score,
    ROUND(AVG(balance), 2) as avg_balance,
    ROUND(AVG(estimated_salary), 2) as avg_salary,
    ROUND(AVG(age), 2) as avg_age
FROM banking_customers;

-- 2. CUSTOMER SEGMENTATION ANALYSIS
-- 2.1 Churn rate by different segments
SELECT 
    country,
    COUNT(*) as total_customers,
    SUM(churn) as churned_customers,
    ROUND(AVG(churn) * 100, 2) as churn_rate,
    ROUND(AVG(balance), 2) as avg_balance
FROM banking_customers
GROUP BY country
ORDER BY churn_rate DESC;

-- 2.2 Churn by number of products
SELECT 
    products_number,
    COUNT(*) as total_customers,
    SUM(churn) as churned_customers,
    ROUND(AVG(churn) * 100, 2) as churn_rate,
    ROUND(AVG(balance), 2) as avg_balance
FROM banking_customers
GROUP BY products_number
ORDER BY products_number;

-- 2.3 Churn by active member status
SELECT 
    CASE 
        WHEN active_member = 1 THEN 'Active' 
        ELSE 'Inactive' 
    END as member_status,
    COUNT(*) as total_customers,
    SUM(churn) as churned_customers,
    ROUND(AVG(churn) * 100, 2) as churn_rate
FROM banking_customers
GROUP BY active_member
ORDER BY churn_rate DESC;

-- 3. DEMOGRAPHIC ANALYSIS
-- 3.1 Age groups analysis
SELECT 
    CASE 
        WHEN age < 30 THEN 'Under 30'
        WHEN age BETWEEN 30 AND 40 THEN '30-40'
        WHEN age BETWEEN 40 AND 50 THEN '40-50'
        WHEN age BETWEEN 50 AND 60 THEN '50-60'
        ELSE 'Over 60'
    END as age_group,
    COUNT(*) as total_customers,
    SUM(churn) as churned_customers,
    ROUND(AVG(churn) * 100, 2) as churn_rate,
    ROUND(AVG(balance), 2) as avg_balance
FROM banking_customers
GROUP BY age_group
ORDER BY MIN(age);

-- 3.2 Credit score tiers
SELECT 
    CASE 
        WHEN credit_score < 580 THEN 'Poor (<580)'
        WHEN credit_score BETWEEN 580 AND 669 THEN 'Fair (580-669)'
        WHEN credit_score BETWEEN 670 AND 739 THEN 'Good (670-739)'
        WHEN credit_score BETWEEN 740 AND 799 THEN 'Very Good (740-799)'
        ELSE 'Excellent (800+)'
    END as credit_tier,
    COUNT(*) as total_customers,
    SUM(churn) as churned_customers,
    ROUND(AVG(churn) * 100, 2) as churn_rate
FROM banking_customers
GROUP BY credit_tier
ORDER BY MIN(credit_score);

-- 4. FINANCIAL ANALYSIS
-- 4.1 Balance distribution and churn
SELECT 
    CASE 
        WHEN balance = 0 THEN 'Zero Balance'
        WHEN balance < 1000 THEN 'Low (<1K)'
        WHEN balance < 10000 THEN 'Medium (1K-10K)'
        WHEN balance < 50000 THEN 'High (10K-50K)'
        ELSE 'Very High (50K+)'
    END as balance_tier,
    COUNT(*) as total_customers,
    SUM(churn) as churned_customers,
    ROUND(AVG(churn) * 100, 2) as churn_rate,
    ROUND(AVG(balance), 2) as avg_balance
FROM banking_customers
GROUP BY balance_tier
ORDER BY MIN(balance);

-- 4.2 Salary segments
SELECT 
    CASE 
        WHEN estimated_salary < 30000 THEN 'Low (<30K)'
        WHEN estimated_salary BETWEEN 30000 AND 60000 THEN 'Medium (30K-60K)'
        WHEN estimated_salary BETWEEN 60000 AND 100000 THEN 'High (60K-100K)'
        ELSE 'Very High (100K+)'
    END as salary_segment,
    COUNT(*) as total_customers,
    SUM(churn) as churned_customers,
    ROUND(AVG(churn) * 100, 2) as churn_rate
FROM banking_customers
GROUP BY salary_segment
ORDER BY MIN(estimated_salary);

-- 5. TRANSACTION ANALYSIS
-- 5.1 Transaction patterns by churn status
SELECT 
    c.churn,
    COUNT(t.transaction_id) as total_transactions,
    ROUND(AVG(t.amount), 2) as avg_transaction_amount,
    COUNT(DISTINCT t.customer_id) as active_customers,
    SUM(CASE WHEN t.is_fraudulent = 1 THEN 1 ELSE 0 END) as fraudulent_transactions,
    ROUND(SUM(CASE WHEN t.is_fraudulent = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(t.transaction_id), 4) as fraud_rate
FROM banking_customers c
LEFT JOIN banking_transactions t ON c.customer_id = t.customer_id
GROUP BY c.churn;

-- 5.2 Transaction types analysis
SELECT 
    transaction_type,
    COUNT(*) as transaction_count,
    ROUND(AVG(amount), 2) as avg_amount,
    SUM(CASE WHEN is_fraudulent = 1 THEN 1 ELSE 0 END) as fraudulent_count,
    COUNT(DISTINCT customer_id) as unique_customers
FROM banking_transactions
GROUP BY transaction_type
ORDER BY transaction_count DESC;

-- 6. HIGH-RISK CUSTOMER IDENTIFICATION
-- 6.1 High-value customers at risk (top 20 by balance who churned)
SELECT 
    customer_id,
    credit_score,
    age,
    balance,
    estimated_salary,
    products_number,
    country
FROM banking_customers
WHERE churn = 1
ORDER BY balance DESC
LIMIT 20;

-- 6.2 Customers with multiple risk factors
SELECT 
    customer_id,
    credit_score,
    age,
    balance,
    products_number,
    active_member,
    country,
    CASE 
        WHEN credit_score < 600 THEN 1 ELSE 0 
    END + 
    CASE 
        WHEN balance < 1000 THEN 1 ELSE 0 
    END + 
    CASE 
        WHEN active_member = 0 THEN 1 ELSE 0 
    END as risk_score
FROM banking_customers
WHERE churn = 0  -- Currently retained but at risk
ORDER BY risk_score DESC, balance DESC
LIMIT 20;

-- 7. RETENTION OPPORTUNITIES
-- 7.1 Inactive members with high balances
SELECT 
    customer_id,
    credit_score,
    age,
    balance,
    estimated_salary,
    country
FROM banking_customers
WHERE active_member = 0 
    AND churn = 0
    AND balance > 10000
ORDER BY balance DESC
LIMIT 15;

-- 7.2 Customers with single product but good profile
SELECT 
    customer_id,
    credit_score,
    age,
    balance,
    estimated_salary,
    country
FROM banking_customers
WHERE products_number = 1 
    AND churn = 0
    AND credit_score > 700
    AND balance > 5000
ORDER BY estimated_salary DESC
LIMIT 15;

-- 8. FRAUD ANALYSIS
-- 8.1 Fraud patterns by customer segments
SELECT 
    c.country,
    c.products_number,
    COUNT(t.transaction_id) as total_transactions,
    SUM(t.is_fraudulent) as fraudulent_transactions,
    ROUND(SUM(t.is_fraudulent) * 100.0 / COUNT(t.transaction_id), 4) as fraud_rate,
    ROUND(AVG(t.amount), 2) as avg_transaction_amount
FROM banking_customers c
JOIN banking_transactions t ON c.customer_id = t.customer_id
GROUP BY c.country, c.products_number
HAVING COUNT(t.transaction_id) > 10
ORDER BY fraud_rate DESC;

-- 9. MONTHLY TREND ANALYSIS (if date available)
-- 9.1 Monthly churn trend (example - adjust based on actual date column)
/*
SELECT 
    DATE_TRUNC('month', exit_date) as month,
    COUNT(*) as churned_customers,
    ROUND(AVG(balance), 2) as avg_balance
FROM banking_customers
WHERE churn = 1
GROUP BY DATE_TRUNC('month', exit_date)
ORDER BY month;
*/

-- 10. CUSTOMER LIFETIME VALUE ANALYSIS
-- 10.1 Customer value segments
SELECT 
    CASE 
        WHEN estimated_salary < 30000 THEN 'Low Value'
        WHEN estimated_salary BETWEEN 30000 AND 70000 THEN 'Medium Value'
        ELSE 'High Value'
    END as value_segment,
    COUNT(*) as total_customers,
    SUM(churn) as churned_customers,
    ROUND(AVG(churn) * 100, 2) as churn_rate,
    ROUND(AVG(estimated_salary), 2) as avg_salary,
    SUM(estimated_salary) as total_estimated_value
FROM banking_customers
GROUP BY value_segment
ORDER BY total_estimated_value DESC;