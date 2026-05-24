import os
from dotenv import load_dotenv
from openai import api_key
import requests
import json

# Index Ticker to Exchange Name mapping for the top 20 global stock markets (as of May 2026)
INDEX_TO_EXCHANGE_MAP = {
    # 1-5 
    "IXIC": "NASDAQ",     # Nasdaq
    "GSPC": "NYSE",       # New York Stock Exchange
    "000001": "SSE",      # Shanghai Stock Exchange
    "N100": "EURONEXT",   # Euronext (Pan-European)
    "N225": "JPX",        # Japan Exchange Group (Tokyo)

    # 6-10 
    "399001": "SZSE",     # Shenzhen Stock Exchange
    "HSI": "HKEX",        # Hong Kong Exchanges and Clearing
    "GSPTSE": "TSX",      # Toronto Stock Exchange (TMX Group)
    "NSEI": "NSE",        # National Stock Exchange of India
    "BSESN": "BSE",       # BSE India Limited (Bombay)

    # 11-15 
    "TWII": "TWSE",       # Taiwan Stock Exchange
    "KS11": "KOSPI",      # Korea Exchange
    "GDAXI": "FSX",       # Frankfurt Stock Exchange (Deutsche Boerse)
    "TASI": "TADAWUL",    # Saudi Exchange
    "SSMI": "SIX",        # SIX Swiss Exchange

    # 16-20 
    "AXJO": "ASX",        # Australian Securities Exchange
    "OMXN40": "OMX",      # Nasdaq Nordic and Baltics
    "IBEX": "BME",        # BME Spanish Exchanges (Bolsa de Madrid)
    "J203": "JSE",        # Johannesburg Stock Exchange
    "BVSP": "B3",         # B3 - Brasil Bolsa Balcão

    # Other 
    "FTSE": "LSE",        # London Stock Exchange
    "TEDPIX": "TSE"       # Tehran Stock Exchange
}

def get_stock_info(TOP_STOCKS):
    load_dotenv()
    API_KEY = os.getenv("TWELVEDATA_API_KEY")

    symbols = ""
    symbols_exchange = ""
    for stock in TOP_STOCKS:
        if stock["Symbol"].count('.') >= 1:  # Check if the symbol contains a dot, indicating it's likely in the format "SYMBOL.EXCHANGE"
            symbols_exchange += stock["Symbol"] + ","
        else:
            symbols += stock["Symbol"] + ","

    # Remove the trailing comma
    if symbols.endswith(","):
        symbols = symbols[:-1]  
    if symbols_exchange.endswith(","):
        symbols_exchange = symbols_exchange[:-1]
    print(symbols)
    print(symbols_exchange)

    print("Fetching global market states and metadata...")

    # # Get states for ALL exchanges globally
    # global_states_url = f"https://api.twelvedata.com/market_state?apikey={API_KEY}"
    # global_states = requests.get(global_states_url).json()

    # # Get metadata for ALL stock exchanges globally
    # global_exchanges_url = f"https://api.twelvedata.com/exchanges?type=stock&apikey={API_KEY}"
    # global_exchanges = requests.get(global_exchanges_url).json().get('data', [])

    # with open("global_states.json", "w") as f:
    #     json.dump(global_states, f, indent=4)
    # with open("global_exchanges.json", "w") as f:
    #     json.dump(global_exchanges, f, indent=4)

    with open("global_states.json", "r") as f:
        global_states = json.load(f)
    with open("global_exchanges.json", "r") as f:
        global_exchanges = json.load(f)

    # =====================================================================
    # STEP 2: PROCESS EACH TARGET EXCHANGE
    # =====================================================================

    symbols = symbols + "," + symbols_exchange

    for symbol in symbols.split(","):
        if symbol.count('.') >= 1:
            exchange_code = INDEX_TO_EXCHANGE_MAP.get(symbol.split(".")[0])
        else:
            exchange_code = INDEX_TO_EXCHANGE_MAP.get(symbol)

        print(f"\n{'='*50}")
        print(f" 📊 PROCESSING: {symbol} (Exchange Code: {exchange_code})")
        print(f"{'='*50}")

        # --- A. Extract Data from Global Market State ---
        # Find the specific exchange from our global list

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
            print("[Market State]")
            print(f"Country: {state_info[0].get('country')}")
            print(f"Status: {'OPEN' if state_info[0].get('is_market_open') else 'CLOSED'}")
            print(f"Time to Open: {state_info[0].get('time_to_open')}")
            print(f"Time to Close: {state_info[0].get('time_to_close')}")

if __name__ == "__main__":
    from choose_top_stock import get_top_markets
    TOP_STOCKS, status = get_top_markets(20)  
    print(TOP_STOCKS)
    get_stock_info(TOP_STOCKS)