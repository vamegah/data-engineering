-- Fraud Detection Database Schema
-- Create tables for fraud detection analysis

-- Users table
CREATE TABLE IF NOT EXISTS fraud_users (
    user_id VARCHAR(50) PRIMARY KEY,
    signup_date DATE,
    location VARCHAR(100),
    device_type VARCHAR(50),
    account_age_days INTEGER
);

-- Transactions table
CREATE TABLE IF NOT EXISTS fraud_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    amount DECIMAL(10,2),
    transaction_date TIMESTAMP,
    category VARCHAR(50),
    merchant VARCHAR(100),
    location VARCHAR(50),
    device_used VARCHAR(50),
    hour_of_day INTEGER,
    is_fraud INTEGER,
    FOREIGN KEY (user_id) REFERENCES fraud_users(user_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_transactions_date ON fraud_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_transactions_user ON fraud_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_fraud ON fraud_transactions(is_fraud);
CREATE INDEX IF NOT EXISTS idx_transactions_amount ON fraud_transactions(amount);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON fraud_transactions(category);

-- Create a view for fraud analysis
CREATE OR REPLACE VIEW fraud_analysis_view AS
SELECT 
    t.*,
    u.signup_date,
    u.account_age_days,
    u.device_type as user_device_type,
    EXTRACT(DOW FROM t.transaction_date) as day_of_week,
    CASE 
        WHEN t.amount > 1000 THEN 'High Value'
        WHEN t.amount > 100 THEN 'Medium Value' 
        ELSE 'Low Value'
    END as amount_category
FROM fraud_transactions t
JOIN fraud_users u ON t.user_id = u.user_id;