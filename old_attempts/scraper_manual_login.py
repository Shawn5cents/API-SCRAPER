#!/usr/bin/env python3
"""
Manual Login Scraper - Bypass CloudFlare with Human Help
Following the exact plan structure with manual login assistance
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

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))  # 5 minutes default

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

def extract_load_data(cell_texts):
    """Extract load data from table cells"""
    try:
        company = cell_texts[0] if cell_texts else "Unknown Company"
        
        # Extract locations (look for city, state patterns)
        pickup = "Unknown"
        delivery = "Unknown"
        
        for text in cell_texts:
            match = re.search(r'([A-Z\s]+),?\s+([A-Z]{2})\b', text)
            if match:
                location = f"{match.group(1).strip()}, {match.group(2)}"
                if pickup == "Unknown":
                    pickup = location
                elif delivery == "Unknown":
                    delivery = location
                    break
        
        # Extract miles
        miles = "N/A"
        for text in cell_texts:
            match = re.search(r'(\d+)\s*(?:miles?|mi\.?)', text, re.IGNORECASE)
            if match:
                miles = match.group(1)
                break
        
        # Extract weight
        weight = "N/A"
        for text in cell_texts:
            match = re.search(r'(\d+(?:,\d+)?)\s*(?:lbs?|pounds?)', text, re.IGNORECASE)
            if match:
                weight = f"{match.group(1)} lbs"
                break
        
        return {
            'company': company,
            'pickup': pickup,
            'delivery': delivery,
            'miles': miles,
            'weight': weight,
            'raw_data': ' | '.join(cell_texts[:5])
        }
    except Exception as e:
        print(f"❌ Error extracting load data: {e}")
        return None

def is_load_row(first_cell, all_cells):
    """Check if this row contains load data"""
    if not first_cell or len(first_cell) < 3:
        return False
    
    # Skip headers
    skip_keywords = ['pick-up', 'ref.', 'load type', 'posted by', 'freight', 'audible', 'notes']
    if any(keyword in first_cell.lower() for keyword in skip_keywords):
        return False
    
    # Look for company indicators
    company_indicators = ['LLC', 'INC', 'LOGISTICS', 'TRANSPORT', 'EXPEDITE', 'FREIGHT']
    if any(indicator in first_cell.upper() for indicator in company_indicators):
        return True
    
    # Look for company patterns in any cell
    for cell in all_cells[:3]:
        if any(indicator in cell.upper() for indicator in company_indicators):
            return True
    
    return False

def wait_for_manual_login(page):
    """Wait for user to manually complete login and navigation"""
    print("\n" + "="*60)
    print("🔐 MANUAL LOGIN REQUIRED")
    print("="*60)
    print("👤 Please complete the following steps in the browser window:")
    print("   1. Complete any CloudFlare verification")
    print("   2. Login with your credentials")
    print("   3. Navigate to the load board page")
    print("   4. When you see the loads/items, press ENTER here")
    print("="*60)
    
    # Wait for user confirmation
    input("✋ Press ENTER when you're logged in and on the load board page...")
    
    print("✅ Continuing with automated scraping...")
    return True

def scrape_loads_from_page(page, sent_items):
    """Scrape loads from the current page"""
    new_loads_found = 0
    
    try:
        print("🔍 Analyzing page for load data...")
        
        # Take screenshot for debugging
        try:
            page.screenshot(path=f'scraper_screenshot_{int(time.time())}.png')
        except:
            pass
        
        # Get all tables (most common structure for Sylectus)
        tables = page.locator('table').all()
        print(f"📊 Found {len(tables)} tables")
        
        # Process each table
        for table_idx, table in enumerate(tables):
            try:
                rows = table.locator('tr').all()
                
                if len(rows) < 3:  # Skip small tables
                    continue
                
                print(f"📋 Processing table {table_idx + 1} with {len(rows)} rows")
                
                # Process each row
                for row_idx, row in enumerate(rows):
                    try:
                        # Get all cells in this row
                        cells = row.locator('td, th').all()
                        if len(cells) < 3:
                            continue
                        
                        # Extract cell texts
                        cell_texts = []
                        for cell in cells:
                            try:
                                text = cell.inner_text().strip()
                                cell_texts.append(text)
                            except:
                                cell_texts.append("")
                        
                        # Check if this looks like a load row
                        first_cell = cell_texts[0] if cell_texts else ""
                        
                        if not is_load_row(first_cell, cell_texts):
                            continue
                        
                        print(f"🔍 Processing load row: {first_cell[:30]}...")
                        
                        # Extract load data
                        load_data = extract_load_data(cell_texts)
                        if not load_data:
                            continue
                        
                        # Create unique identifier for this load
                        load_id = f"{load_data['company']}_{load_data['pickup']}_{load_data['delivery']}_{table_idx}_{row_idx}"
                        
                        # Check if we've already sent this load
                        if load_id in sent_items:
                            continue
                        
                        # Try to find link in this row
                        link = "No link available"
                        try:
                            link_element = row.locator('a').first
                            if link_element.count() > 0:
                                href = link_element.get_attribute('href')
                                if href:
                                    link = f"https://www.sylectus.net{href}" if href.startswith('/') else href
                        except:
                            pass
                        
                        print(f"🆕 NEW LOAD: {load_data['company']} - {load_data['pickup']} to {load_data['delivery']}")
                        
                        # Format a message string
                        message = f"""🆕 **NEW SYLECTUS LOAD**

