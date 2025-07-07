#!/usr/bin/env python3
"""
Session Extractor for Sylectus
Handles login with Playwright and extracts session cookies for MCP server usage
"""

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Credentials from working scraper
CORPORATE_ID = "2103390"
CORPORATE_PASSWORD = "Sn59042181#@"
USERNAME = "SNICHOLS"
USER_PASSWORD = "Sn59042181#@"

class SylectusSessionExtractor:
    def __init__(self, headless=True):
        self.headless = headless
        self.session_file = "sylectus_session.json"
        self.session_data = None
        
    def perform_login(self, page):
        """Perform complete login sequence from working scraper"""
        try:
            print("🔐 Starting login sequence...")
            
            # Navigate to main page
            print("🌐 Loading Sylectus homepage...")
            page.goto("https://www.sylectus.net/", timeout=60000)
            print("✅ Page loaded")
            
            # Wait for page to fully load
            time.sleep(3)
            
            # Accept cookies if present (try multiple approaches)
            print("🍪 Looking for cookie consent...")
            try:
                # Wait for the button to appear
                page.wait_for_load_state("networkidle")
                time.sleep(2)
                
                # Try to find and click the cookie button
                cookie_button = page.get_by_role("button", name="Accept All Cookies")
                if cookie_button.is_visible():
                    cookie_button.click()
                    print("✅ Cookies accepted")
                    time.sleep(1)
                else:
                    print("⚠️ Cookie button not visible")
            except Exception as e:
                print(f"⚠️ Cookie button interaction failed: {e}")
                # Continue anyway, might not always be needed
            
            # Click LOG IN link - wait for it to be available
            print("🔐 Looking for LOG IN link...")
            try:
                page.wait_for_selector("a:has-text('LOG IN')", timeout=30000)
                page.get_by_role("link", name="LOG IN").click()
                print("✅ LOG IN clicked")
            except Exception as e:
                print(f"❌ Could not find LOG IN link: {e}")
                # Try alternative approach
                page.locator("a:has-text('LOG IN')").click()
                print("✅ LOG IN clicked (alternative method)")
            
            # Fill Corporate ID
            page.get_by_role("textbox", name="Corporate ID").click()
            page.get_by_role("textbox", name="Corporate ID").fill(CORPORATE_ID)
            page.get_by_role("textbox", name="Corporate ID").press("Tab")
            
            # Fill Corporate Password
            page.locator("#ctl00_bodyPlaceholder_corpPasswordField").fill(CORPORATE_PASSWORD)
            
            # Click Continue
            page.get_by_role("link", name="Continue").click()
            
            # Select user dropdown
            page.get_by_label("").click()
            page.get_by_role("option", name=USERNAME).click()
            
            # Fill user password
            page.get_by_placeholder(" ").click()
            page.get_by_placeholder(" ").fill(USER_PASSWORD)
            
            # Click Log in
            page.get_by_role("link", name="Log in").click()
            
            # Wait for successful login (look for Load Board link)
            page.wait_for_selector("a:has-text('Load Board')", timeout=30000)
            print("✅ Login successful - Load Board link found")
            
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False
    
    def extract_session_cookies(self, context):
        """Extract all cookies from the browser context"""
        try:
            cookies = context.cookies()
            
            # Convert cookies to requests-compatible format
            session_cookies = {}
            for cookie in cookies:
                session_cookies[cookie['name']] = cookie['value']
            
            # Get domain info
            domains = list(set([cookie.get('domain', '') for cookie in cookies]))
            
            session_data = {
                'cookies': session_cookies,
                'raw_cookies': cookies,
                'domains': domains,
                'extracted_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=6)).isoformat()  # Assume 6 hour session
            }
            
            print(f"✅ Extracted {len(session_cookies)} cookies from {len(domains)} domains")
            return session_data
            
        except Exception as e:
            print(f"❌ Failed to extract cookies: {e}")
            return None
    
    def save_session(self, session_data):
        """Save session data to file"""
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            print(f"✅ Session saved to {self.session_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to save session: {e}")
            return False
    
    def load_session(self):
        """Load existing session from file"""
        try:
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Check if session is still valid
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                print("⚠️ Stored session has expired")
                return None
            
            print("✅ Valid session loaded from file")
            return session_data
        except FileNotFoundError:
            print("ℹ️ No existing session file found")
            return None
        except Exception as e:
            print(f"❌ Error loading session: {e}")
            return None
    
    def create_fresh_session(self):
        """Create a new session by performing login"""
        print("🚀 Creating fresh Sylectus session...")
        
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = context.new_page()
            page.set_default_timeout(30000)
            
            try:
                # Perform login
                if not self.perform_login(page):
                    return None
                
                # Navigate to Load Board to ensure full session
                print("🚚 Navigating to Load Board to establish full session...")
                page.get_by_role("link", name="Load Board").click()
                time.sleep(5)  # Allow load board to fully load
                
                # Extract session cookies
                session_data = self.extract_session_cookies(context)
                if not session_data:
                    return None
                
                # Save session for reuse
                if self.save_session(session_data):
                    self.session_data = session_data
                    return session_data
                
                return None
                
            except Exception as e:
                print(f"❌ Error creating session: {e}")
                return None
            finally:
                browser.close()
    
    def get_valid_session(self, force_refresh=False):
        """Get a valid session, creating new one if needed"""
        if force_refresh:
            print("🔄 Force refreshing session...")
            return self.create_fresh_session()
        
        # Try to load existing session first
        session_data = self.load_session()
        if session_data:
            self.session_data = session_data
            return session_data
        
        # Create new session if none exists or expired
        return self.create_fresh_session()
    
    def get_requests_cookies(self):
        """Get cookies formatted for requests library"""
        if not self.session_data:
            session_data = self.get_valid_session()
            if not session_data:
                return None
        
        return self.session_data.get('cookies', {})
    
    def get_headers(self):
        """Get recommended headers for requests"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

# Test function
def test_session_extraction():
    """Test the session extraction"""
    extractor = SylectusSessionExtractor(headless=False)
    
    print("🧪 Testing session extraction...")
    session_data = extractor.get_valid_session()
    
    if session_data:
        print("✅ Session extraction successful!")
        print(f"📊 Cookies extracted: {len(session_data['cookies'])}")
        print(f"🌐 Domains: {', '.join(session_data['domains'])}")
        print(f"⏰ Valid until: {session_data['expires_at']}")
        
        # Test requests format
        cookies = extractor.get_requests_cookies()
        headers = extractor.get_headers()
        
        print("✅ Session ready for MCP server usage")
        return True
    else:
        print("❌ Session extraction failed")
        return False

if __name__ == "__main__":
    test_session_extraction()