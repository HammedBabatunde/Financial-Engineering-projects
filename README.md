# Savings Engine 💰

A Python-based financial engineering tool that imports historical bank statements, processes vectorized data using pandas, and calculates core financial metrics like Runway and Projected Time-to-Goal.

## Features
- **Data Ingestion & Cleaning:** Imports raw bank CSV data, cleans currency formatting, and handles missing values.
- **Vectorized Time-Series Analysis:** Uses a pandas `DatetimeIndex` to group transactions by month, converting raw ledger entries into actionable monthly cash flows.
- **Financial Metrics Engine:** 
  - Calculates **Standard Runway** (How long current savings will last based on average monthly expenses).
  - Calculates **Projected Time-to-Goal** (How long it will take to hit a specific savings target, e.g., $30,000, based on current net savings).
- **Data Visualization:** Generates professional financial reports using `matplotlib` and `seaborn` to visualize wealth snapshots over time and monthly cash flow (Income vs. Expenses).

## Tech Stack
- Python 3
- Pandas (Data manipulation)
- Matplotlib & Seaborn (Data visualization)
- Jupyter Notebook (Interactive analysis)

## Setup & Usage
1. Clone the repository.
2. Create a virtual environment and install the required libraries:
   ```bash
   pip install pandas matplotlib seaborn jupyter
   ```
3. Place your bank statement CSV file in the root directory (e.g., `statement.csv`).
4. Open the `savings_engines.ipynb` notebook and run the cells to generate your personalized financial report!
