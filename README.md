# Stock to WhatsApp Report Bot

A Python automation project that generates a top stock market PDF report and sends it via WhatsApp Web. The main entry point is `whatsapp_bot.py`.

## What it does

- Selects the top stock markets dynamically from the latest monthly WFE Market Statistics report.
  - If a new report includes exchanges not in the dictionary, it falls back to a default top list from May 2026.
- Uses Twelve Data and yfinance to enrich each market with current status and quote data.
  - Uses a hardcoded mapping of 20 exchange names to symbol/index values.
- Generates a styled PDF report with ReportLab.
  - If it is detected that the APIs are not called successfully, checks if the directory has a cached copy of the report. If so, do not replace the copy (and send this copy to the recipient). Otherwise, the new PDF can stil be generated, although with lots of "N/A" fields.
- Uses Playwright and Cohere to automate WhatsApp Web and send the report when a request is detected.
  - New messages are detected every ~5 seconds, and generating and sending the PDF takes ~10 seconds.

## Key files

- `whatsapp_bot.py` - main automation script and WhatsApp listener.
- `helper_program/generate_pdf.py` - collects stock data and generates `market_report.pdf`.
- `helper_program/get_stock_info.py` - maps exchanges to symbols, fetches market status from Twelve Data, and fetches quotes from yfinance.
- `helper_program/choose_top_stock.py` - scrapes WFE monthly reports and selects the top stock markets.
- `helper_program/json_data/global_exchanges.json`, `helper_program/json_data/global_states.json` - local cached market metadata and states.
- `helper_program/json_data/top_stock_info.json` - generated JSON with the final stock report data.

## Requirements

- Python 3.10+ recommended
- Internet access for API calls and WhatsApp Web
- APIs required:
  - `TWELVEDATA_API_KEY`
  - `COHERE_API_KEY`

## Installation

1. Clone the repo and open the workspace.
2. Create a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. Install Playwright browser support:

```powershell
playwright install chromium
```

## Configuration

Create a `.env` file in the repository root with these keys:

```dotenv
TWELVEDATA_API_KEY = your_twelve_data_api_key
COHERE_API_KEY = your_cohere_api_key
```

Both keys can be obtained for free, but you need to create accounts, and their usage are rate-limited:
- TWELVEDATA_API_KEY: https://twelvedata.com/
  - Free accounts are limited to 8 API calls per minute and 800 API calls per day.
  - This program uses 1 API call for processing each PDF request from recipient.
- COHERE_API_KEY: https://dashboard.cohere.com/
  - Free accounts are limited to 20 API calls per minute.
  - This program uses 1 API call for processing each recipient's Whatsapp message.

## Usage

1. Run the bot:

```powershell
python whatsapp_bot.py
```

2. The script will open WhatsApp Web in a Chromium browser.
3. Scan the QR code if needed.
4. Select the recipient chat in WhatsApp Web.
5. The bot will listen for incoming messages from the selected recipient.
6. If Cohere detects a request for a stock market report, the bot generates `market_report.pdf` and sends it.

## Video Showcase
Showcase 1: Detecting 1 message from my friend
  - Note that the waiting time is mainly due to wait() functions set by me (but not due to processing). They can be reduced, as showcased in Showcase 2 below.
[![Watch the video](https://youtu.be/QLa7MvjFv84)](https://youtu.be/QLa7MvjFv84)

Showcase 2: Detecting multiple message from myself
[![Watch the video](https://youtu.be/60hTNko3qJk)](https://youtu.be/60hTNko3qJk)

## Limitations

- The stock mapping in `get_stock_info.py` is hardcoded based on the Twelve Data API on stock exchange information, my limited knowledge, and checking using Gen-AI. I cannot gaurantee that the mapping to stock symbols and representative indices are 100% correct and updated. 
- Moreover, as the mapping only includes the 20 stock exchanges from the top 20 in 2026/5, if any new stock exchanges rise up in the future, this program cannot obtain its information and resort to display the up-to-date information of the default 10 stock exchanges.
- The repository currently relies heavily on DOM selectors from WhatsApp Web. If WhatsApp updates its web layout, CSS selectors in `whatsapp_bot.py` may need updating.
- The repository also relies on WFE's monthly report webpage (https://focus.world-exchanges.org/issue/may-2026/market-statistics for 2026/5 report). While this webpage is generally stable in terms of its webpage structure throughout years, CSS selectors in `choose_top_stock.py` may need updating if WFE webpage changes its structure.
- After you have select the recipient to receive the PDF (step 4 of Usage), you should not switch to another recipient or type any message to the recipient, as these actions will interfere with the program's operation.
- This repository relies on several external API calls (Twelve Data, Yahoo Finance). If the API cannot be called (due to Free account's rate limits, weak Internet connection, ...), a cached copy of PDF may be used (which is not entirely up-to-date), or the generated PDF will have a large amount of missing fields.

## Compliance

1. Observe the rate limits of Twelve Data and Cohere API calls, as shown in the Configuration session.
2. Browser Automation techniques (mainly the Playwright library) are used when visiting WFE webpage and for the Whatsapp bot. While personal use of this technique should cause no consequences, please note that inappropriate use of Browser Automation, such as visiting WFE webpage at an extremely high frequency and sending Whatsapp messages at a high rate, may cause legal consequences under their Terms and Conditions.
3. This repository, including the codes and other files in the report, do not include any license files. Only use the code for non-conmmercial purposes.
