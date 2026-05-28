import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import cohere
from helper_program.generate_pdf import get_info_and_generate_pdf

# Load your COHERE_API_KEY from a .env file
load_dotenv()
client = os.getenv("COHERE_API_KEY")

"""
Uses Cohere AI API to determine if the user is asking for the top stock PDF.
Returns: 0 if the user is NOT asking for the top stock PDF.
         1 if the user IS asking for the top stock PDF.
         2 if the API cannot be called properly.
"""
def detect_intent(message_text):
    if not message_text or len(message_text) < 2:
        return False
        
    prompt = f"""
    Analyze the following message. Is the user asking for a stock market report, 
    financial summary, or market PDF? 
    Reply strictly with 'YES' or 'NO'. 
    
    Message: "{message_text}"
    """
    
    try:
        co = cohere.ClientV2(client)
        response = co.chat(
            model="command-a-plus-05-2026", 
            messages=[{"role": "user", "content": prompt}]
        )
        print(response)
        print(response.message.content[1].text)
        return response.message.content[1].text.upper().strip('.,! ') == "YES"
    except Exception as e:
        print(f"AI Error: {e}")
        return 2

"""
Finds the newest message by CSS selector using binary search on layer1 and layer2.
First binary searches layer1 (with layer2 = 1), then binary searches layer2 (with found layer1).
Returns: A string of the newest message in the Whatsapp Chat if the message is text only.
         Empty string is returned otherwise.
"""
def find_newest_message(page):
    
    def selector_exists(selector, timeout=100):
        """Check if a selector exists without raising an exception"""
        try:
            page.wait_for_selector(selector, timeout=timeout)
            return True
        except:
            return False
    
    def get_selector1(layer1):
        """Get selector, when a specific layer has exactly 1 message sent."""
        return f"#main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div > div.x10l6tqk.x13vifvy.x1o0tod.xupqr0c.x9f619.x78zum5.xdt5ytf.xh8yej3.x5yr21d.x6ikm8r.x1rife3k.xjbqb8w.x1ewm37j > div.x3psx0u.x12xbjc7.x1c1uobl.xrmvbpv.xh8yej3.xquzyny.xvc5jky.x11t971q > div:nth-child({layer1}) > div > div > div > div > div > div > div._amk4.false.false._amkd._amk5.false > div._amk6._amlo.false.false > div:nth-child(2) > div > div.copyable-text > div > span.x1f6kntn.xjb2p0i.x8r4c90.xo1l8bm.x1ic7a3i.x12xpedu._ao3e._aupe.copyable-text > span"
    
    def get_selector1a(layer1):
        """Get selector, when a specific layer has exactly 1 message sent."""
        return f"#main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div > div.x10l6tqk.x13vifvy.x1o0tod.xupqr0c.x9f619.x78zum5.xdt5ytf.xh8yej3.x5yr21d.x6ikm8r.x1rife3k.xjbqb8w.x1ewm37j > div.x3psx0u.x12xbjc7.x1c1uobl.xrmvbpv.xh8yej3.xquzyny.xvc5jky.x11t971q > div:nth-child({layer1}) > div > div > div > div > div > div > div._amk4.false.false._amkd._amk5.false > div._amk6._amlo.false.false > div:nth-child(1) > div > div.copyable-text > div > span.x1f6kntn.xjb2p0i.x8r4c90.xo1l8bm.x1ic7a3i.x12xpedu._ao3e._aupe.copyable-text > span"
    
    def get_selector2(layer1, layer2):
        """Get selector, when a specific layer has more than 1 message sent."""
        return f"#main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div > div.x10l6tqk.x13vifvy.x1o0tod.xupqr0c.x9f619.x78zum5.xdt5ytf.xh8yej3.x5yr21d.x6ikm8r.x1rife3k.xjbqb8w.x1ewm37j > div.x3psx0u.x12xbjc7.x1c1uobl.xrmvbpv.xh8yej3.xquzyny.xvc5jky.x11t971q > div:nth-child({layer1}) > div:nth-child({layer2}) > div > div > div > div > div > div._amk4.false.false._amkd.false > div._amk6._amlo.false.false > div:nth-child(2) > div > div.copyable-text > div > span.x1f6kntn.xjb2p0i.x8r4c90.xo1l8bm.x1ic7a3i.x12xpedu._ao3e._aupe.copyable-text > span"
    
    def get_selector2a(layer1, layer2):
        """Get selector, when a specific layer has more than 1 message sent."""
        return f"#main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div > div.x10l6tqk.x13vifvy.x1o0tod.xupqr0c.x9f619.x78zum5.xdt5ytf.xh8yej3.x5yr21d.x6ikm8r.x1rife3k.xjbqb8w.x1ewm37j > div.x3psx0u.x12xbjc7.x1c1uobl.xrmvbpv.xh8yej3.xquzyny.xvc5jky.x11t971q > div:nth-child({layer1}) > div:nth-child({layer2}) > div > div > div > div > div > div._amk4.false.false._amkd.false > div._amk6._amlo.false.false > div:nth-child(1) > div > div.copyable-text > div > span.x1f6kntn.xjb2p0i.x8r4c90.xo1l8bm.x1ic7a3i.x12xpedu._ao3e._aupe.copyable-text > span"

    def get_selector3(layer1):
        """Get selector, which contains non-standard / non-text message."""
        return f"#main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div > div.x10l6tqk.x13vifvy.x1o0tod.xupqr0c.x9f619.x78zum5.xdt5ytf.xh8yej3.x5yr21d.x6ikm8r.x1rife3k.xjbqb8w.x1ewm37j > div.x3psx0u.x12xbjc7.x1c1uobl.xrmvbpv.xh8yej3.xquzyny.xvc5jky.x11t971q > div:nth-child({layer1}) > div"
                 
    def get_selector3a(layer1, layer2):
        """Get selector, which contains non-standard / non-text message."""
        return f"#main > div.x1n2onr6.x1vjfegm.x1cqoux5.x14yy4lh > div > div > div.x10l6tqk.x13vifvy.x1o0tod.xupqr0c.x9f619.x78zum5.xdt5ytf.xh8yej3.x5yr21d.x6ikm8r.x1rife3k.xjbqb8w.x1ewm37j > div.x3psx0u.x12xbjc7.x1c1uobl.xrmvbpv.xh8yej3.xquzyny.xvc5jky.x11t971q > div:nth-child({layer1}) > div:nth-child({layer2}) > div"

    # Binary search on layer1 (with layer2=1)
    low_layer1, high_layer1 = 1, 20
    best_layer1 = None
    
    while low_layer1 <= high_layer1:
        # print(low_layer1, high_layer1)
        mid_layer1 = (low_layer1 + high_layer1) // 2
        
        # Try message_selector2 with layer2=1
        if selector_exists(get_selector2(mid_layer1, 1) or selector_exists(get_selector2a(mid_layer1, 1))):
            best_layer1 = mid_layer1
            low_layer1 = mid_layer1 + 1
        # Try message_selector1 or selector3 (alternative for layer2=1)
        elif selector_exists(get_selector1(mid_layer1)) or selector_exists(get_selector1a(mid_layer1)) or selector_exists(get_selector3(mid_layer1) or selector_exists(get_selector3a(mid_layer1, 1))):
            best_layer1 = mid_layer1
            low_layer1 = mid_layer1 + 1
        else:
            high_layer1 = mid_layer1 - 1
    
    if best_layer1 is None:
        return ""
    
    # Binary search on layer2 with best_layer1
    low_layer2, high_layer2 = 1, 20
    best_layer2 = None
    
    while low_layer2 <= high_layer2:
        # print(low_layer2, high_layer2)
        mid_layer2 = (low_layer2 + high_layer2) // 2
        
        # Try message_selector2
        if selector_exists(get_selector2(best_layer1, mid_layer2)) or selector_exists(get_selector2a(best_layer1, mid_layer2)) or selector_exists(get_selector3a(best_layer1, mid_layer2)):
            best_layer2 = mid_layer2
            low_layer2 = mid_layer2 + 1
        # If layer2=1, also try message_selector1 or selector3
        elif mid_layer2 == 1 and (selector_exists(get_selector1(best_layer1)) or selector_exists(get_selector1a(best_layer1)) or selector_exists(get_selector3(best_layer1)) ):
            best_layer2 = mid_layer2
            low_layer2 = mid_layer2 + 1
        else:
            high_layer2 = mid_layer2 - 1
    
    if best_layer2 is None:
        return ""
    
    # Fetch the message using found layer1 and layer2
    try:
        incoming_message = page.locator(get_selector2(best_layer1, best_layer2)).text_content(timeout=1000)
        # print(best_layer1, best_layer2)
        print(f"Latest message: {incoming_message}")
        return incoming_message
    except:
        pass
    try:
        incoming_message = page.locator(get_selector2a(best_layer1, best_layer2)).text_content(timeout=1000)
        # print(best_layer1, best_layer2)
        print(f"Latest message: {incoming_message}")
        return incoming_message
    except:
        # Try selector1 if layer2=1. Selector3 skipped as they are non-text element only to aid the binary search.
        if best_layer2 == 1:
            try:
                incoming_message = page.locator(get_selector1(best_layer1)).text_content(timeout=1000)
                print(best_layer1, best_layer2)
                print(incoming_message)
                return incoming_message
            except:
                pass
            try:
                incoming_message = page.locator(get_selector1a(best_layer1)).text_content(timeout=1000)
                print(best_layer1, best_layer2)
                print(incoming_message)
                return incoming_message
            except:
                pass
        
        print(best_layer1, best_layer2)
        return ""

