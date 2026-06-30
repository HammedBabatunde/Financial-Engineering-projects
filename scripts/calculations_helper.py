"""
calculations_helper.py
Contains reusable functions for financial statement ratio analysis.
Loads data from PostgreSQL into a Pandas DataFrame and calculates metrics.
"""

import os
import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# Define helper functions for ratio calculations
def calculate_gross_margin(revenue, cost_of_sales):
    """
    Calculates Gross Profit Margin as a percentage.
    Formula: ((Revenue - Cost of Sales) / Revenue) * 100
    """
    if revenue is None or cost_of_sales is None or revenue == 0:
        return None
    return ((revenue - cost_of_sales) / revenue) * 100


def calculate_operating_margin(revenue, operating_profit):
    """
    Calculates Operating Profit Margin as a percentage.
    Formula: (Operating Profit / Revenue) * 100
    """
    if revenue is None or operating_profit is None or revenue == 0:
        return None
    return (operating_profit / revenue) * 100


def calculate_current_ratio(current_assets, current_liabilities):
    """
    Calculates the Current Ratio (Liquidity metric).
    Formula: Current Assets / Current Liabilities
    """
    if current_assets is None or current_liabilities is None or current_liabilities == 0:
        return None
    return current_assets / current_liabilities


def calculate_debt_to_equity(total_assets, total_liabilities):
    """
    Calculates the Debt-to-Equity ratio.
    Equity is computed using the accounting identity: Equity = Total Assets - Total Liabilities
    Formula: Total Liabilities / Equity
    """
    if total_assets is None or total_liabilities is None:
        return None
    equity = total_assets - total_liabilities
    if equity == 0:
        return None
    return total_liabilities / equity


def calculate_fx_sensitivity(fx_translation_loss, revenue):
    """
    Calculates FX Translation Loss Sensitivity as a percentage of Revenue.
    Formula: (FX Translation Loss / Revenue) * 100
    """
    if fx_translation_loss is None or revenue is None or revenue == 0:
        return None
    return (fx_translation_loss / revenue) * 100


# Main block to fetch from PostgreSQL and execute calculations in Pandas
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(script_dir, "..", "config.env"))

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME", "naira_volatility")

    conn_args = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "dbname": DB_NAME
    }
    if DB_PASSWORD and DB_PASSWORD.strip():
        conn_args["password"] = DB_PASSWORD

    print("Connecting to PostgreSQL to load metrics...")
    conn = psycopg2.connect(**conn_args)

    try:
        # Load the raw financial statement values
        query = """
        SELECT 
            ticker, fiscal_year, fiscal_period, revenue, cost_of_sales, 
            operating_profit, net_profit, total_assets, total_liabilities, 
            current_assets, current_liabilities, cash_and_equivalents, fx_translation_loss
        FROM financial_statements
        WHERE ticker = 'PZN'
        ORDER BY fiscal_year ASC;
        """
        df = pd.read_sql(query, conn)
        print("Data loaded successfully! Shape:", df.shape)

        # Replace database NULLs (which load as None/NaN) with None to safe-guard calculations
        df = df.replace({np.nan: None})

        # Apply calculations row-by-row using lambda functions
        print("Calculating financial ratios...")
        df['gross_margin_%'] = df.apply(
            lambda r: calculate_gross_margin(r['revenue'], r['cost_of_sales']), axis=1
        )
        df['operating_margin_%'] = df.apply(
            lambda r: calculate_operating_margin(r['revenue'], r['operating_profit']), axis=1
        )
        df['current_ratio'] = df.apply(
            lambda r: calculate_current_ratio(r['current_assets'], r['current_liabilities']), axis=1
        )
        df['debt_to_equity_ratio'] = df.apply(
            lambda r: calculate_debt_to_equity(r['total_assets'], r['total_liabilities']), axis=1
        )
        df['fx_sensitivity_%'] = df.apply(
            lambda r: calculate_fx_sensitivity(r['fx_translation_loss'], r['revenue']), axis=1
        )

        # Print the output DataFrame
        columns_to_show = [
            'fiscal_year', 'revenue', 'net_profit', 'gross_margin_%', 
            'operating_margin_%', 'current_ratio', 'debt_to_equity_ratio', 'fx_sensitivity_%'
        ]
        print("\n=== Computed Financial Metrics ===")
        print(df[columns_to_show].to_string(index=False))

        # Save to a new CSV file
        output_path = os.path.join(script_dir, "..", "data", "pz_cussons_ratios.csv")
        df.to_csv(output_path, index=False)
        print(f"\nRatios successfully exported to: {output_path}")

    finally:
        conn.close()
