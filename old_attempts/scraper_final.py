#!/usr/bin/env python3
"""
Final Sylectus Scraper following the exact plan structure
Based on working simple_scraper.py patterns and Playwright implementation
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

WEBSITE_USERNAME = os.getenv('WEBSITE_USERNAME')
WEBSITE_PASSWORD = os.getenv('WEBSITE_PASSWORD') 
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

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
    """Extract load data from table cells (adapted from simple_scraper.py)"""
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
        
        # Extract other data
        miles = "N/A"
        for text in cell_texts:
            match = re.search(r'(\d+)\s*(?:miles?|mi\.?)', text, re.IGNORECASE)
            if match:
                miles = match.group(1)
                break
        
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
    """Check if this row contains load data (from simple_scraper.py)"""
    if not first_cell or len(first_cell) < 3:
        return False
    
    # Skip headers
    skip_keywords = ['pick-up', 'ref.', 'load type', 'posted by', 'freight']
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

# Step 3: Main Scraping Logic
if __name__ == "__main__":
    # Load previously sent items
    sent_items = load_sent_items()
    
    # Start Playwright
    with sync_playwright() as p:
        # Launch a browser (headless=False to watch it work, change to True for production)
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        
        # Create a new context with realistic settings
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        # Create a new page
        page = context.new_page()
        page.set_default_timeout(30000)
        
        try:
            print("🔍 Starting Sylectus scraper...")
            
            # Step 3: Login Sequence (if needed)
            print("🔐 Checking if login is required...")
            
            # Navigate directly to the load board page (based on your working config)
            sylectus_url = "https://www.sylectus.net/Main.aspx?page=II14_managepostedloads.asp?loadboard=True"
            print(f"🌐 Navigating to: {sylectus_url}")
            
            page.goto(sylectus_url, wait_until='domcontentloaded')
            
            # Wait for page to load
            time.sleep(5)
            
            # Check if we need to login
            page_content = page.content().lower()
            current_url = page.url
            
            if 'login' in page_content or 'sign in' in page_content or 'login' in current_url:
                print("🔐 Login required, attempting to login...")
                
                # Try to find and fill login form
                try:
                    # Look for username field
                    username_selectors = [
                        'input[name="username"]',
                        'input[name="user"]',
                        'input[name="email"]',
                        'input[type="text"]'
                    ]
                    
                    username_filled = False
                    for selector in username_selectors:
                        try:
                            if page.locator(selector).count() > 0:
                                page.fill(selector, WEBSITE_USERNAME)
                                print(f"✅ Username filled using: {selector}")
                                username_filled = True
                                break
                        except:
                            continue
                    
                    # Fill password
                    if username_filled and page.locator('input[type="password"]').count() > 0:
                        page.fill('input[type="password"]', WEBSITE_PASSWORD)
                        print("✅ Password filled")
                        
                        # Click login button
                        login_selectors = [
                            'button[type="submit"]',
                            'input[type="submit"]',
                            'button:has-text("Login")',
                            'button:has-text("Sign In")'
                        ]
                        
                        for selector in login_selectors:
                            try:
                                if page.locator(selector).count() > 0:
                                    page.click(selector)
                                    print(f"✅ Login button clicked: {selector}")
                                    break
                            except:
                                continue
                        
                        # Wait for login to complete
                        print("⏳ Waiting for login...")
                        time.sleep(5)
                        
                        # Navigate to load board after login
                        page.goto(sylectus_url, wait_until='domcontentloaded')
                        time.sleep(3)
                
                except Exception as e:
                    print(f"❌ Login error: {e}")
                    print("   Continuing without login...")
            
            # Step 3: Scraping Sequence
            print("🔍 Starting load scraping...")
            
            # Wait for the page to load
            page.wait_for_load_state('networkidle', timeout=30000)
            
            # Get all table rows (based on simple_scraper.py pattern)
            print("📋 Looking for load data tables...")
            
            # Find tables
            tables = page.locator('table').all()
            print(f"📊 Found {len(tables)} tables")
            
            new_loads_found = 0
            
            # Loop through tables
            for table_idx, table in enumerate(tables):
                try:
                    rows = table.locator('tr').all()
                    
                    if len(rows) < 5:  # Skip small tables
                        continue
                    
                    print(f"📋 Checking table {table_idx + 1} with {len(rows)} rows")
                    
                    # Loop through each row (listing)
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
                            
                            print(f"🔍 Processing potential load row {row_idx + 1}...")
                            
                            # Extract load data
                            load_data = extract_load_data(cell_texts)
                            if not load_data:
                                continue
                            
                            # Create unique identifier for this load
                            load_id = f"{load_data['company']}_{load_data['pickup']}_{load_data['delivery']}_{table_idx}_{row_idx}"
                            
                            # Step 4: Check if we've already sent this load
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

🌐 *Via Playwright Scraper*"""
                            
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
            
            print(f"✅ Scraping completed! Found {new_loads_found} new loads")
            
            if new_loads_found == 0:
                print("ℹ️  No new loads found. All current loads may have been sent previously.")
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            # Shutdown: close the browser
            browser.close()
            print("🔒 Browser closed")
            
    print("🏁 Scraper execution complete")