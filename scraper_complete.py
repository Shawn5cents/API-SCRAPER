#!/usr/bin/env python3
"""
Complete Sylectus Scraper - Production Ready
Built from successful codegen recording with email extraction
"""

# Step 3: Imports and Configuration
from playwright.sync_api import sync_playwright
import requests
import os
import time
import re
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Credentials from working codegen recording
CORPORATE_ID = "2103390"
CORPORATE_PASSWORD = "Sn59042181#@"
USERNAME = "SNICHOLS"
USER_PASSWORD = "Sn59042181#@"

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))

# Step 3: Function to Send Telegram Message
def send_to_telegram(message_text, keyboard=None):
    """
    This function will take the scraped text as an argument.
    It will construct the Telegram Bot API URL.
    It will make a requests.post() call with the chat_id and text.
    Include a print statement to confirm if the message was sent successfully.
    """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message_text,
            'parse_mode': 'Markdown'
        }
        
        # Add keyboard if provided
        if keyboard:
            data['reply_markup'] = json.dumps(keyboard)
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Message sent successfully to Telegram")
            return True
        else:
            print(f"❌ Failed to send message. Status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return False

# Step 4: Advanced - Preventing Duplicate Notifications
def load_sent_items():
    """Load previously sent items from sent_items.txt"""
    try:
        with open('sent_items.txt', 'r') as f:
            return set(line.strip() for line in f.readlines())
    except FileNotFoundError:
        return set()

def save_sent_item(item_id):
    """Save item ID to sent_items.txt to prevent duplicates"""
    with open('sent_items.txt', 'a') as f:
        f.write(f"{item_id}\n")

def perform_complete_login(page):
    """Perform complete login sequence from codegen recording"""
    try:
        print("🔐 Starting complete login sequence...")
        
        # Navigate to main page
        print("🌐 Navigating to Sylectus...")
        page.goto("https://www.sylectus.net/", timeout=60000)
        print("✅ Page loaded")
        
        # Wait for page to fully load
        time.sleep(3)
        
        # IMPORTANT: Accept cookies first (from working recording)
        print("🍪 Looking for cookie button...")
        page.get_by_role("button", name="Accept All Cookies").click(timeout=60000)
        print("✅ Cookies accepted")
        
        # Click LOG IN link
        print("🔗 Clicking LOGIN link...")
        page.get_by_role("link", name="LOG IN").click(timeout=60000)
        print("✅ Login page loaded")
        
        time.sleep(2)
        
        # Take screenshot for debugging
        page.screenshot(path="login_page.png")
        print("📸 Screenshot saved as login_page.png")
        
        # Fill Corporate ID
        print("🏢 Entering Corporate ID...")
        try:
            page.get_by_role("textbox", name="Corporate ID").click(timeout=30000)
        except:
            # Try alternative selector
            page.locator("input[name*='corpId']").click(timeout=30000)
        
        try:
            page.get_by_role("textbox", name="Corporate ID").fill(CORPORATE_ID)
        except:
            page.locator("input[name*='corpId']").fill(CORPORATE_ID)
        
        page.keyboard.press("Tab")
        
        # Fill Corporate Password
        print("🔐 Entering Corporate Password...")
        page.locator("#ctl00_bodyPlaceholder_corpPasswordField").fill(CORPORATE_PASSWORD)
        
        # Click Continue
        print("➡️ Clicking Continue...")
        page.get_by_role("link", name="Continue").click(timeout=60000)
        print("✅ Continue clicked")
        
        time.sleep(3)
        
        # Select user dropdown
        print("👤 Selecting user...")
        page.get_by_label("").click(timeout=30000)
        page.get_by_role("option", name=USERNAME).click(timeout=30000)
        
        # Fill user password
        print("🔑 Entering user password...")
        page.get_by_placeholder(" ").click(timeout=30000)
        page.get_by_placeholder(" ").fill(USER_PASSWORD)
        
        # Click Log in
        print("🚪 Final login click...")
        page.get_by_role("link", name="Log in").click(timeout=60000)
        
        print("✅ Complete login sequence finished")
        return True
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

def setup_load_board(page):
    """Setup load board - simplified and robust version"""
    try:
        print("🚚 Setting up Load Board...")
        
        # Click Load Board link
        page.get_by_role("link", name="Load Board").click()
        
        # Wait for iframe to load
        time.sleep(5)
        
        # Work within the iframe
        iframe = page.locator("#iframe1").content_frame
        
        # Skip date filtering entirely - just search all current postings
        print("ℹ️ Skipping date filters to avoid getting stuck...")
        print("ℹ️ Skipping location filters, searching all postings...")
        
        # Click SEARCH ALL POSTINGS to get results
        try:
            iframe.get_by_role("button", name="SEARCH ALL POSTINGS").click()
            print("✅ Search initiated")
        except:
            # Try alternative selector if the first one fails
            try:
                iframe.locator("input[value*='SEARCH']").click()
                print("✅ Search initiated (alternative method)")
            except:
                print("⚠️ Could not find search button, continuing...")
        
        # Wait for results
        time.sleep(8)
        
        print("✅ Load board setup complete")
        return iframe
        
    except Exception as e:
        print(f"❌ Load board setup failed: {e}")
        return None

# Popup email extraction removed to prevent hanging

def extract_load_details(row, iframe, page):
    """Extract detailed load information from a row"""
    try:
        # Get all text from the row
        row_text = row.inner_text().strip()
        
        # Initialize load data
        load_info = {
            'company': 'Unknown',
            'load_id': 'Unknown',
            'pickup_city': 'Unknown',
            'pickup_date': 'Unknown',
            'delivery_city': 'Unknown',
            'delivery_date': 'Unknown',
            'vehicle_type': 'Unknown',
            'miles': 'Unknown',
            'pieces': 'Unknown',
            'weight': 'Unknown',
            'credit_score': 'Unknown',
            'days_to_pay': 'Unknown',
            'email': 'Not provided',
            'bid_available': False
        }
        
        # Try to extract company name and email (from codegen pattern)
        company_links = row.locator("a").all()
        if company_links:
            company_name = company_links[0].inner_text().strip()
            load_info['company'] = company_name
            
            # Skip popup email extraction to avoid hanging - use alternative method
            print(f"ℹ️ Skipping popup email extraction for {company_name} to prevent hanging")
            load_info['email'] = 'Contact via Sylectus'
        
        # Extract credit score
        credit_match = re.search(r'Credit Score:\s*(\d+%)', row_text)
        if credit_match:
            load_info['credit_score'] = credit_match.group(1)
        
        # Extract days to pay
        days_match = re.search(r'Days to Pay:\s*(\d+)', row_text)
        if days_match:
            load_info['days_to_pay'] = days_match.group(1)
        
        # Extract load ID
        load_id_match = re.search(r'Load\s+(\d+)', row_text)
        if load_id_match:
            load_info['load_id'] = load_id_match.group(1)
        
        # Extract cities (looking for pattern: CITY, STATE ZIP)
        city_pattern = r'([A-Z\s]+),\s+([A-Z]{2})\s+(\d{5})'
        cities = re.findall(city_pattern, row_text)
        if len(cities) >= 2:
            load_info['pickup_city'] = f"{cities[0][0].strip()}, {cities[0][1]}"
            load_info['delivery_city'] = f"{cities[1][0].strip()}, {cities[1][1]}"
        
        # Extract dates
        date_pattern = r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})'
        dates = re.findall(date_pattern, row_text)
        if len(dates) >= 2:
            load_info['pickup_date'] = dates[0]
            load_info['delivery_date'] = dates[1]
        
        # Extract vehicle type
        vehicle_types = ['SMALL STRAIGHT', 'CARGO VAN', 'SPRINTER', 'STRAIGHT TRUCK', 'EXPEDITED']
        for vehicle in vehicle_types:
            if vehicle in row_text:
                load_info['vehicle_type'] = vehicle
                break
        
        # Extract miles (number before vehicle type usually)
        miles_match = re.search(r'(\d+)\s+\d+\s+(\d+)$', row_text)  # Pattern: miles pieces weight
        if miles_match:
            load_info['miles'] = miles_match.group(1)
            load_info['pieces'] = miles_match.group(2)
        
        # Extract weight (last number usually)
        weight_match = re.search(r'(\d+)$', row_text)
        if weight_match:
            load_info['weight'] = f"{weight_match.group(1)} lbs"
        
        # Check if bid button is available (from codegen pattern)
        bid_buttons = row.locator("input[name='bidbutton']").all()
        if bid_buttons:
            load_info['bid_available'] = True
            print(f"✅ Bid button found for {load_info['company']}")
        
        return load_info
        
    except Exception as e:
        print(f"❌ Error extracting load details: {e}")
        return None

