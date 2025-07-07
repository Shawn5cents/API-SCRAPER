#!/usr/bin/env python3
"""
Test headless browser configuration
"""

from playwright.sync_api import sync_playwright
import time

def test_headless_browser():
    """Test if headless browser works properly"""
    print("🧪 Testing headless browser configuration...")
    
    try:
        with sync_playwright() as p:
            print("🔧 Launching headless browser...")
            
            # Launch with headless configuration
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ]
            )
            
            print("✅ Browser launched successfully")
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            page.set_default_timeout(30000)
            
            print("🌐 Testing navigation to Google...")
            page.goto("https://www.google.com")
            title = page.title()
            print(f"✅ Google loaded: {title}")
            
            print("🌐 Testing navigation to Sylectus...")
            page.goto("https://www.sylectus.net/", timeout=30000)
            title = page.title()
            print(f"✅ Sylectus loaded: {title}")
            
            # Check for cookie button
            try:
                cookie_btn = page.get_by_role("button", name="Accept All Cookies")
                if cookie_btn.is_visible():
                    print("✅ Cookie button found")
                else:
                    print("ℹ️ Cookie button not visible")
            except:
                print("ℹ️ Cookie button not found")
            
            # Check for login link
            try:
                login_link = page.get_by_role("link", name="LOG IN")
                if login_link.is_visible():
                    print("✅ LOGIN link found")
                else:
                    print("⚠️ LOGIN link not visible")
            except:
                print("⚠️ LOGIN link not found")
            
            browser.close()
            print("✅ Browser closed successfully")
            
            return True
            
    except Exception as e:
        print(f"❌ Headless browser test failed: {e}")
        return False

def test_playwright_installation():
    """Test if Playwright is properly installed"""
    print("🧪 Testing Playwright installation...")
    
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright imported successfully")
        
        with sync_playwright() as p:
            # Check if chromium is available
            try:
                browser = p.chromium.launch(headless=True)
                print("✅ Chromium browser available")
                browser.close()
                return True
            except Exception as e:
                print(f"❌ Chromium not available: {e}")
                print("💡 Try running: python -m playwright install chromium")
                return False
                
    except Exception as e:
        print(f"❌ Playwright import failed: {e}")
        return False

def main():
    """Run headless configuration tests"""
    print("🚀 Testing Headless Configuration\n")
    
    # Test 1: Playwright installation
    if not test_playwright_installation():
        print("\n❌ Playwright installation test failed")
        return False
    
    print()
    
    # Test 2: Headless browser
    if not test_headless_browser():
        print("\n❌ Headless browser test failed")
        return False
    
    print("\n🎉 All headless tests passed! System ready for production.")
    return True

if __name__ == "__main__":
    main()