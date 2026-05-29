# Project Report

## 1. Problem Statement

This project automates the end-to-end generation and delivery of a concise top-stock market report via WhatsApp. The primary problem addressed is the time-consuming, error-prone manual process of collecting up-to-date market-status and quote data across multiple global exchanges, formatting the information into a human-readable PDF, and delivering that report to stakeholders on demand.

Key goals:
- Aggregate a short, accurate top-market summary from authoritative sources (WFE, Twelve Data, Yahoo Finance) with minimal manual effort.
- Produce a precise, portable, and easily understood PDF that combines market metadata, recent quotes, and status (open/closed) information.
- Deliver the PDF over WhatsApp Web automatically when a user requests it, enabling on-demand distribution without requiring users to run scripts or interact with APIs directly.

Primary users and use cases:
- Financial analysts and advisors who need a quick global snapshot to share with clients.
- Small investing teams or automated systems that want scheduled or on-request market summaries.
- Personal or group chats where non-technical users can get a glimpse of the top stock exchanges.

Scope and constraints:
- The system depends on third-party web pages and APIs (WFE, Twelve Data, Yahoo Finance) and therefore inherits their availability and schema stability.
- WhatsApp delivery relies on Playwright DOM selectors for WhatsApp Web; changes to WhatsApp Web may require selector updates.
- The repository contains a hardcoded exchange-to-symbol mapping for resilience; if an exchange is new or unmapped, a default dataset is used as fallback.

## 2. Methodology

### Overview
- The project is organized into a small set of cooperating modules that fetch, normalize, render, and deliver market information.

### Main components
`helper_program.choose_top_stock.py`
Scrapes the World Federation of Exchanges (WFE) monthly "Market Statistics" page based on the current month, and extracts the top exchanges by market capitalization. If scraping fails or table layout changes, a local default (`helper_program/DEFAULT_DATA/top_10_stock.py`) is used as a safe fallback.

`helper_program.get_stock_info.py`
Maps exchanges to representative Twelve Data index names and yfinance tickers, then fetches global market state metadata to Twelve Data API (temporarily cached in `helper_program/json_data/global_states.json`), and retrieves recent quotes from Yahoo Finance via `yfinance`.

`helper_program.generate_pdf.py`
Consumes the enriched JSON dataset (`helper_program/json_data/top_stock_info.json`) and creates a styled landscape PDF using ReportLab with headers, a results table, and explanatory notes.

`whatsapp_bot.py`
The orchestrator and runtime entry point. Uses Playwright to open a persistent Chromium context for WhatsApp Web, monitors the selected chat for incoming messages, uses Cohere to detect intent (whether a user requested a market PDF), and triggers `get_info_and_generate_pdf()` from `helper_program.generate_pdf` to build and send `market_report.pdf`.

### How a request is handled (high-level flow)
1. A user sends a message in the selected WhatsApp chat.
2. `whatsapp_bot` detects the newest message and sends the text to Cohere for intent classification (YES/NO).
3. On a positive intent match, `generate_pdf.get_info_and_generate_pdf()` runs: it fetches top exchanges, enriches them, writes `top_stock_info.json`, and generates `market_report.pdf`.
4. `whatsapp_bot` automates the WhatsApp attachment flow (clipboard/upload) to send the PDF to the requesting chat.

### Prerequisites for the server
- The environment provides API keys in a `.env` file: `TWELVEDATA_API_KEY` and `COHERE_API_KEY`.
- Playwright browsers are installed (`python -m playwright install chromium`) and the user can scan the WhatsApp QR code for initial login.
- Python dependencies listed in `requirements.txt` are installed in the runtime environment.
- The device running `whatsapp_bot.py` can connect to the Internet to use API and send Whatsapp messages.

### Design choices
1. Primary live sources: WFE (choose top exchanges), Twelve Data (market states / exchange metadata), and Yahoo Finance (quotes via `yfinance`).
  - These data sources are credible, contiuously updating, free of charge to access, and well-known.
2. Local cached JSON files (`helper_program/json_data/global_states.json`, `helper_program/json_data/top_stock_info.json`) in `helper_program/json_data`
  - Act as offline samples for development/testing. For example, `helper_program/get_stock_info.get_stock_status()` accepts parameter `use_sample_data`, which helps reduce rate-limited API calls when testing.
3. Fallbacks at multiple layers
- When WFE scraping fails, the default dataset is loaded.
- When Twelve Data or yfinance calls fail, the system returns status codes and preserves previously cached data.
- Playwright DOM selectors are wrapped with wait/try logic.
  - These all ensure smooth running of the system.


## 3. Evaluation Dataset
For the following evaluations in the next session, no sample datasets are used. All data and information are obtained dynamically from primary live sources: WFE, Twelve Data, and Yahoo Finance.
- This is because the expected result will change based on the time running the programs.

## 4. Evaluation Methods

- Describe how you evaluate or validate the report generation and automation.
- Explain whether you use live API checks, manual validation, or automated tests.
- Mention any metrics or criteria used to determine success.

### Unit test of `choose_top_stock.py`
- I tested this function by changing the month of accessing to 5 different months and running them in the main function of this file.
- I then checked on WFE website to verify the output printed on console are informatively correct.
- The result shows that all my tested case passed. The results in `2026/6`. `2026/5`, `2022/3`, `2018/1` can all be printed correctly. The result in `2015/12` prints the default 10 top stock exchanges from 2026/5 because WFE webpage only stores monthly report from 2018/1 and so on.
- This showcases the versatility for this program to access and retrieve information from WFE webpage for their different monthly report.
- All the printed results are stored in `choose_top_stock Output` for reference.

### Unit test of `get_stock_info.py` and `generate_pdf.py`
Testing these together as it is difficult to evaluate get_stock_info.py without generate the corresponding PDF file for viewing.
- Test case 1: PDF generation and correctness of information
  - I first tested this program by retriveing information from top 20 stocks (as determined by `choose_top_stock.py`) as in 2026/6 (and the stock information are retrieved in real time). The PDF is successfully generated, and I sampled 2 stock information (Nasdaq and HKEX) from their official website to sample the correctness right after the PDF is generated, which is verified to be correct.
  - Output references: In `generate_pdf1 Output` folder: `market_report_noon`, `noon_report_Nasdaq_check.png`, `noon_report_HKEX_check.png`

- Test case 2: Testing at different time and for different version of top stocks

## 5. Experimental Results

- Summarize the outcomes of running the system.
- Note any observed behavior, such as successful PDF generation, message detection, and WhatsApp delivery.
- Mention limitations, failure modes, or areas for improvement.
