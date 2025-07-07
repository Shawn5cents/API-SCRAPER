#!/usr/bin/env python3
"""
Automated Website Scraper with Telegram Alerts
Following the detailed step-by-step plan exactly
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
            'text': message_text
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
            
            # Fill in username (adapt these selectors based on Codegen results)
            print("📝 Filling username...")
            page.fill('input[name="username"]', WEBSITE_USERNAME)
            
            # Fill in password
            print("📝 Filling password...")
            page.fill('input[name="password"]', WEBSITE_PASSWORD)
            
            # Click login button
            print("🔑 Clicking login button...")
            page.click('button[type="submit"]')
            
            # Wait for login to complete - ensure the login was successful and the next page has loaded
            page.wait_for_url("**/main*", timeout=30000)
            print("✅ Login successful!")
            
            # Step 3: Scraping Sequence
            print("🔍 Navigating to listings page...")
            
            # Navigate to the page with the listings
            page.goto("https://www.sylectus.net/items")  # Replace with actual listings URL
            
            # Wait for page to load
            page.wait_for_load_state('networkidle')
            
            # Get all item listings into a list using the item container selector from Codegen
            print("📋 Getting all listings...")
            listings = page.locator(".selector-for-one-item-block").all()  # Replace with actual selector
            
            print(f"📊 Found {len(listings)} listings")
            
            # Loop through each listing
            for i, listing in enumerate(listings):
                try:
                    print(f"🔍 Processing listing {i+1}...")
                    
                    # Find the individual data points relative to the current listing
                    title = listing.locator(".selector-for-the-title").inner_text()  # Replace with actual selector
                    price = listing.locator(".selector-for-the-price").inner_text()  # Replace with actual selector
                    link = listing.locator("a").get_attribute("href")
                    
                    # Create unique identifier for this item
                    item_id = f"{title}_{link}"
                    
                    # Step 4: Check if item already sent
                    if item_id in sent_items:
                        print(f"⏭️  Skipping already sent item: {title[:50]}...")
                        continue
                    
                    # Format a message string
                    message = f"New Item: {title}\nPrice: {price}\nLink: https://www.sylectus.net{link}"
                    
                    # Call send_to_telegram function
                    if send_to_telegram(message):
                        # Save item ID to prevent duplicates
                        save_sent_item(item_id)
                        sent_items.add(item_id)
                        print(f"✅ Sent notification for: {title[:50]}...")
                    
                    # Add a small delay to avoid sending messages too quickly
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Error processing listing {i+1}: {e}")
                    continue
            
            print("✅ Scraping completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during scraping: {e}")
            
        finally:
            # Shutdown: close the browser
            browser.close()
            print("🔒 Browser closed")