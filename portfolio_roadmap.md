# Portfolio Project Roadmap: Naira/USD Volatility Tracker & UK Corporate Impact

This document is your step-by-step technical blueprint for building **The Naira/USD Volatility Tracker**. It is designed to combine your learnings from three DataCamp courses:
1. **Manipulating Time Series Data** (Pandas indices, date logic, rolling windows, resample, percent changes).
2. **Intermediate SQL** (Aggregation, grouping, filtering with `WHERE` and `HAVING`, relational joins).
3. **Analyzing Financial Statements in Python** (Balance Sheet liquidity ratios, Income Statement margins, Cash Flow coverage, and foreign exchange impact analysis).

By building this project according to this roadmap, you will have a high-quality portfolio piece ready to publish on GitHub.

---

## 1. Directory Structure

To ensure a clean, professional repository, create the following folder structure in your project folder:

```text
Volatility tracker project/
├── README.md                      # GitHub Repository Landing Page (Template Provided)
├── project_todo.md                 # Your Interactive Checklist (Template Provided)
├── portfolio_roadmap.md           # This document (Technical Specifications)
├── config.env                     # Git-ignored local file containing API keys
├── database/
│   ├── schema.sql                 # SQL script defining your SQLite database schema
│   └── queries.sql                # SQL queries analyzing volatility vs. corporate financials
├── data/
│   ├── raw_exchange_rates.csv     # Daily currency rates downloaded via your API script
│   └── pz_cussons_financials.csv  # Financial statement rows you will extract and save
├── scripts/
│   ├── data_ingestion.py          # Python script to download data from the API
│   ├── db_manager.py              # Python script to load CSV data into SQLite
│   └── calculations_helper.py     # Python script with reusable financial ratio functions
└── analysis_showcase.ipynb        # Master Jupyter Notebook containing all visualizations & analysis
```

---

## 2. API Data Ingestion (Time Series Course)

Your first task is to write a script (`data_ingestion.py`) that pulls daily exchange rate data for NGN/USD. 

### API Selection
* **AlphaVantage**: A standard finance API. 
  * API Function: `FX_DAILY`
  * Parameters: `from_symbol=USD`, `to_symbol=NGN`, `outputsize=full` (to get maximum historical data).
  * API URL structure: `https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=USD&to_symbol=NGN&outputsize=full&apikey=YOUR_API_KEY`
* **Fallback API (ExchangeRate-API)**: If AlphaVantage has rate limits or requires a payment tier for historical USD/NGN, you can use `https://open.er-api.com/v6/latest/USD` (or search for a free historical CSV source like Kaggle/UN database to seed your project if API access is restricted).

### Security Best Practices
Never hardcode your API keys in your Python files.
1. Create a file called `config.env` in your project root folder.
2. In `config.env`, add: `ALPHAVANTAGE_API_KEY=your_actual_key_here`
3. Create a `.gitignore` file and add `config.env` inside it so your key is never pushed to GitHub.
4. In Python, use `python-dotenv` to load the key:
   ```python
   from dotenv import load_dotenv
   import os
   load_dotenv('config.env')
   api_key = os.getenv('ALPHAVANTAGE_API_KEY')
   ```

### Pandas Data Processing
When you load the API response (which will be JSON format) into Pandas:
* **Index Creation**: Convert the date column to a datetime type using `pd.to_datetime()` and set it as your index: `df.index = pd.to_datetime(df['date'])`.
* **Handling Missing Dates**: Financial APIs do not record data on weekends or trading holidays. Use `df = df.asfreq('D')` to introduce null rows for weekends, and then apply `df = df.ffill()` (forward fill) to represent weekend rates with Friday's closing rates. This matches Chapter 1 & 2 of the Time Series course.
* **Saving**: Export this cleaned time series to `data/raw_exchange_rates.csv`.

---

## 3. Relational Storage Schema (Intermediate SQL Course)

Instead of keeping everything in CSVs, you will import your data into an SQLite database (`naira_volatility.db`). This demonstrates database engineering capability.

In `database/schema.sql`, write the SQL definitions to create the following tables.

### Table 1: `exchange_rates`
Stores daily exchange rate data.
```sql
CREATE TABLE exchange_rates (
    rate_date DATE PRIMARY KEY,
    usd_to_ngn_rate REAL NOT NULL,
    daily_return REAL,
    rolling_volatility_30d REAL
);
```

### Table 2: `companies`
Stores company metadata.
```sql
CREATE TABLE companies (
    ticker TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    reporting_currency TEXT NOT NULL
);
```

