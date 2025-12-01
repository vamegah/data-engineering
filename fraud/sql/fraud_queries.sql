-- Fraud Detection Business Queries
-- SQL queries for fraud analysis and insights

-- 1. Basic Fraud Statistics
SELECT 
    COUNT(*) as total_transactions,
    SUM(is_fraud) as fraud_cases,
    ROUND(AVG(is_fraud) * 100, 2) as fraud_rate_percent,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END), 2) as total_fraud_amount,
    ROUND(AVG(CASE WHEN is_fraud = 1 THEN amount ELSE NULL END), 2) as avg_fraud_amount
FROM fraud_transactions;

-- 2. Fraud by Transaction Category
SELECT 
    category,
    COUNT(*) as total_transactions,
    SUM(is_fraud) as fraud_cases,
    ROUND(AVG(is_fraud) * 100, 2) as fraud_rate_percent,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END), 2) as total_fraud_amount
FROM fraud_transactions
GROUP BY category
ORDER BY fraud_rate_percent DESC;

-- 3. Fraud by Hour of Day
SELECT 
    hour_of_day,
    COUNT(*) as total_transactions,
    SUM(is_fraud) as fraud_cases,
    ROUND(AVG(is_fraud) * 100, 2) as fraud_rate_percent
FROM fraud_transactions
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- 4. Fraud by Location and Device
SELECT 
    location,
    device_used,
    COUNT(*) as total_transactions,
    SUM(is_fraud) as fraud_cases,
    ROUND(AVG(is_fraud) * 100, 2) as fraud_rate_percent
FROM fraud_transactions
GROUP BY location, device_used
ORDER BY fraud_rate_percent DESC;

-- 5. High-Risk Users (Users with multiple fraud cases)
SELECT 
    user_id,
    COUNT(*) as total_transactions,
    SUM(is_fraud) as fraud_cases,
    ROUND(SUM(is_fraud) * 1.0 / COUNT(*) * 100, 2) as fraud_rate_percent,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END), 2) as total_fraud_amount
FROM fraud_transactions
GROUP BY user_id
HAVING SUM(is_fraud) >= 2
ORDER BY fraud_cases DESC, total_fraud_amount DESC;

-- 6. Fraud Pattern by Amount Ranges
SELECT 
    CASE 
        WHEN amount < 50 THEN '0-50'
        WHEN amount < 100 THEN '50-100'
        WHEN amount < 500 THEN '100-500'
        WHEN amount < 1000 THEN '500-1000'
        ELSE '1000+'
    END as amount_range,
    COUNT(*) as total_transactions,
    SUM(is_fraud) as fraud_cases,
    ROUND(AVG(is_fraud) * 100, 2) as fraud_rate_percent,
    ROUND(AVG(amount), 2) as avg_amount
FROM fraud_transactions
GROUP BY amount_range
ORDER BY MIN(amount);

-- 7. Daily Fraud Trends
SELECT 
    DATE(transaction_date) as transaction_day,
    COUNT(*) as total_transactions,
    SUM(is_fraud) as fraud_cases,
    ROUND(AVG(is_fraud) * 100, 2) as fraud_rate_percent
FROM fraud_transactions
GROUP BY DATE(transaction_date)
ORDER BY transaction_day;

-- 8. Merchant Risk Analysis
SELECT 
    merchant,
    COUNT(*) as total_transactions,
    SUM(is_fraud) as fraud_cases,
    ROUND(AVG(is_fraud) * 100, 2) as fraud_rate_percent,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END), 2) as total_fraud_amount
FROM fraud_transactions
GROUP BY merchant
HAVING COUNT(*) >= 10  -- Only merchants with significant volume
ORDER BY fraud_rate_percent DESC
LIMIT 20;

-- 9. User Behavior Patterns for Fraud Detection
SELECT 
    u.user_id,
    u.account_age_days,
    COUNT(t.transaction_id) as transaction_count,
    ROUND(AVG(t.amount), 2) as avg_transaction_amount,
    SUM(t.is_fraud) as fraud_cases,
    CASE 
        WHEN u.account_age_days < 30 THEN 'New User'
        WHEN u.account_age_days < 180 THEN 'Established User'
        ELSE 'Long-term User'
    END as user_segment
FROM fraud_users u
JOIN fraud_transactions t ON u.user_id = t.user_id
GROUP BY u.user_id, u.account_age_days
ORDER BY fraud_cases DESC, transaction_count DESC;

-- 10. Device and Location Combination Risk
SELECT 
    device_used,
    location,
    COUNT(*) as total_transactions,
    SUM(is_fraud) as fraud_cases,
    ROUND(AVG(is_fraud) * 100, 2) as fraud_rate_percent,
    ROUND(AVG(amount), 2) as avg_amount
FROM fraud_transactions
GROUP BY device_used, location
ORDER BY fraud_rate_percent DESC;