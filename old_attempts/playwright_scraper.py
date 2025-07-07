#!/usr/bin/env python3
"""
Advanced Playwright Website Scraper with Telegram Alerts
Based on the comprehensive plan for automated website monitoring
"""

import os
import time
import json
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

class PlaywrightScraper:
    def __init__(self):
        # Configuration from environment
        self.website_username = os.getenv('WEBSITE_USERNAME')
        self.website_password = os.getenv('WEBSITE_PASSWORD')
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.check_interval = int(os.getenv('CHECK_INTERVAL', 300))
        self.headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        self.website_url = os.getenv('WEBSITE_URL', 'https://www.sylectus.com/login')
        
        # Tracking
        self.sent_items_file = os.path.join(os.path.dirname(__file__), 'sent_items.txt')
        self.known_items = self.load_sent_items()
        self.first_run = True
        
        # Validate required config
        if not all([self.telegram_bot_token, self.telegram_chat_id]):
            raise ValueError("Missing required Telegram configuration")
    
    def load_sent_items(self):
        """Load previously sent items from file"""
        try:
            if os.path.exists(self.sent_items_file):
                with open(self.sent_items_file, 'r') as f:
                    return set(line.strip() for line in f.readlines())
            return set()
        except Exception as e:
            print(f"❌ Error loading sent items: {e}")
            return set()
    
    def save_sent_item(self, item_id):
        """Save item ID to prevent duplicate notifications"""
        try:
            with open(self.sent_items_file, 'a') as f:
                f.write(f"{item_id}\n")
            self.known_items.add(item_id)
        except Exception as e:
            print(f"❌ Error saving sent item: {e}")
    
    def send_to_telegram(self, message_text):
        """Send message to Telegram"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message_text,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, data=data, timeout=10)
            success = response.status_code == 200
            
            if success:
                print(f"📱 Telegram: ✅ Message sent")
            else:
                print(f"📱 Telegram: ❌ Failed ({response.status_code})")
                
            return success
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def login_to_website(self, page):
        """Login to the website using credentials"""
        try:
            print("🔐 Attempting login...")
            
            # Navigate to login page
            page.goto(self.website_url)
            page.wait_for_load_state('networkidle')
            
            # Wait for login form to be visible
            page.wait_for_selector('input[type="text"], input[name*="user"], input[id*="user"]', timeout=10000)
            
            # Find and fill username field
            username_selectors = [
                'input[name*="user"]',
                'input[id*="user"]', 
                'input[type="text"]',
                'input[name*="login"]',
                'input[id*="login"]'
            ]
            
            username_filled = False
            for selector in username_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.fill(selector, self.website_username)
                        username_filled = True
                        print(f"✅ Username filled using selector: {selector}")
                        break
                except:
                    continue
            
            if not username_filled:
                print("❌ Could not find username field")
                return False
            
            # Find and fill password field
            password_selectors = [
                'input[type="password"]',
                'input[name*="pass"]',
                'input[id*="pass"]'
            ]
            
            password_filled = False
            for selector in password_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.fill(selector, self.website_password)
                        password_filled = True
                        print(f"✅ Password filled using selector: {selector}")
                        break
                except:
                    continue
            
            if not password_filled:
                print("❌ Could not find password field")
                return False
            
            # Find and click login button
            login_button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Sign In")',
                'input[value*="Login"]',
                'input[value*="Sign In"]'
            ]
            
            login_clicked = False
            for selector in login_button_selectors:
                try:
                    if page.locator(selector).count() > 0:
                        page.click(selector)
                        login_clicked = True
                        print(f"✅ Login button clicked using selector: {selector}")
                        break
                except:
                    continue
            
            if not login_clicked:
                print("❌ Could not find login button")
                return False
            
            # Wait for login to complete
            page.wait_for_load_state('networkidle', timeout=15000)
            
            # Check if login was successful
            current_url = page.url
            if 'login' not in current_url.lower() and 'error' not in current_url.lower():
                print("✅ Login successful")
                return True
            else:
                print("❌ Login may have failed - still on login page")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def extract_item_data(self, item_locator):
        """Extract data from a single item"""
        try:
            # Get all text content from the item
            item_text = item_locator.inner_text()
            
            # Extract various pieces of information
            data = {
                'title': self.extract_title(item_text, item_locator),
                'price': self.extract_price(item_text),
                'location': self.extract_location(item_text),
                'date': self.extract_date(item_text),
                'link': self.extract_link(item_locator),
                'description': item_text[:200] + "..." if len(item_text) > 200 else item_text,
                'raw_text': item_text
            }
            
            return data
        except Exception as e:
            print(f"❌ Error extracting item data: {e}")
            return None
    
    def extract_title(self, text, locator):
        """Extract title from item"""
        try:
            # Try to find title in common selectors
            title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.heading', '[class*="title"]']
            
            for selector in title_selectors:
                try:
                    title_element = locator.locator(selector).first
                    if title_element.count() > 0:
                        return title_element.inner_text().strip()
                except:
                    continue
            
            # Fallback: use first line of text
            lines = text.split('\n')
            return lines[0][:100] if lines else "Unknown Title"
        except:
            return "Unknown Title"
    
    def extract_price(self, text):
        """Extract price from text"""
        price_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',
            r'[\d,]+\s*(?:USD|dollars?)',
            r'Price:\s*\$?([\d,]+(?:\.\d{2})?)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Price not specified"
    
    def extract_location(self, text):
        """Extract location from text"""
        location_patterns = [
            r'([A-Z][a-z]+,?\s+[A-Z]{2})',
            r'Location:\s*([^\n]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+,?\s+[A-Z]{2})'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return "Location not specified"
    
    def extract_date(self, text):
        """Extract date from text"""
        date_patterns = [
            r'\d{1,2}\/\d{1,2}\/\d{2,4}',
            r'\d{4}-\d{2}-\d{2}',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Date not specified"
    
    def extract_link(self, locator):
        """Extract link from item"""
        try:
            # Try to find links in the item
            link_selectors = ['a', '[href]']
            
            for selector in link_selectors:
                try:
                    link_element = locator.locator(selector).first
                    if link_element.count() > 0:
                        href = link_element.get_attribute('href')
                        if href and href.startswith('http'):
                            return href
                        elif href and href.startswith('/'):
                            # Relative URL, construct full URL
                            return f"https://www.sylectus.com{href}"
                except:
                    continue
            
            return "No link available"
        except:
            return "No link available"
    
    def format_item_message(self, item_data):
        """Format item data for Telegram"""
        status = "📋 CURRENT ITEM" if self.first_run else "🆕 NEW ITEM"
        
        return f"""{status}

