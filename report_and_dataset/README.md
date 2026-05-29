# Project Report

## 1. Problem Statement

This project automates the end-to-end generation and delivery of a concise top-stock market report via WhatsApp. The primary problem addressed is the time-consuming, error-prone manual process of collecting up-to-date market-status and quote data across multiple global exchanges, formatting the information into a human-readable PDF, and delivering that report to stakeholders on demand.

### Key goals:
- Aggregate a short, accurate top-market summary from authoritative sources (WFE, Twelve Data, Yahoo Finance) with minimal manual effort.
- Produce a precise, portable, and easily understood PDF that combines market metadata, recent quotes, and status (open/closed) information.
- Deliver the PDF over WhatsApp Web automatically when a user requests it, enabling on-demand distribution without requiring users to run scripts or interact with APIs directly.

### Primary users and use cases:
- Financial analysts and advisors who need a quick global snapshot to share with clients.
- Small investing teams or automated systems that want scheduled or on-request market summaries.
- Personal or group chats where non-technical users can get a glimpse of the top stock exchanges.

### Scope and constraints:
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
- When Twelve Data or yfinance calls fail, the system returns status codes and preserves previously cached report.
- Playwright DOM selectors are wrapped with wait/try logic.
These all ensure smooth running of the system.


## 3. Evaluation Dataset
For the following evaluations in the next session, no sample datasets are used. All data and information are obtained dynamically from primary live sources: WFE, Twelve Data, and Yahoo Finance.
- This is because the expected result will change based on the time running the programs.

## 4. Evaluation Methods
### Unit test of `choose_top_stock.py`
- I tested this function by changing the month of accessing to 5 different months and running them in the main function of `choose_top_stock.py` at the root directory of the repository.
- I then checked on WFE website to verify the output printed on console are informatively correct.
- The result shows that all my tested case passed. The results in `2026/6`. `2026/5`, `2022/3`, `2018/1` can all be printed correctly. The result in `2015/12` prints the default 10 top stock exchanges from 2026/5 because WFE webpage only stores monthly report from 2018/1 and so on.
- This showcases the versatility for this program to access and retrieve information from WFE webpage for their different monthly report.
- Output references: In `/choose_top_stock Output` folder

### Unit test of `get_stock_info.py` and `generate_pdf.py`
Testing these together as it is difficult to evaluate get_stock_info.py without generate the corresponding PDF file for viewing. In the testing, the main function of `generate_pdf.py` is run at the root directory of the repository.
- Test case 1: PDF generation and correctness of information
  - I first tested this program by retriveing information from top 20 stocks (as determined by `choose_top_stock.py`) as in 2026/6 (and the stock information are retrieved in real time). The PDF is successfully generated, and I sampled 2 stock information (Nasdaq and HKEX) from their official website to sample the correctness right after the PDF is generated, which is verified to be correct.
  - Output references: In `/generate_pdf1 Output` folder

- Test case 2: Testing at different time and for different version of top stocks
  - I also tested this program at different times (at night, versus at noon in the above), and also from top 15 stocks as in 2021/7. The corresponding PDFs are successfully generated.
  - Note that the stock 'Tadawul' has "N/A" fields, I checked that it is because their latest quote date is ~7 days prior to the time of testing. After I changed my program to obtain latest 10 days from yfinance quotes, their quotes can be obtained (shown in `/generate_pdf3 Output/market_report_night2`). However, I still keep to only obtain quotes from latest 5 days, as yfinance will sometimes block my access if I obtain a large amount of quotes at a short period of time (this has happened during my testing).
  - Output references: In `/generate_pdf2 Output` folder

- Test case 3: Testing cases where APIs cannot be called successfully
  - I turned off my Internet and run this program to see what happens if the APIs cannot be called. As expected, if the root directory does not contain `market_report.pdf`, it will generate a PDF will lots of "N/A" fields (sample in `/generate_pdf3 Output/market_report_no_wifi`) at the root directory. Otherwise, it will not replace the existing PDF.
  - Output references: In `/generate_pdf3 Output` folder

### Testing of `whatsapp_bot.py`
- I tested this program by sending messages to myself, and to my friends.
- The intention classifier works as intended. In my testing, all text messages sent are correctly classified.
- The detection of new messages and the sending of the PDF file work smootly under long sessions. It is observed that a new message take ~5 seconds to detect, and the PDF file takes ~10 seconds to generate and send.
- Output references: 
  - https://youtu.be/QLa7MvjFv84 (testing 1 message with my friend) 
  - https://youtu.be/60hTNko3qJk (testing multiple messages from me) 

## 5. Experimental Results
The system runs smoothly and achieves the key goals described in Section 1: it aggregates a concise top-market summary from WFE, Twelve Data, and Yahoo Finance; produces a clear PDF report; and delivers that report automatically via WhatsApp Web on request.

During testing, the full end-to-end flow was stable: top exchange selection, data enrichment, PDF generation, intent detection, and WhatsApp sending all worked together without major interruption. The program successfully handled both real-time report requests and fallback conditions when APIs returned partial data.

There are still some limitations in this project. For instance,
- The program depends on external websites and APIs. If WFE, Twelve Data, Yahoo Finance, or WhatsApp Web change their page structure or API availability, the system may require updates.
- The exchange-to-symbol mapping in `helper_program/get_stock_info.py` is hardcoded and may not cover all future exchanges or symbol changes.
- WhatsApp Web automation relies on Playwright selectors in `whatsapp_bot.py`; updates to WhatsApp Web can break the attachment and send workflow.
- When API access is unavailable or rate-limited, generated reports may contain many "N/A" fields, and the bot may fall back to sending an older PDF copy if one already exists.
- The system assumes the user keeps the selected WhatsApp recipient open and does not switch chats while the bot is running, or else message detection may become unreliable.
- The current implementation is designed for small-scale, on-demand use rather than high-frequency automated distribution.

However, the current project is still considered suitable and sufficient for personal use.

## 6. Possible Future Directions
- Migrate from WhatsApp Web automation to an official WhatsApp Business API integration. This would reduce dependence on browser DOM selectors and improve reliability, but it requires registering a legitimate business account and subscribing to the WhatsApp Business API through an approved provider.
- Add a subscription-based delivery model so users can receive the PDF report automatically on a schedule (daily, weekly, market open/close) instead of requiring an explicit request message each time.
- Improve exchange coverage by replacing hardcoded symbol mappings with a dynamic exchange-symbol lookup service, or by using a richer market metadata provider to support new exchanges over time.
- Introduce a lightweight dashboard or admin interface for monitoring bot status, API health, and the latest generated reports.
- Extend the report content to include additional analytics: index performance comparisons, percentage changes over multiple intervals, sentiment notes, and optional attachments such as CSVs or Excel summaries.