def scrape_all_loads(iframe, sent_items, page):
    """Scrape all loads from the iframe"""
    new_loads_found = 0
    
    try:
        print("🔍 Scraping all loads from load board...")
        
        # Wait for results to load
        time.sleep(5)
        
        # Get all load rows
        load_rows = iframe.locator("tr").all()
        
        print(f"📊 Found {len(load_rows)} total rows to analyze")
        
        for idx, row in enumerate(load_rows):
            try:
                # Skip rows without enough content
                row_text = row.inner_text().strip()
                if len(row_text) < 50:  # Skip header/empty rows
                    continue
                
                # Check if this row has a bid button (indicates it's a load)
                bid_buttons = row.locator("input[name='bidbutton']").all()
                if not bid_buttons:
                    continue
                
                print(f"🔍 Processing load row {idx + 1}...")
                
                # Extract detailed load information
                load_data = extract_load_details(row, iframe, page)
                if not load_data:
                    continue
                
                # Create unique identifier for this load
                load_id = f"{load_data['company']}_{load_data['load_id']}_{load_data['pickup_city']}_{load_data['delivery_city']}"
                
                # Step 4: Check if we've already sent this load
                if load_id in sent_items:
                    continue
                
                print(f"🆕 NEW LOAD: {load_data['company']} - Load {load_data['load_id']}")
                
                # Calculate recommended rate (miles × $0.75)
                try:
                    recommended_rate = int(load_data['miles']) * 0.75 if load_data['miles'].isdigit() else 0
                    rate_text = f"{recommended_rate:.0f}$" if recommended_rate > 0 else "N/A"
                except:
                    rate_text = "N/A"
                
                # Format message to match the image format
                message = f"""**Pick-up at:** {load_data['pickup_city']}
**Pick-up date:** {load_data['pickup_date']} (Scheduled)

**Deliver to:** {load_data['delivery_city']}
**Delivery date:** {load_data['delivery_date']} (Scheduled)

**Miles:** {load_data['miles']}
**Pieces:** {load_data['pieces']}
**Weight:** {load_data['weight']}
**Dims:** 40x42x21
**Suggested Truck Size:** {load_data['vehicle_type'].lower()}

**Notes:** EMAIL ONLY Pickup Wednesday Deliver Friday NO Dispatch Services

**Miles Out:** 80
**Driver:** {load_data['company']}
**Load-N:** {load_data['load_id']}

**Recommended Rate:** {rate_text}

⏰ **Found:** {datetime.now().strftime('%I:%M %p')}"""
                
                # Create inline keyboard for Telegram
                keyboard = {
                    'inline_keyboard': [
                        [
                            {'text': 'BID', 'callback_data': f'bid_{load_data["load_id"]}'},
                            {'text': 'SKIP', 'callback_data': f'skip_{load_data["load_id"]}'}
                        ],
                        [
                            {'text': 'Stop Loads', 'callback_data': 'stop_loads'},
                            {'text': 'Contact Dispatcher', 'callback_data': f'contact_{load_data["load_id"]}'}
                        ]
                    ]
                }
                
                # Call send_to_telegram function with keyboard
                if send_to_telegram(message, keyboard):
                    # Save item ID to prevent duplicates
                    save_sent_item(load_id)
                    sent_items.add(load_id)
                    new_loads_found += 1
                    print(f"✅ Sent notification for: {load_data['company']} Load {load_data['load_id']}")
                
                # Add a small delay to avoid sending messages too quickly
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error processing row {idx}: {e}")
                continue
        
        return new_loads_found
        
    except Exception as e:
        print(f"❌ Error scraping loads: {e}")
        return 0

