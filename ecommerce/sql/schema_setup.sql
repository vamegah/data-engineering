-- E-commerce Database Schema
-- Creates tables for customers, products, and transactions

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    signup_date DATE,
    location VARCHAR(100),
    tier VARCHAR(50)
);

-- Products table  
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(100),
    price DECIMAL(10,2),
    cost DECIMAL(10,2)
);

-- Transactions table
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    date DATE,
    quantity INTEGER,
    region VARCHAR(50),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_region ON transactions(region);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_customers_location ON customers(location);

-- Enriched view for business analysis
CREATE OR REPLACE VIEW sales_analysis_view AS
SELECT 
    t.transaction_id,
    t.date,
    t.quantity,
    t.region,
    c.customer_id,
    c.location as customer_location,
    c.tier as customer_tier,
    c.signup_date,
    p.product_id,
    p.product_name,
    p.category,
    p.price,
    p.cost,
    (t.quantity * p.price) as revenue,
    (t.quantity * (p.price - p.cost)) as profit
FROM transactions t
JOIN customers c ON t.customer_id = c.customer_id
JOIN products p ON t.product_id = p.product_id;

-- Monthly sales summary view
CREATE OR REPLACE VIEW monthly_sales_summary AS
SELECT
    DATE_TRUNC('month', t.date) as month,
    COUNT(DISTINCT t.customer_id) as unique_customers,
    COUNT(t.transaction_id) as total_transactions,
    SUM(t.quantity) as total_quantity,
    SUM(t.quantity * p.price) as total_revenue,
    AVG(t.quantity * p.price) as avg_transaction_value
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY DATE_TRUNC('month', t.date)
ORDER BY month;