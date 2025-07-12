#!/usr/bin/env python3
"""
Stealth Session Keeper - Advanced automation for persistent Sylectus sessions
Uses multiple strategies to maintain sessions without detection:
1. Undetected Chrome with profile persistence
2. Session rotation and health monitoring  
3. Human-like interaction patterns
4. Smart login automation with anti-detection
"""

import os
import json
import time
import random
import sqlite3
import requests
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class StealthSessionKeeper:
    def __init__(self):
        self.base_url = "https://www.sylectus.com"
        self.profiles_dir = Path("stealth_profiles")
        self.profiles_dir.mkdir(exist_ok=True)
        self.db_path = "stealth_sessions.db"
        self.init_database()
        
    def init_database(self):
        """Initialize session database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stealth_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT UNIQUE,
                cookies TEXT,
                session_data TEXT,
                user_agent TEXT,
                created_at TIMESTAMP,
                last_validated TIMESTAMP,
                validation_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id TEXT,
                timestamp TIMESTAMP,
                action TEXT,
                result TEXT,
                response_time REAL,
                error_details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_undetected_session(self, username: str, password: str) -> str:
        """Create new undetected browser session"""
        profile_id = f"stealth_{int(time.time())}_{random.randint(1000, 9999)}"
        profile_path = self.profiles_dir / profile_id
        profile_path.mkdir(exist_ok=True)
        
        try:
            # Install undetected-chromedriver if not available
            try:
                import undetected_chromedriver as uc
            except ImportError:
                print("📦 Installing undetected-chromedriver...")
                subprocess.run(["pip", "install", "undetected-chromedriver"], check=True)
                import undetected_chromedriver as uc
            
            # Configure stealth options
            options = uc.ChromeOptions()
            options.add_argument(f"--user-data-dir={profile_path}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--remote-debugging-port=9222")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Create driver
            driver = uc.Chrome(options=options, version_main=None)
            
            # Execute stealth modifications
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            })
            
            # Perform stealthy login
            success = self.stealth_login(driver, username, password)
            
            if success:
                # Extract session data
                cookies = driver.get_cookies()
                session_data = self.extract_session_tokens(driver)
                user_agent = driver.execute_script("return navigator.userAgent;")
                
                # Save to database
                self.save_session_data(profile_id, cookies, session_data, user_agent)
                
                print(f"✅ Stealth session created: {profile_id}")
                
                # Keep browser alive in background
                # driver.quit()  # Commented to keep session alive
                
                return profile_id
            else:
                driver.quit()
                return None
                
        except Exception as e:
            print(f"❌ Failed to create stealth session: {e}")
            return None
    
    def stealth_login(self, driver, username: str, password: str) -> bool:
        """Perform human-like login with advanced stealth techniques"""
        try:
            print("🕵️ Starting stealth login...")
            
            # Navigate with random delay
            driver.get(f"{self.base_url}/Login.aspx")
            time.sleep(random.uniform(2.5, 4.5))
            
            # Simulate human reading time
            self.simulate_reading_behavior(driver)
            
            # Find form elements with multiple strategies
            username_field = self.find_element_stealth(driver, [
                "txtUserName", "username", "user", "login"
            ])
            
            password_field = self.find_element_stealth(driver, [
                "txtPassword", "password", "pass", "pwd"
            ])
            
            if not username_field or not password_field:
                print("❌ Could not find login form elements")
                return False
            
            # Human-like typing
            self.human_type(username_field, username)
            time.sleep(random.uniform(1, 2))
            
            self.human_type(password_field, password)
            time.sleep(random.uniform(1, 2))
            
            # Find and click submit button
            submit_button = self.find_element_stealth(driver, [
                "btnSubmit", "submit", "login", "sign-in"
            ], by_text=True)
            
            if submit_button:
                # Random mouse movement before click
                self.simulate_mouse_movement(driver)
                submit_button.click()
            else:
                # Try form submission
                password_field.submit()
            
            # Wait for redirect with timeout
            start_time = time.time()
            while time.time() - start_time < 15:
                current_url = driver.current_url
                if "main_page.aspx" in current_url or "Main.aspx" in current_url:
                    print("✅ Login successful!")
                    return True
                elif "Login.aspx" in current_url and time.time() - start_time > 5:
                    # Check for error messages
                    error_elements = driver.find_elements("css selector", ".error, .alert, .warning")
                    if error_elements:
                        print(f"❌ Login error: {error_elements[0].text}")
                        return False
                
                time.sleep(0.5)
            
            print("❌ Login timeout or failed")
            return False
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def find_element_stealth(self, driver, identifiers: list, by_text: bool = False):
        """Find elements using multiple strategies"""
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import NoSuchElementException
        
        for identifier in identifiers:
            try:
                if by_text:
                    # Try finding by text content
                    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{identifier}')]")
                    if elements:
                        return elements[0]
                    # Try finding by value
                    elements = driver.find_elements(By.XPATH, f"//input[@value='{identifier}']")
                    if elements:
                        return elements[0]
                else:
                    # Try by name
                    try:
                        return driver.find_element(By.NAME, identifier)
                    except NoSuchElementException:
                        pass
                    
                    # Try by id
                    try:
                        return driver.find_element(By.ID, identifier)
                    except NoSuchElementException:
                        pass
                    
                    # Try by class
                    try:
                        return driver.find_element(By.CLASS_NAME, identifier)
                    except NoSuchElementException:
                        pass
            except Exception:
                continue
        
        return None
    
    def human_type(self, element, text: str):
        """Simulate human typing patterns"""
        element.click()
        time.sleep(random.uniform(0.2, 0.5))
        
        for char in text:
            element.send_keys(char)
            # Variable typing speed
            if char.isspace():
                time.sleep(random.uniform(0.1, 0.3))
            else:
                time.sleep(random.uniform(0.05, 0.15))
            
            # Occasional pauses (thinking)
            if random.random() < 0.1:
                time.sleep(random.uniform(0.3, 0.8))
    
    def simulate_reading_behavior(self, driver):
        """Simulate human reading/scanning behavior"""
        # Random scrolling
        scroll_amount = random.randint(100, 300)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
        time.sleep(random.uniform(0.5, 1.5))
        
        # Scroll back
        driver.execute_script(f"window.scrollBy(0, -{scroll_amount})")
        time.sleep(random.uniform(0.3, 0.8))
    
    def simulate_mouse_movement(self, driver):
        """Simulate random mouse movement"""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            actions = ActionChains(driver)
            # Random movement within viewport
            x_offset = random.randint(-100, 100)
            y_offset = random.randint(-100, 100)
            actions.move_by_offset(x_offset, y_offset).perform()
            time.sleep(random.uniform(0.1, 0.3))
        except:
            pass  # Ignore if action chains fail
    
    def extract_session_tokens(self, driver) -> dict:
        """Extract all relevant session tokens"""
        try:
            # Get all forms of session data
            local_storage = driver.execute_script("return JSON.stringify(localStorage);")
            session_storage = driver.execute_script("return JSON.stringify(sessionStorage);")
            
            # Get hidden form fields that might contain tokens
            hidden_inputs = driver.find_elements("css selector", "input[type='hidden']")
            hidden_data = {}
            for input_elem in hidden_inputs:
                name = input_elem.get_attribute("name")
                value = input_elem.get_attribute("value")
                if name and value:
                    hidden_data[name] = value
            
            return {
                "local_storage": local_storage,
                "session_storage": session_storage,
                "hidden_fields": hidden_data,
                "current_url": driver.current_url,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"⚠️ Failed to extract session tokens: {e}")
            return {}
    
    def save_session_data(self, profile_id: str, cookies: list, session_data: dict, user_agent: str):
        """Save session data to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO stealth_sessions 
            (profile_id, cookies, session_data, user_agent, created_at, last_validated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            profile_id,
            json.dumps(cookies),
            json.dumps(session_data),
            user_agent,
            datetime.now(),
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
    
    def validate_session(self, profile_id: str) -> bool:
        """Validate if a session is still active"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT cookies, user_agent FROM stealth_sessions 
                WHERE profile_id = ? AND status = 'active'
            ''', (profile_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False
            
            cookies_json, user_agent = result
            cookies = json.loads(cookies_json)
            
            # Test session with requests
            session = requests.Session()
            
            # Set cookies
            for cookie in cookies:
                session.cookies.set(
                    cookie['name'], 
                    cookie['value'], 
                    domain=cookie.get('domain', '.sylectus.com')
                )
            
            # Set headers
            session.headers.update({
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # Test API endpoint
            start_time = time.time()
            response = session.get(f"{self.base_url}/II14_managepostedloads.asp", timeout=15)
            response_time = time.time() - start_time
            
            # Log the validation attempt
            self.log_session_activity(profile_id, "validation", 
                                    "success" if response.status_code == 200 and "Login.aspx" not in response.url else "failed",
                                    response_time)
            
            # Update validation timestamp
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE stealth_sessions 
                SET last_validated = ?, validation_count = validation_count + 1
                WHERE profile_id = ?
            ''', (datetime.now(), profile_id))
            conn.commit()
            conn.close()
            
            return response.status_code == 200 and "Login.aspx" not in response.url
            
        except Exception as e:
            self.log_session_activity(profile_id, "validation", "error", 0, str(e))
            return False
    
    def log_session_activity(self, profile_id: str, action: str, result: str, response_time: float, error_details: str = None):
        """Log session activity for monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO session_logs 
            (profile_id, timestamp, action, result, response_time, error_details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (profile_id, datetime.now(), action, result, response_time, error_details))
        
        conn.commit()
        conn.close()
    
    def get_best_session(self) -> str:
        """Get the best performing active session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get sessions ordered by success rate and recency
        cursor.execute('''
            SELECT profile_id, validation_count, last_validated
            FROM stealth_sessions 
            WHERE status = 'active' 
            ORDER BY success_rate DESC, last_validated DESC
            LIMIT 5
        ''')
        
        sessions = cursor.fetchall()
        conn.close()
        
        # Test each session until we find a valid one
        for profile_id, validation_count, last_validated in sessions:
            if self.validate_session(profile_id):
                return profile_id
        
        return None
    
    def get_session_cookies(self, profile_id: str) -> str:
        """Get session cookies as string for scraper"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT cookies FROM stealth_sessions 
            WHERE profile_id = ? AND status = 'active'
        ''', (profile_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            cookies = json.loads(result[0])
            cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            return cookie_string
        
        return None
    
    def maintain_sessions(self, max_sessions: int = 3):
        """Maintain a pool of active sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count active sessions
        cursor.execute('SELECT COUNT(*) FROM stealth_sessions WHERE status = "active"')
        active_count = cursor.fetchone()[0]
        
        # Clean up expired sessions
        cursor.execute('''
            UPDATE stealth_sessions 
            SET status = 'expired' 
            WHERE last_validated < ? AND status = 'active'
        ''', (datetime.now() - timedelta(hours=24),))
        
        conn.commit()
        conn.close()
        
        print(f"📊 Active sessions: {active_count}")
        
        # Test existing sessions
        valid_sessions = []
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT profile_id FROM stealth_sessions WHERE status = "active"')
        
        for (profile_id,) in cursor.fetchall():
            if self.validate_session(profile_id):
                valid_sessions.append(profile_id)
            else:
                # Mark as expired
                cursor.execute('UPDATE stealth_sessions SET status = "expired" WHERE profile_id = ?', (profile_id,))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Valid sessions: {len(valid_sessions)}")
        return valid_sessions

def main():
    """Main function for testing stealth session keeper"""
    keeper = StealthSessionKeeper()
    
    print("🕵️ Stealth Session Keeper")
    print("=" * 40)
    
    # Check existing sessions
    valid_sessions = keeper.maintain_sessions()
    
    if valid_sessions:
        best_session = keeper.get_best_session()
        if best_session:
            cookies = keeper.get_session_cookies(best_session)
            print(f"🍪 Best session cookies: {cookies[:100]}...")
            return cookies
    
    # No valid sessions, need to create new one
    print("⚠️ No valid sessions found. Manual session creation required.")
    print("Run the persistent_session_manager.py to create new sessions.")
    
    return None

if __name__ == "__main__":
    main()