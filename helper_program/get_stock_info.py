import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import json
import yfinance as yf
import pandas as pd

# Maps WFE's standard exchange naming conventions to representative Twelve Data's indices and yfinance tickers
# Ranking retrieved from the top 20 stocks of the (may, 2026) version of the webpage:
# https://focus.world-exchanges.org/issue/may-2026/market-statistics
EXCHANGE_TO_INDEX_MAP = {
    # Format: [Twelve Data Index name, yfinance Ticker]
    
    # 1-5
    "Nasdaq":                               ["NASDAQ", "^IXIC"],
    "New York Stock Exchange (NYSE)":       ["NYSE", "^GSPC"],
    "Shanghai Stock Exchange":              ["SSE", "000001.SS"],
    "Euronext":                             ["EURONEXT", "^N100"],
    "Japan Exchange Group":                 ["JPX", "^N225"],

    # 6-10
    "Shenzhen Stock Exchange":              ["SZSE", "399001.SZ"],
    "Hong Kong Exchanges and Clearing":     ["HKEX", "^HSI"],
    "TMX Group":                            ["TSX", "^GSPTSE"],
    "National Stock Exchange of India":     ["NSE", "^NSEI"],
    "BSE India Limited":                    ["BSE", "^BSESN"],

    # 11-15
    "Taiwan Stock Exchange":                ["TWSE", "^TWII"],
    "Korea Exchange":                       ["KOSDAQ", "^KS11"],
    "Deutsche Boerse AG":                   ["FSX", "^GDAXI"],
    "Saudi Exchange (Tadawul)":             ["TADAWUL", "^TASI.SR"],
    "SIX Swiss Exchange":                   ["SIX", "^SSMI"],

    # 16-20
    "ASX Australian Securities Exchange":   ["ASX", "^AXJO"],
    "Nasdaq Nordic and Baltics":            ["OMX", "^OMXN40"],
    "BME Spanish Exchanges":                ["BME", "^IBEX"],
    "Johannesburg Stock Exchange":          ["JSE", "^J203.JO"],
    "B3 - Brasil Bolsa Balcão":             ["Bovespa", "^BVSP"],

    # Other (in top 20 of previous years, but not in 2026/5's top 20)
    "LSE Group London Stock Exchange":      ["LSE", "^FTSE"],
    "Tehran Stock Exchange":                ["TSE", "^TEDPIX"],
}

"""
Retrieves the information of top stock markets, including their representative ticker symbols and indices.
Parameters:
    TOP_STOCKS (list): A list of dictionaries containing stock information, obtained from the get_top_markets function in choose_top_stock.py. 
    Each dictionary should represent a stock market and contain 3 keys: 'Rank', 'Exchange', and 'Market_Cap'.
Returns:
    A tuple containing:
        - A list of dictionaries with enriched information for each stock market, including 'Symbol' and 'Index' keys.
        - A status code (1 if data was retrieved successfully, 2 if use default data).
"""
def get_stock_info(TOP_STOCKS):
    for stock in TOP_STOCKS:
        exchange = stock.get('Exchange', '').strip()
        
        # Look up the symbol, default to "UNKNOWN" if not found
        symbol = EXCHANGE_TO_INDEX_MAP.get(exchange)[0] if EXCHANGE_TO_INDEX_MAP.get(exchange) else "UNKNOWN"
        index = EXCHANGE_TO_INDEX_MAP.get(exchange)[1] if EXCHANGE_TO_INDEX_MAP.get(exchange) else "UNKNOWN"

        # If we get "UNKNOWN", try to find a match by checking if the exchange name contains or is contained by any of the keys in our mapping
        if symbol == "UNKNOWN":
            contained_match = next((key for key in EXCHANGE_TO_INDEX_MAP.keys() if exchange in key), None)
            contained_by_match = next((key for key in EXCHANGE_TO_INDEX_MAP.keys() if key in exchange), None)
            if contained_match:
                symbol = EXCHANGE_TO_INDEX_MAP.get(contained_match, ["UNKNOWN"])[0]
                index = EXCHANGE_TO_INDEX_MAP.get(contained_match, ["UNKNOWN", "UNKNOWN"])[1]
                print(f"Matched unknown exchange '{exchange}' to containing key '{contained_match}'")
                stock['Exchange'] = contained_match  # Update the exchange name to the matched key for consistency
            elif contained_by_match:
                symbol = EXCHANGE_TO_INDEX_MAP.get(contained_by_match, ["UNKNOWN"])[0]
                index = EXCHANGE_TO_INDEX_MAP.get(contained_by_match, ["UNKNOWN", "UNKNOWN"])[1]
                print(f"Matched unknown exchange '{exchange}' to contained key '{contained_by_match}'")
                stock['Exchange'] = contained_by_match  # Update the exchange name to the matched key for consistency
            else:
                print(f"Could not find a mapping for exchange '{exchange}'. Defaulting to use default data.")
                from helper_program.DEFAULT_DATA.top_10_stock import TOP_TEN_STOCK
                TOP_STOCKS = TOP_TEN_STOCK
                return TOP_STOCKS, 2  # Return the default data and a status code indicating default data usage
            
        stock['Symbol'] = symbol
        stock['Index'] = index

    return TOP_STOCKS, 1  # Return the enriched TOP_STOCKS list along with a success status code (1)

