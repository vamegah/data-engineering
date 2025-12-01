-- E-commerce Business Intelligence Queries
-- Comprehensive SQL queries for business analysis and reporting

-- 1. BASIC BUSINESS METRICS
-- =========================

-- Total revenue, profit, and transaction count
SELECT 
    COUNT(DISTINCT customer_id) as total_customers,
    COUNT(DISTINCT product_id) as total_products,
    COUNT(transaction_id) as total_transactions,
    SUM(quantity) as total_items_sold,
    ROUND(SUM(quantity * price), 2) as total_revenue,
    ROUND(SUM(quantity * (price - cost)), 2) as total_profit,
    ROUND(AVG(quantity * price), 2) as avg_transaction_value
FROM transactions t
JOIN products p ON t.product_id = p.product_id;

-- 2. MONTHLY PERFORMANCE TRENDS
-- =============================

-- Monthly revenue, profit, and customer metrics
SELECT 
    DATE_TRUNC('month', date) as month,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(transaction_id) as total_transactions,
    SUM(quantity) as total_quantity,
    ROUND(SUM(quantity * price), 2) as total_revenue,
    ROUND(SUM(quantity * (price - cost)), 2) as total_profit,
    ROUND(SUM(quantity * price) / COUNT(transaction_id), 2) as avg_order_value
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY DATE_TRUNC('month', date)
ORDER BY month;

-- 3. CUSTOMER ANALYSIS
-- ====================

-- Customer lifetime value analysis
SELECT 
    customer_id,
    COUNT(transaction_id) as transaction_count,
    SUM(quantity) as total_items,
    ROUND(SUM(quantity * price), 2) as total_spent,
    ROUND(AVG(quantity * price), 2) as avg_order_value,
    MIN(date) as first_purchase,
    MAX(date) as last_purchase,
    (MAX(date) - MIN(date)) as customer_lifetime_days
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 20;

-- Customer segmentation by spending
SELECT 
    CASE 
        WHEN total_spent >= 1000 THEN 'VIP'
        WHEN total_spent >= 500 THEN 'Premium' 
        WHEN total_spent >= 100 THEN 'Standard'
        ELSE 'Budget'
    END as customer_segment,
    COUNT(*) as customer_count,
    ROUND(AVG(total_spent), 2) as avg_spending,
    ROUND(AVG(transaction_count), 2) as avg_transactions
FROM (
    SELECT 
        customer_id,
        COUNT(transaction_id) as transaction_count,
        SUM(quantity * price) as total_spent
    FROM transactions t
    JOIN products p ON t.product_id = p.product_id
    GROUP BY customer_id
) customer_stats
GROUP BY customer_segment
ORDER BY avg_spending DESC;

-- 4. PRODUCT PERFORMANCE
-- ======================

-- Top 20 products by revenue
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.price,
    SUM(t.quantity) as total_quantity,
    ROUND(SUM(t.quantity * p.price), 2) as total_revenue,
    ROUND(SUM(t.quantity * (p.price - p.cost)), 2) as total_profit,
    ROUND((SUM(t.quantity * (p.price - p.cost)) / SUM(t.quantity * p.price)) * 100, 2) as profit_margin
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.price
ORDER BY total_revenue DESC
LIMIT 20;

-- Product category performance
SELECT 
    category,
    COUNT(DISTINCT product_id) as product_count,
    SUM(quantity) as total_quantity,
    ROUND(SUM(quantity * price), 2) as total_revenue,
    ROUND(SUM(quantity * (price - cost)), 2) as total_profit,
    ROUND(AVG(price), 2) as avg_price,
    ROUND((SUM(quantity * (price - cost)) / SUM(quantity * price)) * 100, 2) as avg_profit_margin
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY category
ORDER BY total_revenue DESC;

-- 5. REGIONAL ANALYSIS
-- ====================

-- Regional performance metrics
SELECT 
    region,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(transaction_id) as total_transactions,
    SUM(quantity) as total_quantity,
    ROUND(SUM(quantity * price), 2) as total_revenue,
    ROUND(SUM(quantity * (price - cost)), 2) as total_profit,
    ROUND(SUM(quantity * price) / COUNT(transaction_id), 2) as avg_order_value,
    ROUND(SUM(quantity * price) / COUNT(DISTINCT customer_id), 2) as revenue_per_customer
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY region
ORDER BY total_revenue DESC;

-- 6. TIME-BASED ANALYSIS
-- ======================

-- Daily sales patterns
SELECT 
    EXTRACT(DOW FROM date) as day_of_week,
    CASE EXTRACT(DOW FROM date)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_name,
    COUNT(transaction_id) as transaction_count,
    ROUND(SUM(quantity * price), 2) as total_revenue,
    ROUND(AVG(quantity * price), 2) as avg_order_value
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY day_of_week, day_name
ORDER BY day_of_week;

-- Monthly growth rates
WITH monthly_sales AS (
    SELECT 
        DATE_TRUNC('month', date) as month,
        SUM(quantity * price) as monthly_revenue
    FROM transactions t
    JOIN products p ON t.product_id = p.product_id
    GROUP BY DATE_TRUNC('month', date)
)
SELECT 
    month,
    monthly_revenue,
    LAG(monthly_revenue) OVER (ORDER BY month) as previous_month_revenue,
    ROUND(
        ((monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY month)) / 
        LAG(monthly_revenue) OVER (ORDER BY month)) * 100, 2
    ) as growth_rate_percent