### Table 3: `financial_statements`
Stores quarterly or annual financial reports. This table links back to the companies table using a foreign key.
```sql
CREATE TABLE financial_statements (
    statement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    fiscal_year INTEGER NOT NULL,
    fiscal_period TEXT NOT NULL, -- e.g., 'FY', 'Q1', 'H1'
    revenue REAL,
    cost_of_sales REAL,
    operating_profit REAL,
    net_profit REAL,
    total_assets REAL,
    total_liabilities REAL,
    current_assets REAL,
    current_liabilities REAL,
    cash_and_equivalents REAL,
    net_cash_from_operations REAL,
    fx_translation_loss REAL, -- Foreign exchange losses reported on the Income Statement or OCI
    FOREIGN KEY (ticker) REFERENCES companies(ticker)
);
```

In `scripts/db_manager.py`, use Python's built-in `sqlite3` library to execute this schema, and use `pandas.DataFrame.to_sql()` with `if_exists='append'` to populate these tables from your data CSVs.

---

## 4. Time Series Analysis & Calculations (Time Series Course)

Inside your Jupyter Notebook (`analysis_showcase.ipynb`), you will run the time-series operations using Pandas.

### Key Calculations to Implement:
1. **Daily Returns ($R_t$)**:
   $$\text{Daily Return} = \frac{\text{Rate}_t - \text{Rate}_{t-1}}{\text{Rate}_{t-1}}$$
   * Pandas implementation: `df['daily_return'] = df['usd_to_ngn_rate'].pct_change()`
2. **Simple Moving Averages (SMA)**:
   * Implement a 30-day and 90-day moving average to smooth short-term trends.
   * Pandas implementation: `df['sma_30'] = df['usd_to_ngn_rate'].rolling(window=30).mean()`
3. **Rolling Volatility**:
   * Volatility is represented as the rolling standard deviation of daily returns.
   * Calculate 30-day rolling standard deviation:
     `df['rolling_vol_30d'] = df['daily_return'].rolling(window=30).std()`
   * Annualize it (multiply by the square root of 252 trading days):
     `df['annualized_vol_30d'] = df['rolling_vol_30d'] * np.sqrt(252)`
4. **Resampling**:
   * Downsample the daily exchange rate data to get quarterly average rates. This is vital because corporate financial statements are published quarterly/annually.
   * Pandas implementation: `df_quarterly = df['usd_to_ngn_rate'].resample('Q').mean()`

---

## 5. UK Corporate Financial Statements Data

To analyze the impact of Naira devaluations on a major global company listed in the United Kingdom, we will use **PZ Cussons plc** (LSE: PZC). 

PZ Cussons is a British personal care and consumer goods multinational headquartered in Manchester. Nigeria is its largest single market. In its recent annual reports (specifically FY23 and FY24), PZ Cussons reported massive foreign exchange translation losses and a significant decline in revenue and operating profits when translating their Nigerian sales back to British Pounds (GBP) due to the floatation/devaluation of the Naira.

### The Real-World Data (GBP Millions)
Create a file called `data/pz_cussons_financials.csv` containing this extracted financial data.

| Year | Period | Revenue | Cost of Sales | Operating Profit | Net Profit | Total Assets | Total Liabilities | Current Assets | Current Liabilities | Cash & Equivalents | FX Translation Loss (Naira impact) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021 | FY | 603.3 | 362.0 | 65.3 | 55.1 | 552.0 | 280.0 | 290.0 | 200.0 | 85.0 | 2.5 |
| 2022 | FY | 592.8 | 358.5 | 66.6 | 58.7 | 565.0 | 275.0 | 305.0 | 195.0 | 90.0 | 4.8 |
| 2023 | FY | 656.3 | 400.1 | 59.4 | 41.2 | 580.0 | 315.0 | 320.0 | 230.0 | 78.0 | 21.0 |
| 2024 | FY | 528.2 | 340.5 | -15.8 | -95.0 | 410.0 | 360.0 | 225.0 | 260.0 | 45.0 | 108.5 |

*(Note: These figures reflect the dramatic impact in FY24, where currency flotation in Nigeria forced a £108.5m translation loss and pushed the company into an operating loss of £15.8m.)*

Add **PZ Cussons** to your database using SQL commands:
* Add PZ Cussons to the `companies` table:
  ```sql
  INSERT INTO companies (ticker, name, country, reporting_currency) 
  VALUES ('PZC', 'PZ Cussons plc', 'United Kingdom', 'GBP');
  ```
* Insert the spreadsheet metrics into the `financial_statements` table matching the schema.

---

## 6. Python-SQL Integration & Custom Queries (Intermediate SQL Course)

Now, practice writing complex SQL queries using Python `sqlite3` and Pandas to retrieve and merge this data. In your notebook, run the following analysis queries:

