-- Financial Stock Analysis - Business Queries
-- SQL queries for stock market analysis and insights

-- 1. BASIC STOCK INFORMATION
-- Get all stocks with their latest price
SELECT 
    s.symbol,
    s.company_name,
    s.sector,
    s.market_cap,
    sp.date as latest_date,
    sp.close as latest_price,
    sp.volume
FROM stocks s
JOIN stock_prices sp ON s.stock_id = sp.stock_id
WHERE sp.date = (SELECT MAX(date) FROM stock_prices WHERE stock_id = s.stock_id)
ORDER BY sp.close DESC;

-- 2. DAILY PRICE MOVEMENTS
-- Stocks with highest daily gains
SELECT 
    symbol,
    company_name,
    date,
    close,
    daily_return_pct
FROM daily_returns
WHERE date = (SELECT MAX(date) FROM stock_prices)
ORDER BY daily_return_pct DESC
LIMIT 10;

-- 3. SECTOR PERFORMANCE ANALYSIS
-- Compare sectors by average return and volatility
SELECT 
    sector,
    COUNT(*) as stock_count,
    ROUND(AVG(daily_return_pct), 2) as avg_daily_return,
    ROUND(STDDEV(daily_return_pct), 2) as volatility,
    ROUND(MIN(daily_return_pct), 2) as worst_return,
    ROUND(MAX(daily_return_pct), 2) as best_return
FROM daily_returns
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY sector
ORDER BY avg_daily_return DESC;

-- 4. VOLUME ANALYSIS
-- Most actively traded stocks
SELECT 
    s.symbol,
    s.company_name,
    s.sector,
    AVG(sp.volume) as avg_volume,
    MAX(sp.volume) as max_volume
FROM stock_prices sp
JOIN stocks s ON sp.stock_id = s.stock_id
WHERE sp.date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY s.symbol, s.company_name, s.sector
ORDER BY avg_volume DESC
LIMIT 15;

-- 5. TECHNICAL INDICATORS
-- Calculate Simple Moving Averages (SMA)
WITH price_data AS (
    SELECT 
        sp.stock_id,
        s.symbol,
        sp.date,
        sp.close,
        AVG(sp.close) OVER (
            PARTITION BY sp.stock_id 
            ORDER BY sp.date 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) as sma_20,
        AVG(sp.close) OVER (
            PARTITION BY sp.stock_id 
            ORDER BY sp.date 
            ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
        ) as sma_50
    FROM stock_prices sp
    JOIN stocks s ON sp.stock_id = s.stock_id
    WHERE sp.date >= CURRENT_DATE - INTERVAL '90 days'
)
SELECT 
    symbol,
    date,
    close,
    ROUND(sma_20, 2) as sma_20,
    ROUND(sma_50, 2) as sma_50,
    CASE WHEN close > sma_20 THEN 'Above SMA20' ELSE 'Below SMA20' END as sma_20_signal,
    CASE WHEN close > sma_50 THEN 'Above SMA50' ELSE 'Below SMA50' END as sma_50_signal
FROM price_data
WHERE date = (SELECT MAX(date) FROM stock_prices)
ORDER BY symbol;

-- 6. CORRELATION ANALYSIS
-- Find stocks with high correlation (example for 2 stocks)
WITH stock_returns AS (
    SELECT 
        date,
        symbol,
        daily_return_pct
    FROM daily_returns
    WHERE date >= CURRENT_DATE - INTERVAL '90 days'
        AND symbol IN ('S100', 'S101')
),
pivot_returns AS (
    SELECT 
        date,
        MAX(CASE WHEN symbol = 'S100' THEN daily_return_pct END) as return_S100,
        MAX(CASE WHEN symbol = 'S101' THEN daily_return_pct END) as return_S101
    FROM stock_returns
    GROUP BY date
)
SELECT 
    ROUND(CORR(return_S100, return_S101)::numeric, 4) as correlation_coefficient
FROM pivot_returns;

-- 7. PORTFOLIO PERFORMANCE SIMULATION
-- Calculate portfolio value over time
WITH portfolio_stocks AS (
    SELECT 
        sp.stock_id,
        sp.date,
        sp.close,
        p.quantity,
        (sp.close * p.quantity) as position_value
    FROM stock_prices sp
    JOIN portfolio p ON sp.stock_id = p.stock_id
    WHERE sp.date >= p.purchase_date
),
portfolio_daily AS (
    SELECT 
        date,
        SUM(position_value) as total_value
    FROM portfolio_stocks
    GROUP BY date
)
SELECT 
    date,
    total_value,
    ROUND(((total_value - LAG(total_value) OVER (ORDER BY date)) / 
          LAG(total_value) OVER (ORDER BY date)) * 100, 2) as daily_change_pct,
    ROUND((total_value - FIRST_VALUE(total_value) OVER (ORDER BY date)) / 
          FIRST_VALUE(total_value) OVER (ORDER BY date) * 100, 2) as total_return_pct
FROM portfolio_daily
ORDER BY date;

-- 8. RISK ANALYSIS
-- Calculate Value at Risk (VaR) approximation
WITH returns_data AS (
    SELECT 
        symbol,
        date,
        daily_return_pct,
        PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY daily_return_pct) 
            OVER (PARTITION BY symbol) as var_95
    FROM daily_returns
    WHERE date >= CURRENT_DATE - INTERVAL '252 days'  -- 1 trading year
)
SELECT 
    symbol,
    ROUND(MIN(var_95), 2) as daily_var_95,
    ROUND(MIN(var_95) * SQRT(30), 2) as monthly_var_95
FROM returns_data
GROUP BY symbol
ORDER BY daily_var_95
LIMIT 10;