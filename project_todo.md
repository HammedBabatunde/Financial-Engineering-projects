# Naira/USD Volatility Tracker - Project To-Do List

Use this interactive checklist to guide your implementation. You can mark items as completed by changing `[ ]` to `[x]` as you progress through the development steps.

---

## Phase 1: Environment & API Setup (Time Series Course)
- [x] Create your project directory structure as specified in [portfolio_roadmap.md](file:///Users/user/Desktop/Python-for-Financial-Engineering/Volatility%20tracker project/portfolio_roadmap.md).
- [x] Initialize git repository: `git init`.
- [x] Create and activate a Python virtual environment (`venv`):
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- [x] Create a `.gitignore` file to ignore `.env`, `*.db`, venv, and cache directories:
  ```text
  config.env
  *.db
  venv/
  __pycache__/
  .ipynb_checkpoints/
  .DS_Store
  ```
- [x] Install required dependencies in your active virtual environment:
  ```bash
  pip install pandas numpy matplotlib seaborn python-dotenv requests jupyter
  ```
- [x] Create `config.env` and request your free API key from AlphaVantage or ExchangeRate-API.
- [x] Write `scripts/data_ingestion.py`:
  - [x] Implement secure API key retrieval using `dotenv`.
  - [x] Write a function to query daily NGN/USD rates.
  - [x] Handle potential connection issues or empty responses.
  - [x] Write clean date formatting logic to ensure standard ISO formatting (`YYYY-MM-DD`).
  - [x] Export the raw daily rates as `data/raw_exchange_rates.csv`.



---

## Phase 2: Time Series Manipulation (Time Series Course)
- [x] Import daily exchange rate data into Pandas.
- [x] Convert the date column to `DatetimeIndex`.
- [x] Verify if there are missing dates (e.g. weekends) using `.asfreq('D')`.
- [x] Implement forward-fill (`.ffill()`) to handle weekend gap filling.
- [x] Calculate **daily percentage returns** using `.pct_change()`.
- [x] Compute the **30-day Simple Moving Average (SMA)** of the rate.
- [x] Compute the **90-day Simple Moving Average (SMA)** of the rate.
- [x] Compute **30-day rolling standard deviation** of daily returns.
- [x] **Annualize** the 30-day rolling standard deviation by multiplying by `np.sqrt(252)`.
- [x] Handle the missing `NaN` values created by the rolling windows using `.fillna()` or `.dropna()`.
- [x] Downsample (resample) daily data to **quarterly averages** using `.resample('QE').mean()` to align with corporate reporting dates.


---

## Phase 3: SQL Relational Storage (Intermediate SQL Course)
- [x] Create the PostgreSQL database: `naira_volatility` on your local server.
- [x] Write `database/schema.sql`:

  - [x] Create `exchange_rates` table.
  - [x] Create `companies` table.
  - [x] Create `financial_statements` table (with Foreign Key linking to `companies`).
- [x] Write `scripts/db_manager.py`:
  - [x] Connect to PostgreSQL and execute schema.sql to initialize tables.
  - [x] Ingest data/raw_exchange_rates.csv (with computed returns/volatility) using batch insert.
  - [x] Create `data/pz_cussons_financials.csv` containing the LSE-listed PZ Cussons financial statements.
  - [x] Populate the `companies` table with the metadata for PZ Cussons.
  - [x] Ingest `data/pz_cussons_financials.csv` into the `financial_statements` table in the database.


---

## Phase 4: Intermediate SQL Querying (Intermediate SQL Course)
- [x] Open `database/queries.sql` and write SQL commands to query your PostgreSQL database:
  - [x] Write an aggregation query (`GROUP BY`) to find the average exchange rate and peak volatility for each calendar year.
  - [x] Write an `INNER JOIN` query connecting PZ Cussons annual results to the average exchange rates of the corresponding years.
  - [x] Write a filtered query using `HAVING` that extracts only the years where the exchange rate devalued by more than 20% and outputs the corporate FX losses for those years.
- [x] Integrate these queries into Python using `psycopg2.connect()` and `pd.read_sql()` inside your Jupyter Notebook.


---

## Phase 5: Financial Statement Ratio Analysis (Financial Statements Course)
- [x] Write `scripts/calculations_helper.py` to contain reusable financial analysis functions:
  - [x] Define `calculate_gross_margin(revenue, cost_of_sales)`.
  - [x] Define `calculate_operating_margin(revenue, operating_profit)`.
  - [x] Define `calculate_current_ratio(current_assets, current_liabilities)`.
  - [x] Define `calculate_debt_to_equity(total_assets, total_liabilities)`.
  - [x] Define `calculate_fx_sensitivity(fx_translation_loss, revenue)`.

- [x] Load the SQL query outputs into Pandas and compute these ratios for PZ Cussons plc for all reported years (2021-2024).
- [x] Analyze trends:
  - [x] Observe how Gross and Operating Margin changed as the Naira devalued.
  - [x] Observe how current liquidity (Current Ratio) behaved during the FY24 currency flotation.

---

## Phase 6: Exploratory Data Analysis & Visualization
- [x] Set up your showcase Jupyter Notebook `analysis_showcase.ipynb`.
- [x] Plot the daily Naira/USD rate with 30-day and 90-day SMAs overlaid.
- [x] Create a dual-axis chart:
  - [x] Left Y-axis: Daily exchange rate.
  - [x] Right Y-axis: Annualized rolling volatility.
  - [x] Annotate key macroeconomic events (e.g., Central Bank flotation in mid-2023).
- [x] Create a multi-plot visualization panel:
  - [x] Subplot 1: PZ Cussons Operating Profit Margin vs. Time.
  - [x] Subplot 2: PZ Cussons foreign exchange losses vs. average annual USD/NGN rates.
  - [x] Subplot 3: Debt-to-Equity ratio trend.
- [x] Write detailed summaries and explanations in the notebook's markdown cells explaining the economic narratives.


---

## Phase 7: GitHub Publishing
- [x] Format your code PEP8 style and document all custom functions.

- [x] Update the repository [README.md](file:///Users/user/Desktop/Python-for-Financial-Engineering/Volatility%20tracker%20project/README.md) with your findings, charts, and configuration instructions.

- [ ] Initialize git repository: `git init`.
- [ ] Execute `git add .` (Verify that `config.env` is ignored!).
- [ ] Commit your files: `git commit -m "Initial commit: Naira/USD volatility tracker"`.
- [ ] Create a public repository on GitHub and link it as remote origin.
- [ ] Push to GitHub: `git push -u origin main`.
- [ ] Share your project on LinkedIn or add it to your resume portfolio!

