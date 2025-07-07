#!/usr/bin/env python3
"""
Robust Sylectus Scraper - Production Ready
Following the exact plan structure with improved error handling and timeout management
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
    
    # Send startup message
    send_to_telegram("🚀 **Playwright Scraper Started**\\n\\nStarting Sylectus load monitoring...")
    
    # Start Playwright
    with sync_playwright() as p:
        # Launch a browser (headless=False to watch it work, change to True for production)
        browser = p.chromium.launch(
            headless=True,  # Set to False for debugging
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security'
            ]
        )
        
        # Create a new context with realistic settings
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        # Create a new page
        page = context.new_page()
        page.set_default_timeout(15000)  # Reduced timeout
        
        try:
            print("🔍 Starting Sylectus scraper...")
            
            # Try multiple approaches to get to the load board
            load_board_urls = [
                "https://www.sylectus.net/Main.aspx?page=II14_managepostedloads.asp?loadboard=True",
                "https://www.sylectus.net/loadboard",
                "https://www.sylectus.net/loads"
            ]
            
            page_loaded = False
            
            for url in load_board_urls:
                try:
                    print(f"🌐 Trying URL: {url}")
                    
                    # Navigate to the page
                    page.goto(url, wait_until='domcontentloaded', timeout=20000)
                    
                    # Wait a bit for dynamic content
                    time.sleep(3)
                    
                    # Check if we got a useful page
                    page_content = page.content()
                    
                    if len(page_content) > 1000:  # Page has substantial content
                        print("✅ Page loaded successfully")
                        page_loaded = True
                        break
                    else:
                        print(f"❌ Page seems empty or blocked, trying next URL...")
                        
                except Exception as e:
                    print(f"❌ Error loading {url}: {e}")
                    continue
            
            if not page_loaded:
                print("❌ Could not load any load board URLs")
                send_to_telegram("❌ **Scraper Error**\\n\\nCould not access Sylectus load board")
                return
            
            # Step 3: Scraping Sequence
            print("🔍 Starting load scraping...")
            
            # Take a screenshot for debugging
            try:
                page.screenshot(path='debug_screenshot.png')
                print("📸 Screenshot saved as debug_screenshot.png")
            except:
                pass
            
            # Try different strategies to find load data
            strategies = [
                ('table tr', 'Table rows'),
                ('[class*="load"]', 'Load class elements'),
                ('[class*="row"]', 'Row class elements'),
                ('tr', 'All table rows'),
                ('div', 'All divs')
            ]
            
            loads_found = 0
            
            for selector, description in strategies:
                try:
                    print(f"🔍 Trying strategy: {description} ({selector})")
                    
                    elements = page.locator(selector).all()
                    print(f"   Found {len(elements)} elements")
                    
                    if len(elements) == 0:
                        continue
                    
                    # Process elements
                    for idx, element in enumerate(elements):
                        try:
                            # Get text content
                            text = element.inner_text().strip()
                            
                            # Skip empty or very short elements
                            if len(text) < 20:
                                continue
                            
                            # Check if this looks like load data
                            text_lower = text.lower()
                            load_indicators = ['pickup', 'delivery', 'load', 'freight', 'transport', 'logistics']
                            
                            if not any(indicator in text_lower for indicator in load_indicators):
                                continue
                            
                            # Split text into parts (simulate table cells)
                            parts = text.split('\n')
                            if len(parts) < 2:
                                parts = text.split('\t')
                            if len(parts) < 2:
                                parts = re.split(r'\s{2,}', text)  # Split on multiple spaces
                            
                            # Try to extract load data
                            load_data = extract_load_data(parts)
                            if not load_data:
                                continue
                            
                            # Create unique identifier
                            load_id = f"{load_data['company']}_{load_data['pickup']}_{load_data['delivery']}_{idx}"
                            
                            # Check if already sent
                            if load_id in sent_items:
                                continue
                            
                            print(f"🆕 Found new load: {load_data['company']}")
                            
                            # Format message
                            message = f"""🆕 **NEW SYLECTUS LOAD**

🏢 **Company:** {load_data['company']}

📍 **PICKUP:** {load_data['pickup']}
📍 **DELIVERY:** {load_data['delivery']}

📏 **Miles:** {load_data['miles']}
⚖️ **Weight:** {load_data['weight']}

📊 **Raw Data:** {load_data['raw_data']}

⏰ **Found:** {datetime.now().strftime('%I:%M %p')}

🌐 *Via Playwright Scraper*"""
                            
                            # Send to Telegram
                            if send_to_telegram(message):
                                save_sent_item(load_id)
                                sent_items.add(load_id)
                                loads_found += 1
                                
                                # Rate limiting
                                time.sleep(1)
                            
                            # Limit to prevent spam
                            if loads_found >= 10:
                                print("⚠️  Reached load limit (10) for this run")
                                break
                        
                        except Exception as e:
                            print(f"❌ Error processing element {idx}: {e}")
                            continue
                    
                    # If we found loads with this strategy, we're done
                    if loads_found > 0:
                        print(f"✅ Found {loads_found} loads using {description}")
                        break
                        
                except Exception as e:
                    print(f"❌ Error with strategy {description}: {e}")
                    continue
            
            if loads_found == 0:
                print("ℹ️  No new loads found with any strategy")
                
                # Save page content for debugging
                try:
                    with open('debug_page.html', 'w') as f:
                        f.write(page.content())
                    print("💾 Page content saved to debug_page.html")
                except:
                    pass
                
                # Send status update
                send_to_telegram("ℹ️ **Scraper Status**\\n\\nNo new loads found. Monitoring continues...")
            else:
                print(f"✅ Scraping completed! Found {loads_found} new loads")
                
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            send_to_telegram(f"❌ **Scraper Error**\\n\\n{str(e)}")
            
            # Save error info
            import traceback
            with open('error_log.txt', 'a') as f:
                f.write(f"\\n{datetime.now()}: {traceback.format_exc()}\\n")
            
        finally:
            # Shutdown: close the browser
            browser.close()
            print("🔒 Browser closed")
            
    print("🏁 Scraper execution complete")