🏢 **Company:** {load_data['company']}

📍 **PICKUP:** {load_data['pickup']}
📍 **DELIVERY:** {load_data['delivery']}

📏 **Miles:** {load_data['miles']}
⚖️ **Weight:** {load_data['weight']}

🔗 **Link:** {link}

📊 **Raw Data:** {load_data['raw_data']}

⏰ **Found:** {datetime.now().strftime('%I:%M %p')}

🌐 *Via Manual Login Scraper*"""
                        
                        # Call send_to_telegram function
                        if send_to_telegram(message):
                            # Save item ID to prevent duplicates
                            save_sent_item(load_id)
                            sent_items.add(load_id)
                            new_loads_found += 1
                            print(f"✅ Sent notification for: {load_data['company']}")
                        
                        # Add a small delay to avoid sending messages too quickly
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"❌ Error processing row {row_idx + 1}: {e}")
                        continue
            
            except Exception as e:
                print(f"❌ Error processing table {table_idx + 1}: {e}")
                continue
        
        return new_loads_found
        
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        return 0

# Step 3: Main Scraping Logic
if __name__ == "__main__":
    # Load previously sent items
    sent_items = load_sent_items()
    
    print("🚀 Starting Manual Login Scraper...")
    send_to_telegram("🚀 **Manual Login Scraper Started**\n\nWaiting for manual login to complete...")
    
    # Start Playwright
    with sync_playwright() as p:
        # Launch a browser (visible so user can login)
        browser = p.chromium.launch(
            headless=False,  # Must be False for manual login
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        )
        
        # Create a new context
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        # Create a new page
        page = context.new_page()
        page.set_default_timeout(30000)
        
        try:
            # Navigate to Sylectus homepage
            print("🌐 Navigating to Sylectus...")
            page.goto("https://www.sylectus.net/", wait_until='domcontentloaded')
            
            # Wait for manual login
            wait_for_manual_login(page)
            
            # Start monitoring loop
            print(f"🔄 Starting monitoring loop (checking every {CHECK_INTERVAL} seconds)")
            first_run = True
            
            while True:
                try:
                    cycle_start = time.time()
                    
                    if first_run:
                        print("\n🔄 === FIRST RUN - GETTING CURRENT LOADS ===")
                        first_run = False
                    else:
                        print(f"\n🔄 === MONITORING CYCLE === {datetime.now().strftime('%H:%M:%S')}")
                    
                    # Refresh the page to get latest data
                    try:
                        page.reload(wait_until='domcontentloaded', timeout=20000)
                        time.sleep(2)  # Wait for dynamic content
                    except:
                        print("⚠️  Page refresh failed, continuing with current page...")
                    
                    # Scrape loads from current page
                    new_loads = scrape_loads_from_page(page, sent_items)
                    
                    if new_loads > 0:
                        print(f"✅ Found {new_loads} new loads this cycle")
                    else:
                        print("ℹ️  No new loads found this cycle")
                    
                    # Calculate time for this cycle
                    cycle_time = time.time() - cycle_start
                    remaining_time = max(0, CHECK_INTERVAL - cycle_time)
                    
                    if remaining_time > 0:
                        print(f"⏳ Waiting {remaining_time:.0f} seconds until next check...")
                        time.sleep(remaining_time)
                    
                except KeyboardInterrupt:
                    print("\n⏹️  Monitoring stopped by user")
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
            # Don't close browser automatically - user might want to keep session
            print("\n🔒 Script finished. Browser will stay open to maintain session.")
            print("   You can manually close the browser when done.")
            
            # Send completion message
            send_to_telegram("⏹️ **Manual Login Scraper Stopped**\n\nMonitoring session ended.")
            
            # Wait for user input before closing
            try:
                input("Press ENTER to close browser and exit...")
                browser.close()
            except KeyboardInterrupt:
                browser.close()
            
    print("🏁 Scraper execution complete")