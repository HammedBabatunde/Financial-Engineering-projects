-- 1. Drop existing tables if they exist to allow clean re-runs
-- We drop financial_statements first because it references the companies table
DROP TABLE IF EXISTS financial_statements CASCADE;
DROP TABLE IF EXISTS companies CASCADE;
DROP TABLE IF EXISTS exchange_rates CASCADE;

-- 2. Create the exchange_rates table to store daily currency prices
CREATE TABLE exchange_rates (
    rate_date DATE PRIMARY KEY,
    usd_to_ngn_rate DOUBLE PRECISION NOT NULL,
    ngn_to_usd_rate DOUBLE PRECISION NOT NULL,
    daily_return DOUBLE PRECISION,
    sma_30 DOUBLE PRECISION,
    sma_90 DOUBLE PRECISION,
    rolling_vol_30d DOUBLE PRECISION,
    annualized_vol_30d DOUBLE PRECISION
);

-- 3. Create the companies metadata table
CREATE TABLE companies (
    ticker VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    reporting_currency VARCHAR(5) NOT NULL
);

-- 4. Create the financial_statements table referencing the companies table
CREATE TABLE financial_statements (
    statement_id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_period VARCHAR(10) NOT NULL, -- e.g., 'FY', 'Q1', 'H1'
    revenue DOUBLE PRECISION,
    cost_of_sales DOUBLE PRECISION,
    operating_profit DOUBLE PRECISION,
    net_profit DOUBLE PRECISION,
    total_assets DOUBLE PRECISION,
    total_liabilities DOUBLE PRECISION,
    current_assets DOUBLE PRECISION,
    current_liabilities DOUBLE PRECISION,
    cash_and_equivalents DOUBLE PRECISION,
    fx_translation_loss DOUBLE PRECISION, -- naira translation impact
    FOREIGN KEY (ticker) REFERENCES companies(ticker) ON DELETE CASCADE,
    UNIQUE (ticker, fiscal_year, fiscal_period) -- Ensures you don't input duplicates for the same period
);
