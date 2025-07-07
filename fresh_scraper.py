#!/usr/bin/env python3
"""
Fresh Sylectus Scraper - Manual/Interactive approach
Just navigate and scrape whatever pages you're on
"""

from playwright.sync_api import sync_playwright
import time
import json
import re

# Your credentials
CORPORATE_ID = "2103390"
CORPORATE_PASSWORD = "Sn59042181#@"
USERNAME = "SNICHOLS"
USER_PASSWORD = "Sn59042181#@"

def scrape_current_page(page, step_name):
    """Scrape whatever is on the current page"""
    print(f"📄 Scraping {step_name}...")
    
    # Get basic page info
    info = {
        "url": page.url,
        "title": page.title(),
        "step": step_name
    }
    
    # Take screenshot
    page.screenshot(path=f"{step_name}.png")
    print(f"📸 Screenshot saved: {step_name}.png")
    
    # Save full HTML content
    with open(f"{step_name}.html", "w") as f:
        f.write(page.content())
    print(f"💾 HTML saved: {step_name}.html")
    
    # Try to extract any table data
    try:
        # Look for any tables
        tables = page.locator("table").all()
        if tables:
            print(f"📊 Found {len(tables)} tables")
            for i, table in enumerate(tables):
                table_text = table.inner_text()
                with open(f"{step_name}_table_{i}.txt", "w") as f:
                    f.write(table_text)
                print(f"💾 Table {i} saved: {step_name}_table_{i}.txt")
    except Exception as e:
        print(f"⚠️ Table extraction failed: {e}")
    
    # Look for any iframes
    try:
        iframes = page.locator("iframe").all()
        if iframes:
            print(f"🖼️ Found {len(iframes)} iframes")
            for i, iframe in enumerate(iframes):
                try:
                    iframe_content = iframe.content_frame()
                    if iframe_content:
                        iframe_text = iframe_content.inner_text()
                        with open(f"{step_name}_iframe_{i}.txt", "w") as f:
                            f.write(iframe_text)
                        print(f"💾 Iframe {i} content saved: {step_name}_iframe_{i}.txt")
                except Exception as e:
                    print(f"⚠️ Iframe {i} extraction failed: {e}")
    except Exception as e:
        print(f"⚠️ Iframe detection failed: {e}")
    
    return info

def main():
    print("🚀 Starting Fresh Sylectus Scraper...")
    
    with sync_playwright() as p:
        # Launch visible browser
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500,  # Slow down for visibility
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        page.set_default_timeout(60000)
        
        try:
            # Step 1: Go to Sylectus homepage
            print("🌐 Navigating to Sylectus...")
            page.goto("https://www.sylectus.net/")
            time.sleep(3)
            scrape_current_page(page, "01_homepage")
            
            # Step 2: Accept cookies if needed
            try:
                cookie_btn = page.get_by_role("button", name="Accept All Cookies")
                if cookie_btn.is_visible():
                    cookie_btn.click()
                    print("✅ Cookies accepted")
                    time.sleep(2)
                    scrape_current_page(page, "02_after_cookies")
            except:
                print("⚠️ No cookie button found")
            
            print("\n🎮 MANUAL CONTROL TIME!")
            print("📝 Now manually:")
            print("   1. Click LOGIN")
            print("   2. Enter your credentials")
            print("   3. Navigate to load board")
            print("   4. Press Enter here after each major step")
            print("   5. Press Ctrl+C when done")
            
            step = 3
            while True:
                try:
                    input(f"\n➡️ Press Enter after completing step {step} (Ctrl+C to stop): ")
                    scrape_current_page(page, f"step_{step:02d}")
                    step += 1
                except KeyboardInterrupt:
                    print("\n🛑 Manual session ended")
                    break
            
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            print("🔒 Closing browser...")
            browser.close()
            print("✅ Session complete! Check the generated files.")

if __name__ == "__main__":
    main()