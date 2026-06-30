import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Get the script's directory, go up one level, and locate config.env
script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, "..", "config.env")
load_dotenv(config_path)

# Retrieve the API key
API_KEY = os.getenv('ALPHAVANTAGE_API_KEY')

# 3. Safeguard: Check that the API key was successfully loaded
if not API_KEY:
    raise ValueError(
        "API Key not found! Please check that: \n"
        "1. A file named 'config.env' exists in the project root.\n"
        "2. It contains the line: ALPHAVANTAGE_API_KEY=your_key_here"
    )

def fetch_historical_rates(from_currency="USD", to_currency="NGN"):
    """
    Fetches raw daily historical exchange rates from AlphaVantage API.

    Args:
        from_currency (str): The base currency symbol (default "USD").
        to_currency (str): The target currency symbol (default "NGN").

    Returns:
        dict: Raw JSON response containing the daily exchange rates time series.
    """
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "FX_DAILY",
        "from_symbol": from_currency,
        "to_symbol": to_currency,
        "outputsize": "full",
        "apikey": API_KEY
    }

    
    try:
        print(f"Fetching historical rates for {from_currency}/{to_currency}...")
        # Added timeout=10 to prevent hanging indefinitely on a bad connection
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
    except requests.exceptions.Timeout:
        raise Exception("The request timed out. Please check your internet speed and try again.")
    except requests.exceptions.ConnectionError:
        raise Exception("Connection error. Could not connect to AlphaVantage servers. Are you offline?")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error occurred: {e}")
        
    data = response.json()
    
    # AlphaVantage API standard error/limit checking
    if "Error Message" in data:
        raise Exception(f"API Error: {data['Error Message']}")
    if "Note" in data:
        print(f"API Warning (e.g. rate limit): {data['Note']}")
        
    return data


def process_rates_to_dataframe(raw_data):
    """
    Parses the raw AlphaVantage JSON response into a clean, sorted Pandas DataFrame.
    """
    # 1. Retrieve the time series data dictionary
    time_series_key = "Time Series FX (Daily)"
    if time_series_key not in raw_data:
        raise KeyError(f"Expected time series key '{time_series_key}' not found in API response.")
    
    raw_series = raw_data[time_series_key]
    
    # 2. Extract dates and close rates (close rate is typically '4. close')
    records = []
    for date_str, daily_info in raw_series.items():
        records.append({
            "date": date_str,
            "usd_to_ngn_rate": float(daily_info["4. close"])
        })
    
    # 3. Create DataFrame
    df = pd.DataFrame(records)
    
    # 4. Calculate the reciprocal rate (NGN to USD)
    df["ngn_to_usd_rate"] = 1.0 / df["usd_to_ngn_rate"]

    
    # 5. Format dates to standard ISO strings and sort chronologically
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    
    return df

if __name__ == "__main__":
    try:
        # 1. Fetch raw data
        raw_data = fetch_historical_rates()
        
        # 2. Process into a clean DataFrame
        df_rates = process_rates_to_dataframe(raw_data)
        
        # 3. Preview output
        print("\nSuccessfully parsed exchange rates!")
        print(df_rates.head())
        print(f"Total records retrieved: {len(df_rates)}")

        # 4. Export to CSV (New Logic)
        output_dir = os.path.join(script_dir, "..", "data")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "raw_exchange_rates.csv")
        df_rates.to_csv(output_path, index=False)
        print(f"Rates successfully exported to: {output_path}")
        
    except Exception as e:
        print("Error during ingestion test:", e)
