# Stock to WhatsApp Report Bot

A Python automation project that generates a top stock market PDF report and sends it via WhatsApp Web. The main entry point is `whatsapp_bot.py`.

## What it does

- Selects the top stock markets by market capitalization dynamically from the latest monthly WFE Market Statistics report (https://focus.world-exchanges.org/issue/may-2026/market-statistics for 2026/5 report).
- Uses Twelve Data and yfinance to enrich each market with current status and quote data.
  - Uses a hardcoded mapping of 20 exchange names to symbol/index values.
  - If a new report includes exchanges not in the dictionary, it falls back to a default top list from May 2026.
- Generates a styled PDF report with ReportLab.
  - If it is detected that the APIs are not called successfully, checks if the directory has a cached copy of the report. If so, do not replace the copy (and send this copy to the recipient). Otherwise, the new PDF can still be generated, although with lots of "N/A" fields.
- Uses Playwright and Cohere to automate WhatsApp Web and send the report when a request is detected.
  - New messages are detected every ~5 seconds, and generating and sending the PDF takes ~8 seconds.
  - The message is passed through AI, Cohere, for intent classification. Any messages intending to request market information will trigger to request.

## Key files

- `whatsapp_bot.py` - main automation script and WhatsApp listener.
- `src/generate_pdf.py` - collects stock data and generates `market_report.pdf`.
- `src/get_stock_info.py` - maps exchanges to symbols, fetches market status from Twelve Data, and fetches quotes from yfinance.
- `src/choose_top_stock.py` - scrapes WFE monthly reports and selects the top stock markets.
- `src/json_data/global_exchanges.json`, `src/json_data/global_states.json` - local cached market metadata and states.
- `src/json_data/top_stock_info.json` - generated JSON with the final stock report data.

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
  - Free accounts are limited to 20 API calls per minute and 1000 API calls per month.
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

## Video Showcase (Control+Click on the thumbnail to watch)
Showcase 1: Detecting 1 message from my friend
  - Note that the waiting time is mainly due to wait() functions set by me (but not due to processing). They can be reduced, as showcased in Showcase 2 below.

[![Watch the video](https://img.youtube.com/vi/QLa7MvjFv84/maxresdefault.jpg)](https://youtu.be/QLa7MvjFv84)

Showcase 2: Detecting multiple message from myself

[![Watch the video](https://img.youtube.com/vi/60hTNko3qJk/maxresdefault.jpg)](https://youtu.be/60hTNko3qJk)

## Limitations

- The stock mapping dictionary in `get_stock_info.py` is currently a static configuration validated against May 2026 market identifiers. While highly accurate for the current top 20 exchanges, dynamic resolution of new emerging exchanges is not yet supported and will default to the top 10 stock exchanges in May 2026.
- The repository currently relies heavily on DOM selectors from WhatsApp Web. If WhatsApp updates its web layout, CSS selectors in `whatsapp_bot.py` may need updating.
- The repository also relies on WFE's monthly report webpage . While this webpage is generally stable in terms of its webpage structure throughout years, CSS selectors in `choose_top_stock.py` may need updating if WFE webpage changes its structure.
- After the user have selected the recipient to receive the PDF (step 4 of Usage), the server should not switch to another recipient or type any message to the recipient, as these actions will interfere with the program's operation.
- This repository relies on several external API calls (Twelve Data, Yahoo Finance). If the API cannot be called (due to Free account's rate limits, weak Internet connection, ...), a cached copy of PDF may be used (which is not entirely up-to-date). If the cached copy does not exist, the generated PDF will have a large amount of missing fields.

## Compliance

1. Observe the rate limits of Twelve Data and Cohere API calls, as shown in the Configuration section.
2. Browser Automation techniques (mainly the Playwright library) are used when visiting WFE webpage and for the Whatsapp bot. While personal use of this technique should cause no consequences, please note that inappropriate use of Browser Automation, such as visiting WFE webpage at an extremely high frequency and sending Whatsapp messages at a high rate, may cause legal consequences under their Terms and Conditions.
3. This repository, including the codes and other files in the report, do not include any license files. Only use the code for non-commmercial purposes.
