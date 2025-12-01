-- Banking Project Database Schema
-- Creates tables for customer churn prediction analysis

-- Customers table
CREATE TABLE IF NOT EXISTS banking_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    credit_score INTEGER,
    country VARCHAR(50),
    gender VARCHAR(10),
    age INTEGER,
    tenure INTEGER,
    balance DECIMAL(15,2),
    products_number INTEGER,
    credit_card INTEGER,
    active_member INTEGER,
    estimated_salary DECIMAL(15,2),
    churn INTEGER
);

-- Transactions table
CREATE TABLE IF NOT EXISTS banking_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    transaction_type VARCHAR(50),
    amount DECIMAL(15,2),
    date DATE,
    merchant VARCHAR(100),
    location VARCHAR(50),
    is_fraudulent INTEGER,
    FOREIGN KEY (customer_id) REFERENCES banking_customers(customer_id)
);

-- Create indexes for better performance
CREATE INDEX idx_customers_churn ON banking_customers(churn);
CREATE INDEX idx_customers_country ON banking_customers(country);
CREATE INDEX idx_transactions_customer ON banking_transactions(customer_id);
CREATE INDEX idx_transactions_date ON banking_transactions(date);
CREATE INDEX idx_transactions_fraud ON banking_transactions(is_fraudulent);

-- Enriched view for analysis
CREATE OR REPLACE VIEW banking_customer_analytics AS
SELECT 
    c.*,
    COUNT(t.transaction_id) as transaction_count,
    AVG(t.amount) as avg_transaction_amount,
    MIN(t.date) as first_transaction_date,
    MAX(t.date) as last_transaction_date,
    SUM(CASE WHEN t.is_fraudulent = 1 THEN 1 ELSE 0 END) as fraudulent_transactions
FROM banking_customers c
LEFT JOIN banking_transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.credit_score, c.country, c.gender, c.age, c.tenure, 
         c.balance, c.products_number, c.credit_card, c.active_member, 
         c.estimated_salary, c.churn;

-- Sample data validation query
SELECT 
    COUNT(*) as total_customers,
    AVG(churn) as churn_rate,
    AVG(balance) as avg_balance,
    AVG(credit_score) as avg_credit_score
FROM banking_customers;