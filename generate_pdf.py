import datetime
from zoneinfo import ZoneInfo
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

def generate_pdf(json_data, output_filename="market_report.pdf"):
    # 1. Setup Document in Landscape
    # A4 landscape dimensions are automatically handled by passing landscape(A4)
    pdf = SimpleDocTemplate(output_filename, pagesize=landscape(A4),
                            leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    
    elements = []
    
    # 2. Setup Styles for Text
    styles = getSampleStyleSheet()
    
    # Title Styles
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Title'], fontSize=18, spaceAfter=5
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle', parent=styles['Normal'], fontSize=12, textColor=colors.slategray, spaceAfter=20, alignment=TA_CENTER
    )
    
    # Cell Styles (Left, Center, Right)
    cell_left = ParagraphStyle('CellLeft', parent=styles['Normal'], fontSize=8, leading=11)
    cell_center = ParagraphStyle('CellCenter', parent=cell_left, alignment=TA_CENTER)
    cell_right = ParagraphStyle('CellRight', parent=cell_left, alignment=TA_RIGHT)

    # 3. Add Header
    hkt = ZoneInfo("Asia/Hong_Kong")
    now_str = datetime.datetime.now(hkt).strftime('%Y-%m-%d %H:%M:%S HKT')
    elements.append(Paragraph("<b>Comprehensive Global Market Analysis</b>", title_style))
    elements.append(Paragraph(f"Generated using program written by LO Chun Ling", subtitle_style))
    elements.append(Paragraph(f"Generated on: {now_str}", subtitle_style))

    # 4. Define Table Headers
    table_data = [[
        Paragraph("<b>Rank</b>", cell_center),
        Paragraph("<b>Exchange & Region</b>", cell_left),
        Paragraph("<b>Identifiers</b>", cell_center),
        Paragraph("<b>Market Cap (USD)</b>", cell_center),
        Paragraph("<b>Quote Date</b>", cell_center),
        Paragraph("<b>Open / Close</b>", cell_center),
        Paragraph("<b>High / Low</b>", cell_center),
        Paragraph("<b>Daily Change</b>", cell_center),
        Paragraph("<b>Market Status</b>", cell_center)
    ]]

    # 5. Process JSON Data
    for item in json_data:
        # Core & Identifiers
        rank = str(item.get("Rank", "-"))
        exchange = item.get("Exchange", "N/A")
        country = item.get("country", "N/A")
        symbol = item.get("Symbol", "N/A")
        index = item.get("Index", "N/A")
        
        # Financials
        market_cap = f"{float(item.get('Market_Cap', 0)):,.2f}"
        open_price = f"{float(item.get('Open', 0)):,.2f}"
        high_price = f"{float(item.get('High', 0)):,.2f}"
        low_price = f"{float(item.get('Low', 0)):,.2f}"
        close_price = f"{float(item.get('Close', 0)):,.2f}"
        
        # Performance
        daily_change = float(item.get("Daily_Change", 0)) if item.get("Daily_Change") != "N/A" else "N/A"
        change_color = "green" if daily_change != "N/A" and daily_change >= 0 else "red"
        change_sign = "+" if daily_change != "N/A" and daily_change >= 0 else ""
        
        # Market Status & Timing
        is_open = item.get("is_market_open", False)
        status_text = "<font color='green'>OPEN</font>" if is_open else "<font color='red'>CLOSED</font>"
        time_info = f"Closes in: {item.get('time_to_close')}" if is_open else f"Opens in: {item.get('time_to_open')}"
        date = item.get("Quote_Date", "N/A")

        # Create rich-text Paragraphs for each cell to handle grouping and line breaks
        col_rank = Paragraph(rank, cell_center)
        col_exchange = Paragraph(f"<b>{exchange}</b><br/><font color='slategray'>{country}</font>", cell_left)
        col_identifiers = Paragraph(f"<b>{symbol}</b><br/><font color='slategray'>{index}</font>", cell_center)
        col_mcap = Paragraph(f"<b>{market_cap}M</b>", cell_center)
        col_date = Paragraph(f"{date}", cell_center)
        col_open_close = Paragraph(f"O: {open_price}<br/>C: <b>{close_price}</b>", cell_center)
        col_high_low = Paragraph(f"<font color='slategray'>H: {high_price}<br/>L: {low_price}</font>", cell_center)
        col_change = Paragraph(f"<font color='{change_color}'><b>{change_sign}{daily_change:.4f}%</b></font>", cell_center) if daily_change != "N/A" else Paragraph(f"<font color='{change_color}'><b>N/A</b></font>", cell_center)
        col_status = Paragraph(f"<b>{status_text}</b><br/><font color='slategray'>{time_info}</font>", cell_center)

        table_data.append([
            col_rank, col_exchange, col_identifiers, col_mcap, col_date,
            col_open_close, col_high_low, col_change, col_status
        ])

    # 6. Build and Style the Table
    # Define relative column widths (Total should fit within ~780 points for A4 landscape)
    # [Rank Exchange & Region, Identifiers, Market Cap (USD), Quote Date, Open / Close, High / Low, Daily Change, Market Status]
    col_widths = [40, 160, 60, 85, 60, 80, 70, 80, 120]
    
    table = Table(table_data, colWidths=col_widths, repeatRows=1) # repeatRows=1 repeats header on new pages
    
    style = TableStyle([
        # Header Styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.darkslategray),
        
        # General Table Styling
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LINEBELOW', (0, 1), (-1, -1), 0.5, colors.lightgrey),
    ])

    # Alternating Row Colors
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fafafa'))

    table.setStyle(style)
    elements.append(table)

    # 7. Add Page Break before Column Descriptions
    elements.append(PageBreak())
    
    description_title = ParagraphStyle(
        'DescriptionTitle', parent=styles['Title'], fontSize=14, spaceAfter=10, textColor=colors.darkslategray
    )
    description_text = ParagraphStyle(
        'DescriptionText', parent=styles['Normal'], fontSize=11, leading=14, spaceAfter=8
    )
    
    elements.append(Paragraph("<b>Column Descriptions</b>", description_title))
    
    descriptions = [
        "<b>Rank:</b> The rank of this market index among all tracked exchanges globally, by market capitalization.",
        "<b>Exchange & Region:</b> The name of the stock exchange and the country/region it operates in.",
        "&nbsp;&nbsp;&nbsp;&nbsp;• Region Data obtained from Twelve Data.",
        "<b>Identifiers:</b> The stock symbol and index name used to identify the market.",
        "<b>Market Cap (USD):</b> The total market capitalization in millions of USD.",
        "&nbsp;&nbsp;&nbsp;&nbsp;• Data obtained from the latest issue of Market Statistics by the World Federation of Exchanges (WFE).",
        "<b>Quote Date:</b> The date when the latest quote was recorded (UTC), associated with the following Open, High, Low, Close values.",
        "<b>Open / Close:</b> The opening price (O) and closing price (C) of the market index for the date in Quote Date.",
        "&nbsp;&nbsp;&nbsp;&nbsp;• Data obtained from Yahoo Finance.",
        "<b>High / Low:</b> The highest (H) and lowest (L) prices recorded for the market index during the Quote Date.",
        "&nbsp;&nbsp;&nbsp;&nbsp;• Data obtained from Yahoo Finance.",
        "<b>Daily Change:</b> The percentage change in the market closing index value compared to the previous trading day.",
        "&nbsp;&nbsp;&nbsp;&nbsp;• If \"N/A\", it means there are no 2 close prices available from the last 5 dates to calculate the change.",
        "<b>Market Status:</b> Indicates whether the market is currently OPEN or CLOSED, and displays the time until the market opens or closes.",
        "&nbsp;&nbsp;&nbsp;&nbsp;• Data obtained from Twelve Data."
    ]
    
    for desc in descriptions:
        elements.append(Paragraph(desc, description_text))

    # 8. Generate PDF
    pdf.build(elements)
    print(f"✅ ReportLab PDF successfully generated: {output_filename}")


def get_info_and_generate_pdf():
    import json
    from choose_top_stock import get_top_markets
    from get_stock_info import get_stock_info, get_stock_status, get_stock_quote

    # Prepare TOP_STOCKS json to generate the PDF
    TOP_STOCKS, status = get_top_markets(num_stocks=10, use_current_month = True, month="november", year=2019)  
    TOP_STOCKS, status = get_stock_info(TOP_STOCKS)
    TOP_STOCKS, status = get_stock_status(TOP_STOCKS, use_sample_states=False)
    TOP_STOCKS, status = get_stock_quote(TOP_STOCKS)
    
    # Write to top_stock_info.json for reference, then read from it
    with open("top_stock_info.json", "w") as f:
        json.dump(TOP_STOCKS, f, indent=4)
    with open("top_stock_info.json", "r") as f:
        json_list = json.load(f)
    
    # Generate the PDF report using the loaded JSON data
    generate_pdf(json_list)

if __name__ == "__main__":
    get_info_and_generate_pdf()