### Query 1: Calculating Average Exchange Rates and Volatility by Calendar Year
Write a query using SQL aggregates, `GROUP BY`, and `ORDER BY` to summarize the Naira:
```sql
SELECT 
    strftime('%Y', rate_date) AS calendar_year,
    AVG(usd_to_ngn_rate) AS average_rate,
    MIN(usd_to_ngn_rate) AS minimum_rate,
    MAX(usd_to_ngn_rate) AS maximum_rate,
    AVG(rolling_volatility_30d) AS avg_annual_volatility
FROM exchange_rates
GROUP BY calendar_year
ORDER BY calendar_year ASC;
```

### Query 2: Joining FX Volatility and Corporate Profitability
Write a query that joins the daily exchange rate statistics (aggregated by year) with the financial statements of PZ Cussons (`PZC`) using an `INNER JOIN`.
```sql
SELECT 
    f.fiscal_year,
    f.revenue,
    f.operating_profit,
    f.fx_translation_loss,
    e.avg_rate AS avg_naira_rate,
    e.max_vol AS peak_naira_volatility
FROM financial_statements f
INNER JOIN (
    SELECT 
        strftime('%Y', rate_date) AS yr,
        AVG(usd_to_ngn_rate) AS avg_rate,
        MAX(rolling_volatility_30d) AS max_vol
    FROM exchange_rates
    GROUP BY yr
) e ON CAST(f.fiscal_year AS TEXT) = e.yr
WHERE f.ticker = 'PZC'
ORDER BY f.fiscal_year ASC;
```

### Query 3: Identifying High Devaluation Quarters/Years (Intermediate SQL Filter)
Write a query using `HAVING` to find years where the Naira devalued by more than a specified threshold and list the corresponding corporate revenue.
```sql
SELECT 
    f.fiscal_year,
    f.revenue,
    f.fx_translation_loss,
    (e_max.max_rate - e_min.min_rate) / e_min.min_rate * 100 AS devaluation_percentage
FROM financial_statements f
JOIN (
    SELECT strftime('%Y', rate_date) as yr, MIN(usd_to_ngn_rate) as min_rate
    FROM exchange_rates GROUP BY yr
) e_min ON CAST(f.fiscal_year AS TEXT) = e_min.yr
JOIN (
    SELECT strftime('%Y', rate_date) as yr, MAX(usd_to_ngn_rate) as max_rate
    FROM exchange_rates GROUP BY yr
) e_max ON CAST(f.fiscal_year AS TEXT) = e_max.yr
WHERE f.ticker = 'PZC'
GROUP BY f.fiscal_year
HAVING devaluation_percentage > 20.0
ORDER BY f.fiscal_year DESC;
```

---

## 7. Financial Statement Analysis & Visualization

In Python, create helper functions in `scripts/calculations_helper.py` to compute key corporate performance metrics:

1. **Gross Profit Margin**:
   $$\text{Gross Margin} = \frac{\text{Revenue} - \text{Cost of Sales}}{\text{Revenue}}$$
2. **Operating Profit Margin**:
   $$\text{Operating Margin} = \frac{\text{Operating Profit}}{\text{Revenue}}$$
3. **Current Ratio (Liquidity)**:
   $$\text{Current Ratio} = \frac{\text{Current Assets}}{\text{Current Liabilities}}$$
4. **Debt-to-Equity / Capital Strength**:
   $$\text{Debt-to-Equity} = \frac{\text{Total Liabilities}}{\text{Total Assets} - \text{Total Liabilities}}$$
5. **FX Sensitivity**:
   $$\text{FX Loss to Revenue Ratio} = \frac{\text{FX Translation Loss}}{\text{Revenue}}$$

### Visualizations to Plot in Matplotlib / Seaborn
Create high-impact, professional charts for your portfolio page:
* **Chart 1: NGN/USD Exchange Rate and Rolling SMAs (Dual Axis)**
  * Y1: Daily NGN/USD exchange rate.
  * Y2: Annualized 30-day rolling volatility.
  * *Purpose*: Visualize exactly when the currency devaluations occurred and highlight volatility spikes.
* **Chart 2: UK Multinational Profit Margins vs. Volatility**
  * Bar plot of PZ Cussons Operating Margin vs. line plot of Naira Volatility.
  * *Purpose*: Show how operating profit collapsed when volatility skyrocketed in 2024.
* **Chart 3: Current Ratio and FX Loss Impact**
  * Scatter plot showing PZ Cussons' Current Ratio and FX Translation Loss size.
  * *Purpose*: Show how currency volatility deteriorated liquidity of a UK corporate holding foreign operational subsidiaries.

---

## 8. Publishing on GitHub

To display this project on your CV/resume:
1. Initialize git in your project root: `git init`.
2. Commit your code, documentation, and notebook (ensure `config.env` is excluded in your `.gitignore`!).
3. Create a public repository on GitHub called `naira-usd-volatility-tracker`.
4. Push your local repository to GitHub.
5. Ensure your `README.md` is populated with the template provided in the next steps so recruiters can understand your project at a single glance.
