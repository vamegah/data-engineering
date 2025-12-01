-- Financial Stock Analysis - Database Schema
-- Run this in PostgreSQL to set up the database tables

-- Stocks master data
CREATE TABLE IF NOT EXISTS stocks (
    stock_id VARCHAR(50) PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(200) NOT NULL,
    sector VARCHAR(100),
    market_cap VARCHAR(50),
    dividend_yield DECIMAL(10,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily stock prices
CREATE TABLE IF NOT EXISTS stock_prices (
    id SERIAL PRIMARY KEY,
    stock_id VARCHAR(50) REFERENCES stocks(stock_id),
    date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Portfolio table for analysis
CREATE TABLE IF NOT EXISTS portfolio (
    id SERIAL PRIMARY KEY,
    stock_id VARCHAR(50) REFERENCES stocks(stock_id),
    purchase_date DATE,
    purchase_price DECIMAL(10,2),
    quantity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON stock_prices(date);
CREATE INDEX IF NOT EXISTS idx_stock_prices_stock_id ON stock_prices(stock_id);
CREATE INDEX IF NOT EXISTS idx_stocks_sector ON stocks(sector);
CREATE INDEX IF NOT EXISTS idx_stocks_market_cap ON stocks(market_cap);

-- Create a view for daily returns
CREATE OR REPLACE VIEW daily_returns AS
SELECT 
    sp.stock_id,
    s.symbol,
    s.company_name,
    s.sector,
    sp.date,
    sp.close,
    LAG(sp.close) OVER (PARTITION BY sp.stock_id ORDER BY sp.date) as prev_close,
    ROUND(((sp.close - LAG(sp.close) OVER (PARTITION BY sp.stock_id ORDER BY sp.date)) / 
          LAG(sp.close) OVER (PARTITION BY sp.stock_id ORDER BY sp.date)) * 100, 2) as daily_return_pct
FROM stock_prices sp
JOIN stocks s ON sp.stock_id = s.stock_id;

-- Create a view for sector performance
CREATE OR REPLACE VIEW sector_performance AS
SELECT 
    s.sector,
    COUNT(DISTINCT s.stock_id) as stock_count,
    ROUND(AVG(sp.close), 2) as avg_price,
    ROUND(MIN(sp.close), 2) as min_price,
    ROUND(MAX(sp.close), 2) as max_price,
    SUM(sp.volume) as total_volume
FROM stocks s
JOIN stock_prices sp ON s.stock_id = sp.stock_id
WHERE sp.date = (SELECT MAX(date) FROM stock_prices)
GROUP BY s.sector;