"""
The main loop to automate detection of message and sending of the PDF file when needed.
"""
def run_whatsapp_bot(pdf_filepath):
    main_search_selector = "#_r_9_"
    input_field_selector = "#main > footer > div.x1n2onr6.xhtitgo.x9f619.x78zum5.x1q0g3np.xuk3077.xjbqb8w.x1wiwyrm.xquzyny.xvc5jky.x11t971q.xnpuxes.copyable-area > div > span > div > div > div > div.x1n2onr6.xh8yej3.xjdcl3y.lexical-rich-text-input > div.x1hx0egp.x6ikm8r.x1odjw0f.x1k6rcq7.x6prxxf > p"
    send_button_selector = "#main > footer > div.x1n2onr6.xhtitgo.x9f619.x78zum5.x1q0g3np.xuk3077.xjbqb8w.x1wiwyrm.xquzyny.xvc5jky.x11t971q.xnpuxes.copyable-area > div > span > div > div > div > div.x9f619.x78zum5.x6s0dn4.xl56j7k.xpvyfi4.x2lah0s.x1c4vz4f.x1fns5xo.x1ba4aug.x1c9tyrk.xeusxvb.x1pahc9y.x1ertn4p.x1pse0pq.xpcyujq.xfn3atn.x1ypdohk.x1m2oepg > div > span > div > button > div > div > div:nth-child(1) > span"
    file_button_selector ="#app > div > div > div.x78zum5.xdt5ytf.x5yr21d > div > div.x10l6tqk.x13vifvy.x1o0tod.x78zum5.xh8yej3.x5yr21d.x6ikm8r.x10wlt62.x47corl > div.x9f619.x1n2onr6.x5yr21d.x6ikm8r.x10wlt62.x17dzmu4.x1i1dayz.x2ipvbc.xjdofhw.xyyilfv.x1iyjqo2.xpilrb4.x1t7ytsu.x1vb5itz.x12xzxwr > div > span > div > div > div > div.x1n2onr6.xupqr0c.x78zum5.x1r8uery.x1iyjqo2.xdt5ytf.x1hc1fzr.x6ikm8r.x10wlt62 > div > div.x78zum5.x1c4vz4f.x2lah0s.x1helyrv.x6s0dn4.x1qughib.x178xt8z.x13fuv20.xx42vgk.x1y1aw1k.xwib8y2.xf7dkkf.xv54qhq > div.x1247r65.xng8ra > span > div > div > span"
    send_text_selector = "#app > div > div > div.x78zum5.xdt5ytf.x5yr21d > div > div.x10l6tqk.x13vifvy.x1o0tod.x78zum5.xh8yej3.x5yr21d.x6ikm8r.x10wlt62.x47corl > div.x9f619.x1n2onr6.x5yr21d.x6ikm8r.x10wlt62.x17dzmu4.x1i1dayz.x2ipvbc.xjdofhw.xyyilfv.x1iyjqo2.xpilrb4.x1t7ytsu.x1vb5itz.x12xzxwr > div > span > div > div > div > div.x1n2onr6.xupqr0c.x78zum5.x1r8uery.x1iyjqo2.xdt5ytf.x1hc1fzr.x6ikm8r.x10wlt62 > div > div.x1c4vz4f.xs83m0k.xdl72j9.x1g77sc7.x78zum5.xozqiw3.x1oa3qoh.x12fk4p8.xeuugli.x2lwn1j.x1nhvcw1.xdt5ytf.x6s0dn4.x1n2onr6.x6ikm8r.x10wlt62.x5yr21d > div.x1c4vz4f.xs83m0k.xdl72j9.x1g77sc7.x78zum5.xozqiw3.x1oa3qoh.x12fk4p8.xeuugli.x1nhvcw1.xdt5ytf.x6s0dn4.x1n2onr6.xbktkl8.x16ovd2e.xvtqlqk.xvpt6g3.xdx6fka.xh8yej3 > div > div > div.x1n2onr6.xh8yej3.x1iyjqo2.xs83m0k.x1t1x2f9.xeuugli.x1k70j0n.x14z9mp.xzueoph.x1lziwak.xisnujt.x14ug900.x1vvkbs.x126k92a.x1hx0egp.lexical-rich-text-input > div.x1hx0egp.x6ikm8r.x1odjw0f.x1k6rcq7.x1lkfr7t > p"
    print("🚀 Starting WhatsApp Playwright Automation...")
    
    # Use a persistent context so you don't have to scan the QR code every time
    user_data_dir = "./whatsapp_session_data"
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False, # Set to False so you can scan the QR code the first time!
            viewport={"width": 1280, "height": 720}
        )

        page = browser.new_page()
        page.goto("https://web.whatsapp.com/")
        print("⏳ Waiting for WhatsApp Web to load (Scan QR if needed)...")
        
        # Wait until the main search box appears (indicates successful login)
        page.wait_for_selector(main_search_selector, timeout=60000)
        print("✅ Logged in!")

        # 1. Ask user to select a recipient first, until the message input box is detected
        print(f"Please choose the recipient for the PDF report by searching their name in WhatsApp Web.")
        page.wait_for_selector(input_field_selector, timeout=60000)

        print("✅ Recipient chosen! Please wait for initialization...")
        previous_message = find_newest_message(page)
        
        # Start the Main Listening Loop
        print("🎧 Now listening for PDF requests...")
        while True:
            try:
                # 2. Detect the latest message in each loop, so as to know whether AI needs to evaluate the message
                incoming_message = find_newest_message(page)

                if incoming_message != "" and incoming_message != previous_message:
                    print(f"📩 New Message Detected: {incoming_message}")
                    previous_message = incoming_message
                    
                    # 3. Pass to our Cohere AI
                    if detect_intent(incoming_message) == 1:
                        print("🤖 AI Detected Intent: YES! Generating and sending PDF...")
                        
                        get_info_and_generate_pdf()
                        
                        # 4. Automate the Attachment Flow
                        command = f"powershell Set-Clipboard -LiteralPath {pdf_filepath}"
                        os.system(command)
                        page.keyboard.press('Control+V')
                        page.fill(send_text_selector, "Here is your requested top stock info PDF.")
                        page.wait_for_timeout(2000) # Wait for upload to complete
                        page.click(file_button_selector, timeout=2000)
                        
                        print(f"✅ PDF sent successfully to recipient!")

                    else:
                        print("🤖 AI Detected Intent: NO. Waiting for next message...")
                            
            except Exception as e:
                print(f"Loop error (likely DOM changed): {e}")
                
            # Check every 2 seconds to avoid spamming the CPU
            time.sleep(2)
    

if __name__ == "__main__":
    pdf_filepath = "market_report.pdf"
    run_whatsapp_bot(pdf_filepath = pdf_filepath)
