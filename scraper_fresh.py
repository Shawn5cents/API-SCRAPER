#!/usr/bin/env python3
"""
Fresh Sylectus Scraper - Based on new codegen recording
"""

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

# Credentials from codegen
CORPORATE_ID = "2103390"
CORPORATE_PASSWORD = "Sn59042181#@"
USER_PASSWORD = "Sn59042181#@"

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 120))

def send_to_telegram(message_text):
    """Send message to Telegram"""
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
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Telegram error: {e}")

def login_to_sylectus(page):
    """Login using fresh codegen selectors"""
    try:
        print("🔐 Starting login...")
        
        # Navigate to Sylectus
        page.goto("https://www.sylectus.net/")
        
        # Accept cookies
        page.get_by_role("button", name="Accept All Cookies").click()
        print("✅ Cookies accepted")
        
        # Click login
        page.get_by_role("link", name="LOG IN").click()
        
        # Fill corporate ID (use working sequence)
        page.get_by_role("textbox", name="Corporate ID").click()
        page.get_by_role("textbox", name="Corporate ID").fill(CORPORATE_ID)
        page.get_by_role("textbox", name="Corporate ID").press("Tab")
        
        # Fill corporate password
        page.locator("#ctl00_bodyPlaceholder_corpPasswordField").fill(CORPORATE_PASSWORD)
        
        # Click Continue (missing from new codegen!)
        page.get_by_role("link", name="Continue").click()
        
        # Select user dropdown
        page.get_by_label("").click()
        page.get_by_role("option", name="SNICHOLS").click()
        
        # Fill user password
        page.get_by_placeholder(" ").click()
        page.get_by_placeholder(" ").fill(USER_PASSWORD)
        
        # Click Log in
        page.get_by_role("link", name="Log in").click()
        
        print("✅ Login completed")
        return True
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

def scrape_load_board(page):
    """Scrape the load board iframe"""
    try:
        print("🚚 Navigating to Load Board...")
        page.get_by_role("link", name="Load Board").click()
        
        # Wait for iframe to load
        time.sleep(5)
        
        # Get iframe (using frame_locator from codegen)
        iframe = page.frame_locator("#iframe1")
        
        print("🔍 Scanning for loads...")
        
        # Get all table rows in iframe
        rows = iframe.locator("tr").all()
        
        print(f"📊 Found {len(rows)} rows to check")
        
        for i, row in enumerate(rows[:10]):  # Check first 10 rows
            try:
                row_text = row.inner_text().strip()
                if row_text and len(row_text) > 50:
                    print(f"Row {i}: {row_text[:100]}...")
                    
                    # Send sample to Telegram
                    message = f"🆕 **SAMPLE LOAD DATA**\n\n```\n{row_text[:500]}\n```"
                    send_to_telegram(message)
                    
            except Exception as e:
                print(f"❌ Error processing row {i}: {e}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error scraping load board: {e}")
        return False

def main():
    """Main scraper"""
    print("🚀 Starting Fresh Sylectus Scraper...")
    
    send_to_telegram("🚀 Fresh Sylectus Scraper starting...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible for testing
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(60000)
        
        try:
            # Login
            if login_to_sylectus(page):
                # Scrape once
                scrape_load_board(page)
            else:
                send_to_telegram("❌ Login failed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            send_to_telegram(f"💥 Error: {e}")
        finally:
            time.sleep(5)  # Give time to see results
            browser.close()

if __name__ == "__main__":
    main()