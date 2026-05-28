import pandas as pd
import requests
from io import StringIO

# Default number of top stocks to retrieve
stock_num = 20

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
def get_top_markets(num_stocks=stock_num, use_current_month=True, month=None, year=None):
    if use_current_month:
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
        df = tables[0]

        # Find the (as right as possible, but still meaningful) column by locating a column whose next neighbor contains '%' in its name.
        percent_col_indices = [i for i, name in enumerate(df.columns) if '%' in str(name)]
        if not percent_col_indices:
            raise ValueError("Unable to locate a column followed by a '%' column in the table header.")

        required_col_index = percent_col_indices[0] - 1
        if required_col_index < 0:
            raise ValueError("The '%' column is in the first position, so there is no previous required column.")

        # Get the exchange and market cap column names based on the identified indices
        exchange_col = df.columns[0] 
        market_cap_col = df.columns[required_col_index]
        
        # Sort values by Market Cap descending and take the top N
        # (Ensuring data is numeric, stripping commas/dollar signs if necessary)
        df[market_cap_col] = pd.to_numeric(df[market_cap_col].replace(',$', '', regex=True), errors='coerce')
        df = df[~df[exchange_col].astype(str).str.contains('Total', case=False, na=False)]
        top_df = df.nlargest(num_stocks, market_cap_col)

        # Print the table of top stocks with structure according to WFE website
        # print(top_df)

        results = []
        for index, row in top_df.iterrows():
            exchange_name = str(row[exchange_col]).strip()

            results.append({
                "Rank": len(results) + 1,
                "Exchange": exchange_name,
                # "Symbol": symbol,
                "Market_Cap": row[market_cap_col]
            })
            
        return results, 1

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Returning a default list of top 10 exchanges from may 2026.")
        try:
            from helper_program.DEFAULT_DATA.top_10_stock import TOP_TEN_STOCK
        except ModuleNotFoundError:
            from DEFAULT_DATA.top_10_stock import TOP_TEN_STOCK
        return TOP_TEN_STOCK, 0

if __name__ == "__main__":
    top_markets, status= get_top_markets(stock_num, use_current_month=True, month="april", year=2015)
    
    print("\n--- Top " + str(stock_num) + " Global Stock Markets ---" if status == 1 else "\n--- Default List of Top 10 Global Stock Markets ---")
    for market in top_markets:
        print(f"{market['Rank']}. {market['Exchange']} \t (Market Cap: ${market['Market_Cap']:.2f}M)")