FROM monthly_sales
ORDER BY month;

-- 7. CUSTOMER TIER ANALYSIS
-- =========================

-- Customer tier performance
SELECT 
    c.tier as customer_tier,
    COUNT(DISTINCT t.customer_id) as customer_count,
    COUNT(t.transaction_id) as transaction_count,
    SUM(t.quantity) as total_quantity,
    ROUND(SUM(t.quantity * p.price), 2) as total_revenue,
    ROUND(AVG(t.quantity * p.price), 2) as avg_order_value,
    ROUND(SUM(t.quantity * p.price) / COUNT(DISTINCT t.customer_id), 2) as revenue_per_customer
FROM transactions t
JOIN products p ON t.product_id = p.product_id
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.tier
ORDER BY revenue_per_customer DESC;

-- 8. PRODUCT PRICE SEGMENT ANALYSIS
-- =================================

-- Price segment performance
SELECT 
    CASE 
        WHEN price < 50 THEN 'Budget (<$50)'
        WHEN price < 100 THEN 'Mid-Range ($50-$100)'
        WHEN price < 200 THEN 'Premium ($100-$200)'
        ELSE 'Luxury ($200+)'
    END as price_segment,
    COUNT(DISTINCT p.product_id) as product_count,
    SUM(t.quantity) as total_quantity,
    ROUND(SUM(t.quantity * p.price), 2) as total_revenue,
    ROUND(SUM(t.quantity * (p.price - p.cost)), 2) as total_profit,
    ROUND(AVG(p.price), 2) as avg_price,
    ROUND((SUM(t.quantity * (p.price - p.cost)) / SUM(t.quantity * p.price)) * 100, 2) as profit_margin
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY price_segment
ORDER BY total_revenue DESC;

-- 9. CUSTOMER RETENTION ANALYSIS
-- ==============================

-- Customer acquisition and retention by month
WITH customer_first_purchase AS (
    SELECT 
        customer_id,
        MIN(DATE_TRUNC('month', date)) as first_purchase_month
    FROM transactions
    GROUP BY customer_id
),
monthly_customers AS (
    SELECT 
        DATE_TRUNC('month', date) as month,
        customer_id
    FROM transactions
    GROUP BY DATE_TRUNC('month', date), customer_id
)
SELECT 
    fp.first_purchase_month as cohort,
    mc.month,
    COUNT(DISTINCT mc.customer_id) as active_customers,
    ROUND(
        COUNT(DISTINCT mc.customer_id) * 100.0 / 
        (SELECT COUNT(DISTINCT customer_id) FROM customer_first_purchase WHERE first_purchase_month = fp.first_purchase_month),
        2
    ) as retention_rate
FROM monthly_customers mc
JOIN customer_first_purchase fp ON mc.customer_id = fp.customer_id
GROUP BY fp.first_purchase_month, mc.month
ORDER BY cohort, month;

-- 10. PROFITABILITY DRILL-DOWN
-- ============================

-- Identify most and least profitable products
(SELECT 
    'Most Profitable' as category,
    p.product_name,
    p.category,
    ROUND(SUM(t.quantity * (p.price - p.cost)), 2) as total_profit,
    ROUND((SUM(t.quantity * (p.price - p.cost)) / SUM(t.quantity * p.price)) * 100, 2) as profit_margin
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_profit DESC
LIMIT 10)

UNION ALL

(SELECT 
    'Least Profitable' as category,
    p.product_name,
    p.category,
    ROUND(SUM(t.quantity * (p.price - p.cost)), 2) as total_profit,
    ROUND((SUM(t.quantity * (p.price - p.cost)) / SUM(t.quantity * p.price)) * 100, 2) as profit_margin
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
HAVING SUM(t.quantity) > 10  -- Only consider products with meaningful sales
ORDER BY total_profit ASC
LIMIT 10)

ORDER BY category, total_profit DESC;

-- 11. SEASONAL PRODUCT ANALYSIS
-- =============================

-- Products with strong seasonal patterns
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    EXTRACT(MONTH FROM t.date) as month,
    SUM(t.quantity) as monthly_quantity,
    ROUND(SUM(t.quantity * p.price), 2) as monthly_revenue,
    ROUND(AVG(t.quantity * p.price), 2) as avg_order_value
FROM transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, EXTRACT(MONTH FROM t.date)
HAVING SUM(t.quantity) > 50  -- Only products with significant sales
ORDER BY p.product_id, month;

-- 12. CROSS-SELLING OPPORTUNITIES
-- ===============================

-- Products frequently bought together
WITH product_pairs AS (
    SELECT 
        t1.transaction_id,
        t1.product_id as product1,
        t2.product_id as product2
    FROM transactions t1
    JOIN transactions t2 ON t1.transaction_id = t2.transaction_id AND t1.product_id < t2.product_id
)
SELECT 
    p1.product_name as product_1,
    p2.product_name as product_2,
    p1.category as category_1,
    p2.category as category_2,
    COUNT(*) as times_bought_together
FROM product_pairs pp
JOIN products p1 ON pp.product1 = p1.product_id
JOIN products p2 ON pp.product2 = p2.product_id
GROUP BY p1.product_name, p2.product_name, p1.category, p2.category
HAVING COUNT(*) > 5
ORDER BY times_bought_together DESC
LIMIT 20;