"""
Retrieves the current market status (open/closed) and time to open/close for each of the top stock markets.
Parameters: 
    TOP_STOCKS (list): A list of dictionaries containing stock information.
    Each dictionary should represent a stock market and contain at least the keys 'Exchange' and 'Symbol'.
    use_sample_states (bool): Whether to use sample market states for testing purposes (to save API calls when testing).
Returns:
    A tuple containing:
        - The updated list of stock market information with added keys for 'country', 'is_market_open', 'time_to_open', and 'time_to_close' for each stock market.
        - A status code (1 if data was retrieved successfully, 0 if an error occurred).
"""
def get_stock_status(TOP_STOCKS, use_sample_states=True):
    # =====================================================================
    # STEP 1: LOAD API KEY FROM .env FILE
    # =====================================================================
    try:
        load_dotenv()
        API_KEY = os.getenv("TWELVEDATA_API_KEY")
    except Exception as e:
        print("Error loading API key from .env file. Please ensure you have a .env file with TWELVEDATA_API_KEY set.")
        print(f"Exception details: {e}")
        return TOP_STOCKS, 0  # Return the original TOP_STOCKS list along with an error status code (0)

    # =====================================================================
    # STEP 2: FETCH GLOBAL MARKET STATES AND EXCHANGE METADATA FROM TWELVE DATA API
    # =====================================================================
    print("Fetching global market states and metadata...")

    base_dir = Path(__file__).resolve().parent
    json_dir = base_dir / "json_data"

    try:
        if use_sample_states:
            with open(json_dir / "global_states.json", "r") as f:
                global_states = json.load(f)
        else:
            # Get states for ALL exchanges globally
            global_states_url = f"https://api.twelvedata.com/market_state?apikey={API_KEY}"
            global_states = requests.get(global_states_url).json()

            with open(json_dir / "global_states.json", "w") as f:
                json.dump(global_states, f, indent=4)

    except Exception as e:
        print("Error fetching data from Twelve Data API. Please check your API key and network connection.")
        print(f"Exception details: {e}")
        return TOP_STOCKS, 0  # Return the original TOP_STOCKS list along with an error status code (0)
    
    # =====================================================================
    # STEP 3: OBTAIN EXCHANGE INFO FOR EACH TARGET EXCHANGE
    # =====================================================================
    for stock in TOP_STOCKS:
        # Find the specific exchange from our global list first
        for item in global_states:
            if item.get('name').lower() == stock['Symbol'].lower():
                stock['country'] = item.get('country')
                stock['is_market_open'] = item.get('is_market_open')
                stock['time_to_open'] = item.get('time_to_open')
                stock['time_to_close'] = item.get('time_to_close')
                break  # Assuming we only want the first match for each exchange

    return TOP_STOCKS, 1  # Return the enriched TOP_STOCKS list along with a success status code (1)
    

