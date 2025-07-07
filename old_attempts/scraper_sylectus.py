#!/usr/bin/env python3
"""
Automated Sylectus Scraper with Telegram Alerts
Following the detailed step-by-step plan exactly with actual Sylectus selectors
"""

# Step 3: Imports and Configuration
from playwright.sync_api import sync_playwright
import requests
import os
import time

# Load environment variables
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
        response = requests.post(url, data=data)
        
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

# Step 3: Main Scraping Logic
if __name__ == "__main__":
    # Load previously sent items
    sent_items = load_sent_items()
    
    # Start Playwright
    with sync_playwright() as p:
        # Launch a browser (headless=False to watch it work, change to True for production)
        browser = p.chromium.launch(headless=False)
        
        # Create a new page
        page = browser.new_page()
        
        try:
            # Step 3: Login Sequence
            print("🔐 Starting login process...")
            
            # Navigate to login page
            page.goto("https://www.sylectus.net/")
            
            # Wait for page to load
            page.wait_for_load_state('networkidle')
            
            # Fill in username - look for common login field patterns
            print("📝 Filling username...")
            try:
                # Try different possible username field selectors
                if page.locator('input[name="username"]').count() > 0:
                    page.fill('input[name="username"]', WEBSITE_USERNAME)
                elif page.locator('input[name="user"]').count() > 0:
                    page.fill('input[name="user"]', WEBSITE_USERNAME)
                elif page.locator('input[name="email"]').count() > 0:
                    page.fill('input[name="email"]', WEBSITE_USERNAME)
                elif page.locator('input[type="text"]').count() > 0:
                    page.fill('input[type="text"]', WEBSITE_USERNAME)
                else:
                    print("❌ Could not find username field")
            except Exception as e:
                print(f"❌ Error filling username: {e}")
            
            # Fill in password
            print("📝 Filling password...")
            try:
                page.fill('input[type="password"]', WEBSITE_PASSWORD)
            except Exception as e:
                print(f"❌ Error filling password: {e}")
            
            # Click login button
            print("🔑 Clicking login button...")
            try:
                # Try different possible login button selectors
                if page.locator('button[type="submit"]').count() > 0:
                    page.click('button[type="submit"]')
                elif page.locator('input[type="submit"]').count() > 0:
                    page.click('input[type="submit"]')
                elif page.locator('button:has-text("Login")').count() > 0:
                    page.click('button:has-text("Login")')
                elif page.locator('button:has-text("Sign In")').count() > 0:
                    page.click('button:has-text("Sign In")')
                else:
                    print("❌ Could not find login button")
            except Exception as e:
                print(f"❌ Error clicking login button: {e}")
            
            # Wait for login to complete - ensure the login was successful and the next page has loaded
            print("⏳ Waiting for login to complete...")
            time.sleep(5)  # Give time for login to process
            
            # Check if we're logged in (look for common indicators)
            current_url = page.url
            if 'login' not in current_url.lower():
                print("✅ Login appears successful!")
            else:
                print("⚠️  Still on login page, continuing anyway...")
            
            # Step 3: Scraping Sequence
            print("🔍 Navigating to listings page...")
            
            # Navigate to the page with the listings (use the actual Sylectus URL from your config)
            sylectus_url = "https://www.sylectus.net/Main.aspx?page=II14_managepostedloads.asp?loadboard=True"
            page.goto(sylectus_url)
            
            # Wait for page to load
            page.wait_for_load_state('networkidle')
            
            # Get all item listings - look for table rows which is common for Sylectus
            print("📋 Getting all listings...")
            
            # Try different selectors for load listings
            listings = []
            
            # First try table rows
            if page.locator('table tr').count() > 0:
                listings = page.locator('table tr').all()
                print(f"📊 Found {len(listings)} table rows")
            
            # If no table rows, try other common selectors
            if not listings:
                if page.locator('[class*="item"]').count() > 0:
                    listings = page.locator('[class*="item"]').all()
                    print(f"📊 Found {len(listings)} items")
                elif page.locator('[class*="load"]').count() > 0:
                    listings = page.locator('[class*="load"]').all()
                    print(f"📊 Found {len(listings)} loads")
            
            if not listings:
                print("❌ No listings found. Page may have changed or login failed.")
                return
            
            # Loop through each listing
            new_items_count = 0
            for i, listing in enumerate(listings):
                try:
                    # Skip header rows and empty rows
                    listing_text = listing.inner_text().strip()
                    if len(listing_text) < 10 or 'pick-up' in listing_text.lower():
                        continue
                    
                    print(f"🔍 Processing listing {i+1}...")
                    
                    # Extract data from the listing (adapt based on Sylectus structure)
                    try:
                        # Get all cell texts for this row
                        cells = listing.locator('td').all()
                        cell_texts = [cell.inner_text().strip() for cell in cells]
                        
                        if len(cell_texts) < 3:
                            continue
                        
                        # Extract basic info (adapt these based on actual Sylectus table structure)
                        company = cell_texts[0] if cell_texts else "Unknown Company"
                        
                        # Look for pickup location (common patterns)
                        pickup = "Unknown"
                        delivery = "Unknown"
                        
                        for text in cell_texts:
                            if ', ' in text and len(text.split(', ')) == 2:
                                parts = text.split(', ')
                                if len(parts[1]) == 2:  # State abbreviation
                                    if pickup == "Unknown":
                                        pickup = text
                                    else:
                                        delivery = text
                                        break
                        
                        # Create a formatted title
                        title = f"{company} - {pickup} to {delivery}"
                        
                        # Try to get link if available
                        link_element = listing.locator('a').first
                        link = ""
                        if link_element.count() > 0:
                            href = link_element.get_attribute('href')
                            if href:
                                link = f"https://www.sylectus.net{href}" if href.startswith('/') else href
                        
                        # Create unique identifier for this item
                        item_id = f"{company}_{pickup}_{delivery}_{i}"
                        
                        # Step 4: Check if item already sent
                        if item_id in sent_items:
                            continue
                        
                        # Format a message string
                        message = f"""🆕 **NEW SYLECTUS LOAD**

🏢 **Company:** {company}
📍 **Pickup:** {pickup}
📍 **Delivery:** {delivery}
🔗 **Link:** {link if link else "Not available"}

📊 **Raw Data:** {' | '.join(cell_texts[:5])}

⏰ **Found:** {time.strftime('%I:%M %p')}"""
                        
                        # Call send_to_telegram function
                        if send_to_telegram(message):
                            # Save item ID to prevent duplicates
                            save_sent_item(item_id)
                            sent_items.add(item_id)
                            new_items_count += 1
                            print(f"✅ Sent notification for: {title[:50]}...")
                        
                        # Add a small delay to avoid sending messages too quickly
                        time.sleep(1)
                        
                    except Exception as e:
                        print(f"❌ Error extracting data from listing {i+1}: {e}")
                        continue
                    
                except Exception as e:
                    print(f"❌ Error processing listing {i+1}: {e}")
                    continue
            
            print(f"✅ Scraping completed! Sent {new_items_count} new notifications.")
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            
        finally:
            # Shutdown: close the browser
            browser.close()
            print("🔒 Browser closed")