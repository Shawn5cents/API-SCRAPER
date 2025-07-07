#!/usr/bin/env python3
"""
Simple Sylectus Scraper - You navigate, I scrape
"""

from playwright.sync_api import sync_playwright
import json
import time
import re

def extract_load_data(page):
    """Extract all load data from current page"""
    loads = []
    
    try:
        # Try to find iframe content first
        iframe = page.locator("#iframe1").content_frame()
        if iframe:
            print("📋 Found iframe, scraping load board...")
            # Get all table rows
            rows = iframe.locator("tr").all()
            for i, row in enumerate(rows):
                try:
                    text = row.inner_text().strip()
                    if text and len(text) > 50:  # Likely a load row
                        loads.append({
                            "row_number": i,
                            "raw_text": text
                        })
                except:
                    continue
        else:
            # Regular page content
            print("📋 Scraping regular page content...")
            tables = page.locator("table").all()
            for table in tables:
                rows = table.locator("tr").all()
                for i, row in enumerate(rows):
                    try:
                        text = row.inner_text().strip()
                        if text and len(text) > 20:
                            loads.append({
                                "row_number": i,
                                "raw_text": text
                            })
                    except:
                        continue
    except Exception as e:
        print(f"❌ Error extracting loads: {e}")
    
    return loads

def main():
    print("🚀 Simple Sylectus Scraper")
    print("Navigate to the pages you want, I'll scrape whatever you're on")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("🌐 Starting at Sylectus...")
        page.goto("https://www.sylectus.net/")
        
        print("\n🎮 GO NAVIGATE TO YOUR PAGES")
        print("When you're ready to scrape, come back here and press Enter")
        
        try:
            while True:
                input("\n➡️ Press Enter to scrape current page (Ctrl+C to quit): ")
                
                url = page.url
                title = page.title()
                print(f"\n📄 Scraping: {title}")
                print(f"🔗 URL: {url}")
                
                # Take screenshot
                timestamp = int(time.time())
                screenshot_file = f"scrape_{timestamp}.png"
                page.screenshot(path=screenshot_file)
                print(f"📸 Screenshot: {screenshot_file}")
                
                # Extract loads
                loads = extract_load_data(page)
                
                if loads:
                    print(f"✅ Found {len(loads)} potential load entries")
                    
                    # Save to file
                    data_file = f"loads_{timestamp}.json"
                    with open(data_file, "w") as f:
                        json.dump({
                            "url": url,
                            "title": title,
                            "timestamp": timestamp,
                            "loads": loads
                        }, f, indent=2)
                    print(f"💾 Data saved: {data_file}")
                    
                    # Show first few
                    for i, load in enumerate(loads[:3]):
                        print(f"\n📦 Load {i+1}:")
                        print(f"   {load['raw_text'][:100]}...")
                else:
                    print("❌ No load data found on this page")
                
        except KeyboardInterrupt:
            print("\n🛑 Scraping stopped")
        finally:
            browser.close()

if __name__ == "__main__":
    main()