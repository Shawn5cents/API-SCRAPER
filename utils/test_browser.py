#!/usr/bin/env python3
"""
Simple browser test to debug the issue
"""

from playwright.sync_api import sync_playwright
import time

print("🧪 Testing basic browser functionality...")

try:
    with sync_playwright() as p:
        print("✅ Playwright imported successfully")
        
        browser = p.chromium.launch(headless=False)
        print("✅ Browser launched")
        
        context = browser.new_context()
        page = context.new_page()
        print("✅ Page created")
        
        print("🌐 Navigating to Google first...")
        page.goto("https://www.google.com", timeout=30000)
        print("✅ Google loaded successfully")
        
        print("🌐 Now trying Sylectus...")
        page.goto("https://www.sylectus.net/", timeout=30000)
        print("✅ Sylectus page loaded")
        
        # Get page title
        title = page.title()
        print(f"📄 Page title: {title}")
        
        # Check for cookie button
        try:
            cookie_button = page.get_by_role("button", name="Accept All Cookies")
            if cookie_button.is_visible():
                print("✅ Cookie button found and visible")
            else:
                print("⚠️ Cookie button found but not visible")
        except Exception as e:
            print(f"❌ Cookie button not found: {e}")
        
        # Take a screenshot for debugging
        page.screenshot(path="debug_page.png")
        print("📸 Screenshot saved as debug_page.png")
        
        time.sleep(5)
        browser.close()
        print("✅ Test completed successfully")
        
except Exception as e:
    print(f"❌ Test failed: {e}")