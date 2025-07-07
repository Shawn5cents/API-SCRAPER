#!/usr/bin/env python3
"""
Test scraper to debug where it's getting stuck
"""

from playwright.sync_api import sync_playwright
import time
from dotenv import load_dotenv

load_dotenv()

print("🚀 Starting test scraper...")

with sync_playwright() as p:
    print("✅ Playwright started")
    
    browser = p.chromium.launch(headless=False)
    print("✅ Browser launched")
    
    context = browser.new_context()
    page = context.new_page()
    print("✅ Page created")
    
    try:
        print("🌐 Navigating to Sylectus...")
        page.goto("https://www.sylectus.net/", timeout=30000)
        print("✅ Page loaded")
        
        print("🍪 Looking for cookie button...")
        try:
            page.get_by_role("button", name="Accept All Cookies").click(timeout=10000)
            print("✅ Cookies accepted")
        except:
            print("⚠️ No cookie button found")
        
        print("🔐 Looking for login link...")
        try:
            page.get_by_role("link", name="LOG IN").click(timeout=10000)
            print("✅ Login link clicked")
        except:
            print("❌ Login link not found")
        
        print("📝 Looking for Corporate ID field...")
        try:
            page.get_by_role("textbox", name="Corporate ID").fill("2103390", timeout=10000)
            print("✅ Corporate ID filled")
        except:
            print("❌ Corporate ID field not found")
        
        print("Test completed - browser will stay open for 30 seconds")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        browser.close()
        print("🔒 Browser closed")