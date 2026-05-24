import pandas as pd
import requests
from io import StringIO

# Default number of top stocks to retrieve
stock_num = 10

# Maps WFE's standard exchange naming conventions to Twelve Data Index Tickers
# Ranking retrieved from the top 20 stocks of the (may, 2026) version of the webpage:
# https://focus.world-exchanges.org/issue/may-2026/market-statistics
EXCHANGE_TO_INDEX_MAP = {
    # 1-5
    "Nasdaq":                            "IXIC",        # NASDAQ Composite
    "New York Stock Exchange (NYSE)":    "GSPC",        # S&P 500 (Alternative: NYA for NYSE Composite)
    "Shanghai Stock Exchange":           "000001.SHG",  # SSE Composite
    "Euronext":                          "N100",        # Euronext 100
    "Japan Exchange Group":              "N225",        # Nikkei 225

    # 6-10
    "Shenzhen Stock Exchange":           "399001.SZSE", # SZSE Component
    "Hong Kong Exchanges and Clearing":  "HSI.HKEX",    # Hang Seng Index
    "TMX Group":                         "GSPTSE",      # S&P/TSX Composite
    "National Stock Exchange of India":  "NSEI.NSE",    # Nifty 50
    "BSE India Limited":                 "BSESN",       # BSE SENSEX

    # 11-15
    "Taiwan Stock Exchange":             "TWII.TWSE",   # TAIEX Dollar Index
    "Korea Exchange":                    "KS11.KOSPI",  # KOSPI Composite
    "Deutsche Boerse AG":                "GDAXI",       # DAX Performance Index
    "Saudi Exchange (Tadawul)":          "TASI.TADWUL", # Tadawul All Share Index
    "SIX Swiss Exchange":                "SSMI",        # Swiss Market Index

    # 16-20
    "ASX Australian Securities Exchange": "AXJO.ASX",   # S&P/ASX 200
    "Nasdaq Nordic and Baltics":          "OMXN40",     # OMX Nordic 40
    "BME Spanish Exchanges":              "IBEX",       # IBEX 35
    "Johannesburg Stock Exchange":        "J203.JSE",   # JSE All Share Index
    "B3 - Brasil Bolsa Balcão":           "BVSP",       # IBOVESPA

    # Other (in top 20 of previous years, but not in 2026/5's top 20)
    "LSE Group London Stock Exchange":    "FTSE",       # FTSE 100 Index
    "Tehran Stock Exchange":              "TEDPIX",     # TEDPIX Index
}

def get_current_month_year():
    from datetime import datetime
    now = datetime.now()
    return now.strftime("%B").lower(), now.year

""" 
Retrieves the top stock markets based on market capitalization from the WFE webpage. 
If any error occurs during retrieval or parsing, returns a default list of top 10 stock markets from may 2026.
Returns:    A tuple containing:
            - A list of dictionaries with keys 'Rank', 'Exchange', 'Symbol', and 'Market_Cap' for each of the top stock markets.
            - A status code (1 if data was retrieved successfully from the webpage, 0 if the default data is being returned due to an error).
"""
def get_top_markets(num_stocks=stock_num):
    month, year = get_current_month_year()
    wfe_url = f"https://focus.world-exchanges.org/issue/{month}-{year}/market-statistics"

    print(f"Fetching data from: {wfe_url}")
    
    try:
        response = requests.get(wfe_url)
        response.raise_for_status()
        
        # pandas read_html automatically finds all <table> tags in the HTML
        tables = pd.read_html(StringIO(response.text))
        
        if not tables:
            print("No tables found on the page.")
            raise ValueError("No tables found on the page.")

        # Assuming the main statistics table is the first one on the page.
        # (You may need to change the index if WFE adds formatting tables above it)
        df = tables[0]

        # Find the required column by locating a column whose next neighbor contains '%' in its name.
        percent_col_indices = [i for i, name in enumerate(df.columns) if '%' in str(name)]
        if not percent_col_indices:
            raise ValueError("Unable to locate a column followed by a '%' column in the table header.")

        required_col_index = percent_col_indices[0] - 1
        if required_col_index < 0:
            raise ValueError("The '%' column is in the first position, so there is no previous required column.")

        # Get the exchange and market cap column names based on the identified indices
        exchange_col = df.columns[0] 
        market_cap_col = df.columns[required_col_index]
        
        # Sort values by Market Cap descending and take the top 10
        # (Ensuring data is numeric, stripping commas/dollar signs if necessary)
        df[market_cap_col] = pd.to_numeric(df[market_cap_col].replace(',$', '', regex=True), errors='coerce')
        df = df[~df[exchange_col].astype(str).str.contains('Total', case=False, na=False)]
        top_df = df.nlargest(num_stocks, market_cap_col)

        # print(top_df)

        results = []
        for index, row in top_df.iterrows():
            exchange_name = str(row[exchange_col]).strip()
            
            # Look up the symbol, default to "UNKNOWN" if not found
            symbol = EXCHANGE_TO_INDEX_MAP.get(exchange_name, "UNKNOWN")

            # If we get "UNKNOWN", try to find a match by checking if the exchange name contains or is contained by any of the keys in our mapping
            if symbol == "UNKNOWN":
                contained_match = next((key for key in EXCHANGE_TO_INDEX_MAP if exchange_name in key), None)
                contained_by_match = next((key for key in EXCHANGE_TO_INDEX_MAP if key in exchange_name), None)
                if contained_match:
                    symbol = EXCHANGE_TO_INDEX_MAP[contained_match]
                    print(f"Matched unknown exchange '{exchange_name}' to containing key '{contained_match}'")
                elif contained_by_match:
                    symbol = EXCHANGE_TO_INDEX_MAP[contained_by_match]
                    print(f"Matched unknown exchange '{exchange_name}' to contained key '{contained_by_match}'")
                else:
                    raise ValueError(f"Could not find a ticker symbol for exchange '{exchange_name}'.")

            results.append({
                "Rank": len(results) + 1,
                "Exchange": exchange_name,
                "Symbol": symbol,
                "Market_Cap": row[market_cap_col]
            })
            
        return results, 1

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Returning a default list of top 10 exchanges from may 2026.")
        from DEFAULT_DATA.top_10_stock import TOP_TEN_STOCK
        return TOP_TEN_STOCK, 0

if __name__ == "__main__":
    top_markets, status= get_top_markets(stock_num)
    
    print("\n--- Top " + str(stock_num) + " Global Stock Markets ---" if status == 1 else "\n--- Default List of Top 10 Global Stock Markets ---")
    for market in top_markets:
        print(f"{market['Rank']}. {market['Exchange']} -> Ticker: {market['Symbol']}  (Market Cap: ${market['Market_Cap']:.2f}M)")