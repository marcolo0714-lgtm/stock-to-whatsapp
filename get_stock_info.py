import os
from dotenv import load_dotenv
from openai import api_key
import requests
import json
import yfinance as yf
import pandas as pd


"""
Retrieves the information of top stock markets from Twelve Data API based on the provided list of top stocks. 
It fetches global market states and metadata for stock exchanges, then processes each target exchange to extract and display relevant information.
Parameters:
    TOP_STOCKS (list): A list of dictionaries containing stock information, obtained from the get_top_markets function in choose_top_stock.py. 
    Each dictionary should represent a stock market and contain 4 keys: 'Rank', 'Exchange', 'Symbol', and 'Market_Cap'.
Returns:
    None
"""
def get_stock_info(TOP_STOCKS, use_sample_states=True):
    # =====================================================================
    # STEP 1: FETCH GLOBAL MARKET STATES AND EXCHANGE METADATA
    # =====================================================================
    load_dotenv()
    API_KEY = os.getenv("TWELVEDATA_API_KEY")

    print("Fetching global market states and metadata...")

    if use_sample_states:
        with open("global_states.json", "r") as f:
            global_states = json.load(f)
        with open("global_exchanges.json", "r") as f:
            global_exchanges = json.load(f)
    else:
        # Get states for ALL exchanges globally
        global_states_url = f"https://api.twelvedata.com/market_state?apikey={API_KEY}"
        global_states = requests.get(global_states_url).json()

        # Get metadata for ALL stock exchanges globally
        global_exchanges_url = f"https://api.twelvedata.com/exchanges?type=stock&apikey={API_KEY}"
        global_exchanges = requests.get(global_exchanges_url).json().get('data', [])

        with open("global_states.json", "w") as f:
            json.dump(global_states, f, indent=4)
        with open("global_exchanges.json", "w") as f:
            json.dump(global_exchanges, f, indent=4)

    # =====================================================================
    # STEP 2: OBTAIN STOCK EXCHANGE INFO FOR EACH TARGET EXCHANGE
    # =====================================================================

    for stock in TOP_STOCKS:
        exchange_code = stock.get('Symbol')[0]
        print(f"\n{'='*50}")
        print(f" 📊 PROCESSING: {stock['Symbol'][0]}")
        print(f"{'='*50}")

        # Find the specific exchange from our global list first
        state_info = []
        for item in global_states:
            if item.get('name').lower() == exchange_code.lower():
                state_info.append({
                    'country': item.get('country'),
                    'is_market_open': item.get('is_market_open'),
                    'time_to_open': item.get('time_to_open'),
                    'time_to_close': item.get('time_to_close')
                })
        
        if len(state_info) > 0:
            for market in state_info:
                print(f"Country: {market.get('country')}")
                print(f"Status: {'OPEN' if market.get('is_market_open') else 'CLOSED'}")
                print(f"Time to Open: {market.get('time_to_open')}")
                print(f"Time to Close: {market.get('time_to_close')}")
    
def get_stock_quote(TOP_STOCKS):
    tickers = list([stock['Symbol'][1] for stock in TOP_STOCKS])
    print("Fetching data from Yahoo Finance...\n")

    # Download the last 5 days of data
    # We download 5 days instead of 1 to guarantee we have at least two contiguous 
    # trading days to calculate the previous close, accounting for weekends and holidays.
    data = yf.download(tickers, period="3d", group_by='ticker', progress=False)

    print(f"{'Stock Exchange':<22} | {'Representative Ticker':<21} | {'Close Price':<12} | {'Daily Change'}")
    print("-" * 65)

    # 3. Process and calculate the percentage change for each exchange
    for stock in TOP_STOCKS:
        print()
        name = stock['Exchange']
        ticker = stock['Symbol'][1]
        try:
            # Extract the DataFrame for the specific ticker and drop empty rows (like market holidays)
            df = data[ticker].dropna()
            print(df)
            
            # Ensure we have at least 2 days of data to compare
            if len(df) >= 2:
                # Calculate daily percentage change for the 'Close' column
                daily_returns = df['Close'].pct_change() * 100
                
                # Extract the most recent closing price and percentage change
                latest_close = df['Close'].iloc[-1]
                latest_pct_change = daily_returns.iloc[-1]
                
                # Format the output neatly with aligned columns
                print(f"{name:<22} | {ticker:<10} | {latest_close:>10,.2f} | {latest_pct_change:>+8.2f}%")
            else:
                print(f"{name:<22} | {ticker:<10} | {'Not enough data':>25}")
                
        except Exception as e:
            print(f"{name:<22} | {ticker:<10} | Error processing data")



if __name__ == "__main__":
    from choose_top_stock import get_top_markets
    TOP_STOCKS, status = get_top_markets(20)  
    print(TOP_STOCKS)
    get_stock_info(TOP_STOCKS, use_sample_states=True)
    get_stock_quote(TOP_STOCKS)