import os
import sqlite3 # Kept if needed, but not used here
import psycopg2
from psycopg2.extras import execute_values
import pandas as pd
import numpy as np
from dotenv import load_dotenv

# Load env variables from root config.env
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "..", "config.env")
load_dotenv(config_path)

# Database Credentials
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "naira_volatility")

def get_db_connection():
    """
    Helper function to establish connection to the target database.
    """
    conn_args = {
        "host": DB_HOST,
        "port": DB_PORT,
        "user": DB_USER,
        "dbname": DB_NAME
    }
    if DB_PASSWORD and DB_PASSWORD.strip():
        conn_args["password"] = DB_PASSWORD
    return psycopg2.connect(**conn_args)

def run_schema_sql():
    """
    Reads database/schema.sql and executes the DDL commands to setup tables.
    """
    schema_path = os.path.join(script_dir, "..", "database", "schema.sql")
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")
        
    print(f"Reading schema file: {schema_path}...")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
        
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        print("Executing schema DDL scripts...")
        cursor.execute(schema_sql)
        conn.commit()
        print("Database tables initialized successfully!")
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"Error executing schema: {e}")
        raise e
    finally:
        conn.close()

def ingest_exchange_rates():
    """
    Loads raw exchange rates, runs the calculations (Phase 2), and batch-saves to Postgres.
    """
    csv_path = os.path.join(script_dir, "..", "data", "raw_exchange_rates.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Exchange rates file not found. Run data_ingestion.py first.")
        
    print(f"Loading raw exchange rates from: {csv_path}...")
    df = pd.read_csv(csv_path)
    
    # 1. Run Time Series Calculations (Phase 2)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    
    # Reindex & Forward Fill gaps
    df = df.asfreq("D").ffill()
    
    # Compute Metrics
    df["daily_return"] = df["usd_to_ngn_rate"].pct_change()
    df["sma_30"] = df["usd_to_ngn_rate"].rolling(window=30).mean()
    df["sma_90"] = df["usd_to_ngn_rate"].rolling(window=90).mean()
    df["rolling_vol_30d"] = df["daily_return"].rolling(window=30).std()
    df["annualized_vol_30d"] = df["rolling_vol_30d"] * np.sqrt(252)
    
    # Drop NaNs to keep DB clean
    df = df.dropna()
    df = df.reset_index()
    
    # Convert Datetime objects back to standard ISO strings for Postgres
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    
    # 2. Ingest to Postgres
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Prepare insertion query
        insert_query = """
        INSERT INTO exchange_rates (
            rate_date, usd_to_ngn_rate, ngn_to_usd_rate, daily_return, 
            sma_30, sma_90, rolling_vol_30d, annualized_vol_30d
        ) VALUES %s;
        """
        
        # Format rows as tuples
        # Columns in order: date, usd_to_ngn_rate, ngn_to_usd_rate, daily_return, sma_30, sma_90, rolling_vol_30d, annualized_vol_30d
        records = list(
            df[[
                "date", "usd_to_ngn_rate", "ngn_to_usd_rate", "daily_return",
                "sma_30", "sma_90", "rolling_vol_30d", "annualized_vol_30d"
            ]].itertuples(index=False, name=None)
        )
        
        print(f"Ingesting {len(records)} daily records into the database...")
        execute_values(cursor, insert_query, records)
        conn.commit()
        print("Data ingestion completed successfully!")
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"Error ingesting exchange rates: {e}")
        raise e
    finally:
        conn.close()

def ingest_company_and_financials():
    """
    Inserts PZ Cussons company metadata and loads the 5-year financials CSV into Postgres.
    """
    csv_path = os.path.join(script_dir, "..", "data", "pz_cussons_financials.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Financials CSV not found at: {csv_path}")

    # Load corporate financials DataFrame
    df = pd.read_csv(csv_path)
    
    # Replace Pandas NaN with Python None (which translates to SQL NULL)
    df = df.replace({np.nan: None})

    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Insert Company Metadata into the 'companies' table
        company_query = """
        INSERT INTO companies (ticker, name, country, reporting_currency)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ticker) DO NOTHING;
        """
        company_data = ("PZN", "PZ Cussons Nigeria Plc", "Nigeria", "NGN")
        
        print("Inserting company metadata into 'companies' table...")
        cursor.execute(company_query, company_data)
        
        # 2. Insert Financial Statement Rows into 'financial_statements'
        financials_query = """
        INSERT INTO financial_statements (
            ticker, fiscal_year, fiscal_period, revenue, cost_of_sales, 
            operating_profit, net_profit, total_assets, total_liabilities, 
            current_assets, current_liabilities, cash_and_equivalents, fx_translation_loss
        ) VALUES %s
        ON CONFLICT (ticker, fiscal_year, fiscal_period) DO NOTHING;
        """
        
        # Select columns in exact order of insert query
        columns = [
            "ticker", "fiscal_year", "fiscal_period", "revenue", "cost_of_sales",
            "operating_profit", "net_profit", "total_assets", "total_liabilities",
            "current_assets", "current_liabilities", "cash_and_equivalents", "fx_translation_loss"
        ]
        records = list(df[columns].itertuples(index=False, name=None))
        
        print(f"Ingesting {len(records)} financial statement records into the database...")
        execute_values(cursor, financials_query, records)
        
        conn.commit()
        print("Company and financial statements ingestion completed successfully!")
        cursor.close()
    except Exception as e:
        conn.rollback()
        print(f"Error ingesting corporate data: {e}")
        raise e
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        run_schema_sql()
        ingest_exchange_rates()
        ingest_company_and_financials()  
    except Exception as e:
        print(f"\nExecution failed: {e}")