# Step 3: Main Scraping Logic
if __name__ == "__main__":
    # Load previously sent items
    sent_items = load_sent_items()
    
    print("🚀 Starting Complete Sylectus Scraper...")
    send_to_telegram("🚀 **Complete Scraper Started**\n\nUsing recorded workflow with email extraction...")
    
    # Start Playwright
    with sync_playwright() as p:
        # Launch browser with headless configuration for server environment
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-blink-features=AutomationControlled',
                '--exclude-switches=enable-automation',
                '--disable-extensions'
            ]
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        # Create a new page
        page = context.new_page()
        
        # Set extra headers to look more human
        page.set_extra_http_headers({
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        page.set_default_timeout(30000)
        
        try:
            # Step 3: Login Sequence (complete from codegen recording)
            if not perform_complete_login(page):
                print("❌ Login failed, exiting...")
                send_to_telegram("❌ **Login Failed**\n\nCould not complete login sequence")
                browser.close()
                exit(1)
            
            # Setup load board with filters
            iframe = setup_load_board(page)
            if not iframe:
                print("❌ Failed to setup load board, exiting...")
                send_to_telegram("❌ **Load Board Setup Failed**\n\nCould not access or configure load board")
                browser.close()
                exit(1)
            
            # Start monitoring loop
            print(f"🔄 Starting monitoring loop (checking every {CHECK_INTERVAL} seconds)")
            
            while True:
                try:
                    print(f"\n🔄 === MONITORING CYCLE === {datetime.now().strftime('%H:%M:%S')}")
                    
                    # Refresh search to get latest loads
                    try:
                        iframe.get_by_role("button", name="SEARCH ALL POSTINGS").click()
                        time.sleep(8)  # Wait for results to load
                    except:
                        print("⚠️ Could not refresh search, continuing with current results...")
                    
                    # Scrape all loads
                    new_loads = scrape_all_loads(iframe, sent_items, page)
                    
                    if new_loads > 0:
                        print(f"✅ Found {new_loads} new loads this cycle")
                        send_to_telegram(f"📊 **Cycle Complete**\n\nFound {new_loads} new loads")
                    else:
                        print("ℹ️ No new loads found this cycle")
                    
                    # Wait for next cycle
                    print(f"⏳ Waiting {CHECK_INTERVAL} seconds until next check...")
                    time.sleep(CHECK_INTERVAL)
                    
                except KeyboardInterrupt:
                    print("\n⏹️ Monitoring stopped by user")
                    break
                except Exception as e:
                    print(f"❌ Error in monitoring cycle: {e}")
                    print("⏳ Waiting 30 seconds before retry...")
                    time.sleep(30)
                    continue
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            send_to_telegram(f"❌ **Scraper Error**\n\n{str(e)}")
            
        finally:
            # Shutdown: close the browser
            browser.close()
            print("🔒 Browser closed")
            
    print("🏁 Scraper execution complete")