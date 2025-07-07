#!/usr/bin/env python3
"""
Sylectus Scraper Built from Codegen Recording
Following the exact plan structure with recorded selectors
"""

# Step 3: Imports and Configuration
from playwright.sync_api import sync_playwright
import requests
import os
import time
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Credentials from codegen recording
CORPORATE_ID = "2103390"
CORPORATE_PASSWORD = "Sn59042181#@"
USERNAME = "SNICHOLS"
USER_PASSWORD = "Sn59042181#@"

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))

# Step 3: Function to Send Telegram Message
def send_to_telegram(message_text):
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

def perform_login(page):
    """Perform login sequence exactly as recorded in codegen"""
    try:
        print("🔐 Starting login sequence...")
        
        # Navigate to main page
        page.goto("https://www.sylectus.net/")
        
        # Handle cookie consent popup if it appears
        try:
            # Wait a moment for popup to appear
            time.sleep(2)
            
            # Try common cookie consent selectors
            consent_selectors = [
                'button:has-text("Accept")',
                'button:has-text("Accept All")',
                'button:has-text("OK")',
                'button:has-text("I Accept")',
                '[id*="accept"]',
                '[class*="accept"]',
                '#onetrust-accept-btn-handler',
                '.onetrust-close-btn-handler'
            ]
            
            for selector in consent_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.locator(selector).click()
                        print("✅ Cookie consent handled")
                        time.sleep(1)
                        break
                except:
                    continue
                    
        except:
            print("ℹ️ No cookie consent popup found")
        
        # Click LOG IN link
        page.get_by_role("link", name="LOG IN").click()
        
        # Fill Corporate ID
        page.get_by_role("textbox", name="Corporate ID").click()
        page.get_by_role("textbox", name="Corporate ID").fill(CORPORATE_ID)
        page.get_by_role("textbox", name="Corporate ID").press("Tab")
        
        # Fill Corporate Password
        page.locator("#ctl00_bodyPlaceholder_corpPasswordField").fill(CORPORATE_PASSWORD)
        
        # Click Continue
        page.get_by_role("link", name="Continue").click()
        
        # Select user dropdown
        page.get_by_label("").click()
        page.get_by_role("option", name=USERNAME).click()
        
        # Fill user password
        page.get_by_placeholder(" ").click()
        page.get_by_placeholder(" ").fill(USER_PASSWORD)
        
        # Click Log in
        page.get_by_role("link", name="Log in").click()
        
        print("✅ Login sequence completed")
        return True
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

def navigate_to_load_board(page):
    """Navigate to load board as recorded"""
    try:
        print("🚚 Navigating to Load Board...")
        
        # Click Load Board link
        page.get_by_role("link", name="Load Board").click()
        
        # Wait for iframe to load
        time.sleep(3)
        
        # Work within the iframe
        iframe = page.locator("#iframe1").content_frame
        
        # Set date (click on 7th)
        iframe.locator("#todate").click()
        iframe.get_by_text("7", exact=True).first.click()
        
        # Click SEARCH ALL POSTINGS
        iframe.get_by_role("button", name="SEARCH ALL POSTINGS").click()
        
        print("✅ Load board loaded")
        return iframe
        
    except Exception as e:
        print(f"❌ Navigation failed: {e}")
        return None