"""
Retrieves the most recent market quotes (Open, High, Low, Close), percent change, and quote price for each of the top stock markets.
Parameters: 
    TOP_STOCKS (list): A list of dictionaries containing stock information.
    Each dictionary should represent a stock market and contain at least the keys 'Exchange' and 'Symbol'.
Returns:
    A tuple containing:
        - The updated list of stock market information with added keys for 'Open', 'High', 'Low', 'Close', 'Quote_Date', 'Daily_Change' for each stock market.
        - A status code (1 if data was retrieved successfully, 0 if an error occurred).
"""
def get_stock_quote(TOP_STOCKS):
    tickers = list([stock['Index'] for stock in TOP_STOCKS])
    print("Fetching data from Yahoo Finance...\n")

    # Download the last 5 days of data
    # We download 5 days instead of 1 to guarantee we have at least two contiguous 
    # trading days to calculate the previous close, accounting for weekends and holidays.
    try:
        data = yf.download(tickers, period="5d", group_by='ticker', progress=False)
    except Exception as e:
        print("Error fetching data from Yahoo Finance. Please check your network connection.")
        print(f"Exception details: {e}")
        return TOP_STOCKS, 0  # Return the original TOP_STOCKS list along with an error status code (0)

    # 3. Process and calculate the percentage change for each exchange
    for stock in TOP_STOCKS:
        name = stock['Exchange']
        ticker = stock['Index']

        # Extract the DataFrame for the specific ticker and drop empty rows (like market holidays)
        df = data[ticker].dropna()

        # print "Open", "High", "Low", "Close" values for each exchange
        # print(df)
        
        # Ensure we have at least 2 days of data to compare
        if len(df) >= 2:
            # Calculate daily percentage change for the 'Close' column
            daily_returns = df['Close'].pct_change() * 100
            latest_pct_change = str(daily_returns.iloc[-1])
        else:
            latest_pct_change = None
            
        # Extract the most recent closing price and percentage change
        try:
            open = df['Open'].iloc[-1]
            high = df['High'].iloc[-1]
            low = df['Low'].iloc[-1]
            close = df['Close'].iloc[-1]
            date = df.index[-1].strftime('%Y-%m-%d')

            stock['Daily_Change'] = latest_pct_change
            stock['Open'] = open
            stock['High'] = high
            stock['Low'] = low
            stock['Close'] = close
            stock['Quote_Date'] = str(date)
        except:
            pass

    return TOP_STOCKS, 1  # Return the enriched TOP_STOCKS list along with a success status code (1)


if __name__ == "__main__":
    from choose_top_stock import get_top_markets

    TOP_STOCKS, status = get_top_markets(num_stocks=20, use_current_month=False, month="june", year=2026)
    TOP_STOCKS, status = get_stock_info(TOP_STOCKS)
    TOP_STOCKS, status1 = get_stock_status(TOP_STOCKS, use_sample_states=False)
    TOP_STOCKS, status2 = get_stock_quote(TOP_STOCKS)

    path = "helper_program/json_data/top_stock_info.json"
    try:
        f = open(path)
        f.close()
        # If the path exists, write the json only when latest info is obtained
        if status1 and status2:
            with open(path, "w") as f:
                json.dump(TOP_STOCKS, f, indent=4)
                print("Information obtained and updated at:", path)
    except:
        # If the path does not exist, always write the json
        with open(path, "w") as f:
            json.dump(TOP_STOCKS, f, indent=4)
            print("Information obtained and updated at:", path)
