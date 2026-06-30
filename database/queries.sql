-- Query 1: Annual Exchange Rate and Volatility Aggregation
SELECT 
    EXTRACT(YEAR FROM rate_date) AS calendar_year,
    AVG(usd_to_ngn_rate) AS average_usd_to_ngn_rate,
    AVG(ngn_to_usd_rate) AS average_ngn_to_usd_rate,
    MAX(annualized_vol_30d) AS peak_annualized_volatility
FROM exchange_rates
GROUP BY calendar_year
ORDER BY calendar_year ASC;


-- Query 2: Join Corporate Financials with Annualized Exchange Rate Metrics
SELECT 
    f.ticker,
    f.fiscal_year,
    f.revenue AS corporate_revenue_ngn,
    f.net_profit AS corporate_net_profit_ngn,
    COALESCE(f.fx_translation_loss, 0) AS reported_fx_loss_ngn, -- Replaces NULL with 0
    e.avg_usd_to_ngn_rate,
    e.peak_annualized_volatility
FROM financial_statements f
INNER JOIN (
    SELECT 
        EXTRACT(YEAR FROM rate_date) AS yr,
        AVG(usd_to_ngn_rate) AS avg_usd_to_ngn_rate,
        MAX(annualized_vol_30d) AS peak_annualized_volatility
    FROM exchange_rates
    GROUP BY yr
) e ON f.fiscal_year = e.yr
WHERE f.ticker = 'PZN'
ORDER BY f.fiscal_year ASC;


-- Query 3: Filtered Join showing Years with >20% Naira Devaluation and Corporate FX Loss Impact
SELECT 
    f.fiscal_year,
    f.revenue AS corporate_revenue_ngn,
    COALESCE(f.fx_translation_loss, 0) AS corporate_fx_loss_ngn, -- Replaces NULL with 0
    e.min_rate AS year_opening_rate,
    e.max_rate AS year_peak_rate,
    ROUND(CAST(e.devaluation_pct AS NUMERIC), 2) AS devaluation_percentage
FROM financial_statements f
INNER JOIN (
    SELECT 
        EXTRACT(YEAR FROM rate_date) AS yr,
        MIN(usd_to_ngn_rate) AS min_rate,
        MAX(usd_to_ngn_rate) AS max_rate,
        ((MAX(usd_to_ngn_rate) - MIN(usd_to_ngn_rate)) / MIN(usd_to_ngn_rate) * 100) AS devaluation_pct
    FROM exchange_rates
    GROUP BY yr
    -- HAVING filters aggregated groups (only keep years where rate devalued > 20%)
    HAVING ((MAX(usd_to_ngn_rate) - MIN(usd_to_ngn_rate)) / MIN(usd_to_ngn_rate) * 100) > 20.0
) e ON f.fiscal_year = e.yr
WHERE f.ticker = 'PZN'
ORDER BY f.fiscal_year DESC;