def scrape_loads_from_iframe(iframe, sent_items):
    """Scrape loads from the iframe content"""
    new_loads_found = 0
    
    try:
        print("🔍 Scraping loads from load board...")
        
        # Wait for results to load
        time.sleep(5)
        
        # Get all rows with load data
        # Based on the codegen, loads appear as rows with company names as links
        load_rows = iframe.locator("tr").all()
        
        print(f"📊 Found {len(load_rows)} rows to check")
        
        for idx, row in enumerate(load_rows):
            try:
                # Get all text content from the row
                row_text = row.inner_text().strip()
                
                if len(row_text) < 10:  # Skip empty rows
                    continue
                
                # Look for company name links (main indicator of load rows)
                company_links = row.locator("a").all()
                
                if not company_links:
                    continue
                
                # Extract company name from first link
                company_name = company_links[0].inner_text().strip()
                
                if len(company_name) < 3:
                    continue
                
                print(f"🔍 Processing load from: {company_name}")
                
                # Get all cell data
                cells = row.locator("td").all()
                cell_texts = []
                
                for cell in cells:
                    try:
                        text = cell.inner_text().strip()
                        cell_texts.append(text)
                    except:
                        cell_texts.append("")
                
                # Extract load information
                load_data = {
                    'company': company_name,
                    'pickup': extract_location(cell_texts, 'pickup'),
                    'delivery': extract_location(cell_texts, 'delivery'),
                    'date': extract_date(cell_texts),
                    'miles': extract_miles(cell_texts),
                    'weight': extract_weight(cell_texts),
                    'raw_data': ' | '.join(cell_texts[:6])
                }
                
                # Create unique ID
                load_id = f"{company_name}_{load_data['pickup']}_{load_data['delivery']}_{idx}"
                
                # Check if already sent
                if load_id in sent_items:
                    continue
                
                # Get bid button link if available
                bid_button = row.locator("input[name='bidbutton']")
                bid_link = "Available via bid button"
                
                print(f"🆕 NEW LOAD: {company_name}")
                
                # Format a message string
                message = f"""🆕 **NEW SYLECTUS LOAD**

🏢 **Company:** {load_data['company']}

📍 **PICKUP:** {load_data['pickup']}
📍 **DELIVERY:** {load_data['delivery']}

📅 **Date:** {load_data['date']}
📏 **Miles:** {load_data['miles']}
⚖️ **Weight:** {load_data['weight']}

🎯 **Action:** {bid_link}

📊 **Raw Data:** {load_data['raw_data']}

⏰ **Found:** {datetime.now().strftime('%I:%M %p')}

🌐 *Via Codegen Scraper*"""
                
                # Call send_to_telegram function
                if send_to_telegram(message):
                    # Save item ID to prevent duplicates
                    save_sent_item(load_id)
                    sent_items.add(load_id)
                    new_loads_found += 1
                    print(f"✅ Sent notification for: {company_name}")
                
                # Add a small delay to avoid sending messages too quickly
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error processing row {idx}: {e}")
                continue
        
        return new_loads_found
        
    except Exception as e:
        print(f"❌ Error scraping loads: {e}")
        return 0

def extract_location(cell_texts, location_type):
    """Extract pickup or delivery location"""
    for text in cell_texts:
        # Look for city, state patterns
        match = re.search(r'([A-Z\s]+),?\s+([A-Z]{2})\b', text)
        if match:
            return f"{match.group(1).strip()}, {match.group(2)}"
    return "Location TBD"

def extract_date(cell_texts):
    """Extract date information"""
    for text in cell_texts:
        date_match = re.search(r'(\d{1,2}\/\d{1,2}\/\d{2,4})', text)
        if date_match:
            return date_match.group(1)
    return "Date TBD"

def extract_miles(cell_texts):
    """Extract miles"""
    for text in cell_texts:
        match = re.search(r'(\d+)\s*(?:miles?|mi\.?)', text, re.IGNORECASE)
        if match:
            return f"{match.group(1)} miles"
    return "Miles TBD"

def extract_weight(cell_texts):
    """Extract weight"""
    for text in cell_texts:
        match = re.search(r'(\d+(?:,\d+)?)\s*(?:lbs?|pounds?)', text, re.IGNORECASE)
        if match:
            return f"{match.group(1)} lbs"
    return "Weight TBD"

# Step 3: Main Scraping Logic
if __name__ == "__main__":
    # Load previously sent items
    sent_items = load_sent_items()
    
    print("🚀 Starting Codegen-Based Scraper...")
    send_to_telegram("🚀 **Codegen Scraper Started**\n\nUsing recorded login sequence...")
    
    # Start Playwright
    with sync_playwright() as p:
        # Launch a browser (headless=False to watch it work, change to True for production)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        
        # Create a new page
        page = context.new_page()
        page.set_default_timeout(30000)
        
        try:
            # Step 3: Login Sequence (from codegen recording)
            if not perform_login(page):
                print("❌ Login failed, exiting...")
                send_to_telegram("❌ **Login Failed**\n\nCould not complete login sequence")
                browser.close()
                exit(1)
            
            # Navigate to load board
            iframe = navigate_to_load_board(page)
            if not iframe:
                print("❌ Failed to access load board, exiting...")
                send_to_telegram("❌ **Navigation Failed**\n\nCould not access load board")
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
                        time.sleep(5)  # Wait for results
                    except:
                        print("⚠️ Could not refresh search, continuing with current results...")
                    
                    # Scrape loads
                    new_loads = scrape_loads_from_iframe(iframe, sent_items)
                    
                    if new_loads > 0:
                        print(f"✅ Found {new_loads} new loads this cycle")
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