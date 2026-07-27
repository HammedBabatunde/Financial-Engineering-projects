# 📈 Quantitative Portfolio Analysis & Optimization on the NGX

A comprehensive quantitative portfolio management and optimization project for equities listed on the **Nigerian Stock Exchange (NGX)** using historical market data fetched live via the [`afrimarket`](https://github.com/ambroseikpele/afrimarket) Python library.

This project implements an end-to-end quantitative finance and Modern Portfolio Theory (MPT) framework adapted specifically for African frontier equity markets.

---

## 🌟 Key Features

* **Data Extraction & Preprocessing**: Automated ingestion of NGX stock prices and the NGX All-Share Index (`ASI`) via `afrimarket`, with forward-filling (`.ffill()`) time-series alignment.
* **Risk & Performance Analytics**:
  * Annualized Return & Annualized Volatility ($T = 252$).
  * Risk-adjusted ratios: **Sharpe Ratio** & **Sortino Ratio** (downside volatility).
  * Higher-moment shape evaluation: **Skewness** & **Kurtosis** (fat-tail distribution analysis).
  * Rolling Peak-to-Trough **Maximum Drawdown** tracking.
* **CAPM & Benchmark Attribution**:
  * OLS regression of portfolio excess returns against the NGX All-Share Index.
  * Calculation of **Market Beta ($\beta$)**, **Annualized Alpha ($\alpha$)**, and **$R^2$**.
  * Active Return and Active Sector Weighting relative to market benchmarks.
* **Modern Portfolio Theory (MPT) Optimization**:
  * Markowitz Efficient Frontier optimization using `PyPortfolioOpt`.
  * **Max Sharpe Portfolio** (growth-efficiency allocation).
  * **Minimum Volatility Portfolio** (capital preservation allocation).
  * Advanced risk models: **Exponentially Weighted Moving Average (EWMA)** and **Downside Semicovariance**.
* **₦1,000,000 Historical Backtesting**: Visual backtest comparing cumulative growth of ₦1,000,000 starting capital across all strategies over a 10-year timeline (2016–2026).

---

## 📊 Summary Results Table

| Strategy | Annual Return | Annual Volatility | Sharpe Ratio | Sortino Ratio | Max Drawdown | Beta ($\beta$) | Alpha ($\alpha$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Equal Weighted Baseline** | 26.70% | 24.54% | 0.68 | 0.96 | -64.54% | 0.86 | 5.33% |
| **Max Sharpe Portfolio** | **28.87%** | 27.83% | **0.68** | 0.94 | -65.28% | 0.96 | **+6.12%** |
| **Min Volatility Portfolio** | 25.64% | **23.77%** | 0.66 | 0.92 | -66.62% | **0.78** | 5.32% |
| **NGX All-Share Index** | 23.22% | 13.92% | 0.95 | 1.40 | -54.16% | 1.00 | 0.00% |

---

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/afrimarket-portfolio-optimization.git
cd afrimarket-portfolio-optimization
```

### 3. Create & Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate   # On MacOS/Linux
# .venv\Scripts\activate    # On Windows
```

### 4. Install Dependencies
```bash
pip install pandas numpy scipy statsmodels matplotlib seaborn PyPortfolioOpt afrimarket
```

---

## 📁 Repository Structure

```
├── project.ipynb             # Main Interactive Jupyter Notebook
└── README.md                 # Project Documentation
```

---

## 💡 Key Strategic Takeaways

1. **Active Alpha Outperformance**: The **Max Sharpe Portfolio** achieved the highest annual return (**28.87%**) and stock selection Alpha (**+6.12% per year**), compounding an initial ₦1,000,000 investment to over **₦11.5 Million** over 10 years.
2. **Defensive Hedging**: The **Minimum Volatility Portfolio** achieved the lowest market Beta ($\beta = 0.78$) and lowest annual volatility ($23.77\%$), utilizing `GUINNESS (28.5%)` and `ACCESSCORP (14.8%)` as cross-sector stability anchors.
3. **Market Outperformance**: All custom portfolio strategies successfully outperformed the passive NGX All-Share Index over the historical backtest period.

---

## 🙏 Acknowledgments

* **[afrimarket](https://github.com/ambroseikpele/afrimarket)** by Ambrose Ikpele for providing the Python market data interface to the Nigerian Stock Exchange.