📝 **{item_data['title']}**

💰 **Price:** {item_data['price']}
📍 **Location:** {item_data['location']}
📅 **Date:** {item_data['date']}
🔗 **Link:** {item_data['link']}

📄 **Description:**
{item_data['description']}

⏰ **Found:** {datetime.now().strftime('%I:%M %p')}

🌐 *Via Playwright Scraper*"""
    
    def scrape_items(self, page):
        """Scrape items from the current page"""
        try:
            print("🔍 Scraping items from page...")
            
            # Wait for page to load
            page.wait_for_load_state('networkidle')
            
            # Common item container selectors
            item_selectors = [
                '[class*="item"]',
                '[class*="listing"]',
                '[class*="load"]',
                '[class*="row"]',
                'tr',
                '.item',
                '.listing',
                '.load-item'
            ]
            
            items = []
            
            for selector in item_selectors:
                try:
                    item_locators = page.locator(selector).all()
                    
                    if len(item_locators) > 2:  # Found reasonable number of items
                        print(f"📊 Found {len(item_locators)} items using selector: {selector}")
                        
                        for i, item_locator in enumerate(item_locators):
                            try:
                                item_data = self.extract_item_data(item_locator)
                                if item_data and len(item_data['raw_text'].strip()) > 10:
                                    # Create unique ID for this item
                                    item_id = f"{item_data['title'][:50]}_{i}"
                                    
                                    # Check if we've already sent this item
                                    if item_id not in self.known_items:
                                        item_data['id'] = item_id
                                        items.append(item_data)
                                        
                                        if self.first_run:
                                            print(f"📋 CURRENT: {item_data['title'][:50]}")
                                        else:
                                            print(f"🆕 NEW: {item_data['title'][:50]}")
                                    
                            except Exception as e:
                                print(f"❌ Error processing item {i}: {e}")
                                continue
                        
                        break  # Found items, don't try other selectors
                        
                except Exception as e:
                    continue
            
            return items
            
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            return []
    
    def run_scraping_cycle(self):
        """Run one complete scraping cycle"""
        try:
            print(f"\n🔄 {'=== FIRST RUN ===' if self.first_run else '=== MONITORING CYCLE ==='} {datetime.now().strftime('%H:%M:%S')}")
            
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context()
                page = context.new_page()
                
                # Login if credentials provided
                if self.website_username and self.website_password:
                    if not self.login_to_website(page):
                        print("❌ Login failed, continuing without login...")
                        # Continue anyway, might work with public access
                
                # Navigate to main page if different from login
                if hasattr(self, 'main_page_url'):
                    page.goto(self.main_page_url)
                    page.wait_for_load_state('networkidle')
                
                # Scrape items
                items = self.scrape_items(page)
                
                # Send notifications for new items
                if items:
                    print(f"📱 Sending {len(items)} item alerts...")
                    for item in items:
                        message = self.format_item_message(item)
                        
                        if self.send_to_telegram(message):
                            # Mark as sent
                            self.save_sent_item(item['id'])
                            time.sleep(1)  # Rate limit
                        else:
                            print(f"❌ Failed to send message for: {item['title'][:50]}")
                else:
                    status = "current" if self.first_run else "new"
                    print(f"✅ No {status} items found ({len(self.known_items)} total tracked)")
                
                # Close browser
                browser.close()
                
                # Mark first run as complete
                if self.first_run:
                    self.first_run = False
                    print(f"📊 First run complete: {len(items)} items processed")
                
                return len(items)
                
        except Exception as e:
            print(f"❌ Scraping cycle error: {e}")
            return 0
    
    def run(self):
        """Main monitoring loop"""
        print("🚀 Starting Playwright Website Scraper...")
        
        # Send startup notification
        startup_message = "🚀 **Playwright Scraper Started**\n\nMonitoring website for new items and alerts."
        self.send_to_telegram(startup_message)
        
        # Run first cycle
        self.run_scraping_cycle()
        
        # Continuous monitoring
        while True:
            try:
                print(f"\n⏰ Waiting {self.check_interval} seconds until next check...")
                time.sleep(self.check_interval)
                self.run_scraping_cycle()
                
            except KeyboardInterrupt:
                print("\n⏹️ Stopping scraper...")
                self.send_to_telegram("⏹️ **Playwright Scraper Stopped**")
                break
            except Exception as e:
                print(f"❌ Main loop error: {e}")
                time.sleep(30)  # Wait before retrying

if __name__ == "__main__":
    try:
        scraper = PlaywrightScraper()
        scraper.run()
    except Exception as e:
        print(f"❌ Failed to start scraper: {e}")