# The Naira/USD Volatility Tracker & Corporate Impact Study (PZ Cussons Nigeria Plc)

A comprehensive portfolio project integrating Time Series Data Manipulation, Relational Database Ingestion (PostgreSQL), and Corporate Financial Statement Analysis. This study tracks the historical exchange rate of the Nigerian Naira (NGN) against the US Dollar (USD), calculates statistical volatility trends, and analyzes their real-world impact on NGX-listed consumer goods manufacturer **PZ Cussons Nigeria Plc** (NGX: PZ), which serves as a prime case study of transaction and translation exposure under currency regime shifts.

---

## 🌟 Key Features
- **Time Series Engine**: Fetches daily currency exchange rates via AlphaVantage API, handles calendar day index alignment (`.asfreq('D')`), forward fills weekend trading gaps (`.ffill()`), and computes 30-day and 90-day moving averages alongside annualized rolling volatility.
- **Relational Storage**: Integrates a PostgreSQL database model storing currency history and corporate financials with structural integrity constraints (foreign keys, unique index bounds) and optimized batch inserts (`execute_values`).
- **Financial Sensitivity Model**: Computes Gross Profit Margin, Operating Margin, Current Ratio (Liquidity), Debt-to-Equity (Solvency), and FX Sensitivity metrics to map the microeconomic shock of the Naira floatation.
- **Visual Showcase**: Features custom-styled visualizations including moving average overlays, a dual-axis spot rate vs. rolling volatility chart, and a multi-plot corporate performance panel.

---

## 🛠️ Tech Stack & Concepts
- **Language**: Python 3.x
- **Database**: PostgreSQL
- **Key Python Libraries**: Pandas, NumPy, Matplotlib, Seaborn, psycopg2, python-dotenv, Requests
- **DataCamp Course Integrations**:
  1. *Manipulating Time Series Data*: `.asfreq()`, `.ffill()`, `.pct_change()`, `.rolling().mean()`, `.rolling().std()`, `.resample('QE')`.
  2. *Intermediate SQL*: `CREATE TABLE`, `FOREIGN KEY`, `INNER JOIN`, `GROUP BY`, `HAVING`, `COALESCE()`, `ON CONFLICT DO NOTHING`.
  3. *Analyzing Financial Statements*: Gross Margin, Operating Margin, Current Ratio, Debt-to-Equity, translation loss ratios.

---

## 📁 Repository Directory Structure

```text
├── README.md                      # This file
├── project_todo.md                 # Step-by-step progress checklist
├── portfolio_roadmap.md           # Technical blueprint and guides
├── database/
│   ├── schema.sql                 # PostgreSQL table schemas
│   └── queries.sql                # SQL queries executing aggregates, joins, and filters
├── data/
│   ├── raw_exchange_rates.csv     # Cleaned daily currency rates output
│   ├── pz_cussons_financials.csv  # Extracted corporate financials (in base Naira)
│   └── pz_cussons_ratios.csv      # Computed financial ratios output
├── scripts/
│   ├── data_ingestion.py          # Script for currency API fetching
│   ├── db_manager.py              # Script to initialize tables and ingest data to Postgres
│   └── calculations_helper.py     # Python functions computing financial ratios
└── analysis_showcase.ipynb        # Master showcase Jupyter Notebook
```

---

## 🚀 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/naira-usd-volatility-tracker.git
   cd naira-usd-volatility-tracker
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install pandas numpy matplotlib seaborn python-dotenv requests psycopg2-binary jupyter
   ```

4. **Configure Database & API Credentials**:
   - Create a file named `config.env` in the root folder.
   - Insert your AlphaVantage API key and PostgreSQL credentials:
     ```env
     ALPHAVANTAGE_API_KEY=your_key_here
     DB_HOST=localhost
     DB_PORT=5432
     DB_USER=postgres
     DB_PASSWORD=your_postgres_password
     DB_NAME=naira_volatility
     ```

5. **Run the Data Pipeline**:
   - Run the API ingestion script to fetch historical rates:
     ```bash
     python scripts/data_ingestion.py
     ```
   - Run the database manager to run the DDL schema script and ingest data:
     ```bash
     python scripts/db_manager.py
     ```
   - Run the ratio calculations helper to process margins and balance sheet metrics:
     ```bash
     python scripts/calculations_helper.py
     ```

6. **Explore the Notebook**:
   ```bash
   jupyter notebook analysis_showcase.ipynb
   ```

---

## 📊 Results & Key Insights

### 1. Computed Financial Metrics (PZ Cussons Nigeria Plc)

The corporate financial data was extracted from the [2025 Annual Report](ng-pz-2025-ar-00.pdf) (in NGN, base values):


| Fiscal Year | Revenue (Naira) | Net Profit (Naira) | Gross Margin (%) | Operating Margin (%) | Current Ratio (x) | Debt-to-Equity (x) | FX Sensitivity (%) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **2021** | 82,577,540,000 | 1,559,857,000 | *N/A* | *N/A* | 1.23x | 1.75x | *N/A* |
| **2022** | 99,503,320,000 | 6,699,325,000 | *N/A* | *N/A* | 1.36x | 1.90x | *N/A* |
| **2023** | 113,964,309,000 | 14,348,345,000 | *N/A* | *N/A* | 1.56x | 2.44x | *N/A* |
| **2024** | 152,249,309,000 | -90,317,282,000 | 35.55% | -81.77% | 0.59x | -6.71x | 103.72% |
| **2025** | 212,634,336,000 | 10,066,719,000 | 27.14% | 8.90% | 0.64x | -10.74x | 3.66% |

*Note: Missing items (N/A) represent lines not broke down in the high-level 5-year summary for earlier periods.*

### 2. Historical Macroeconomic Findings

* **The Volatility Shock (FY24)**: When the Central Bank of Nigeria floated the Naira on **June 14, 2023**, unified rate windows triggered an immediate devaluation shock. The average exchange rate rose from 635 to 1,476 NGN/USD, pushing 30-day annualized rolling volatility to a peak of **121.49%**.
* **Operational Margin Collapse**: During the FY24 float, PZ Cussons maintained a healthy **35.55% Gross Margin**, indicating intact pricing power. However, their **Operating Margin collapsed to -81.77%** due to a massive **N157.92 Billion write-down** on USD-denominated import obligations. This single foreign exchange loss consumed **103.72%** of the company's total annual sales revenue, driving a **N90.32 Billion bottom-line net loss**.
* **Liquidity and Solvency Trap**: The currency mismatch (debts in USD, cash and sales in local Naira) caused Current Liabilities to double, causing the Current Ratio to crash from **1.56x to a dangerous 0.59x**. The massive net loss completely wiped out capital reserves, driving Total Equity into negative territory (**-N17.34 Billion**) and forcing the Debt-to-Equity ratio negative (**-6.71x** in 2024 and **-10.74x** in 2025), indicating technical insolvency.
* **The Power of Stabilization (FY25)**: In 2025, although the exchange rate remained historically weak (averaging 1,517 NGN/USD), rolling volatility collapsed from 121.49% to just **13.44%**. Because the rate stabilized, foreign exchange write-downs dropped to just N7.78 Billion (3.66% of sales), allowing operating profits to recover to **N18.92 Billion (an 8.90% margin)** and returning the subsidiary to profitability.

---

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.
