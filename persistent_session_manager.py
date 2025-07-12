#!/usr/bin/env python3
"""
Advanced Persistent Session Management System for Sylectus
Maintains active sessions without manual intervention using multiple strategies:
1. Browser profile persistence with undetected Chrome
2. Session token refresh mechanisms
3. Headless browser management with stealth techniques
4. Smart cookie rotation and validation
5. Remote debugging capabilities
"""

import os
import json
import time
import random
import requests
import sqlite3
import hashlib
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class AdvancedSessionManager:
    def __init__(self, base_url="https://www.sylectus.com"):
        self.base_url = base_url
        self.session_db = "session_data.db"
        self.profile_dir = Path("chrome_profiles")
        self.profiles = {}
        self.active_drivers = {}
        self.session_pool = []
        self.remote_debugging_port = 9222
        
        # Create directories
        self.profile_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self.init_database()
        
        # Load existing sessions
        self.load_existing_sessions()
        
        print("🔐 Advanced Session Manager initialized")
    
    def init_database(self):
        """Initialize SQLite database for session storage"""
        conn = sqlite3.connect(self.session_db)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT UNIQUE,
                cookies TEXT,
                session_tokens TEXT,
                user_agent TEXT,
                viewport TEXT,
                created_at TIMESTAMP,
                last_used TIMESTAMP,
                expiry_time TIMESTAMP,
                status TEXT,
                login_credentials TEXT,
                fingerprint TEXT
            )
        ''')
        
        # Session health table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS session_health (
                session_id INTEGER,
                timestamp TIMESTAMP,
                response_time REAL,
                success BOOLEAN,
                error_message TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_realistic_profile(self) -> Dict:
        """Generate realistic browser profile"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ]
        
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1536, "height": 864}
        ]
        
        return {
            "user_agent": random.choice(user_agents),
            "viewport": random.choice(viewports),
            "timezone": random.choice(["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"]),
            "language": "en-US,en;q=0.9",
            "platform": random.choice(["Win32", "MacIntel", "Linux x86_64"])
        }
    
    def create_stealth_driver(self, profile_name: str) -> Optional[uc.Chrome]:
        """Create undetected Chrome driver with stealth configuration"""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium not available. Install: pip install undetected-chromedriver selenium")
            return None
        
        try:
            profile = self.generate_realistic_profile()
            profile_path = self.profile_dir / profile_name
            profile_path.mkdir(exist_ok=True)
            
            options = uc.ChromeOptions()
            
            # Stealth options
            options.add_argument(f"--user-data-dir={profile_path}")
            options.add_argument(f"--user-agent={profile['user_agent']}")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-extensions-except")
            options.add_argument("--disable-plugins-discovery")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Remote debugging
            debug_port = self.remote_debugging_port + len(self.active_drivers)
            options.add_argument(f"--remote-debugging-port={debug_port}")
            
            # Create driver
            driver = uc.Chrome(options=options, version_main=None)
            
            # Execute stealth scripts
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": profile['user_agent'],
                "acceptLanguage": profile['language'],
                "platform": profile['platform']
            })
            
            # Set viewport
            driver.set_window_size(profile['viewport']['width'], profile['viewport']['height'])
            
            self.active_drivers[profile_name] = {
                "driver": driver,
                "profile": profile,
                "debug_port": debug_port,
                "created_at": datetime.now()
            }
            
            print(f"✅ Created stealth driver for profile: {profile_name}")
            return driver
            
        except Exception as e:
            print(f"❌ Failed to create stealth driver: {e}")
            return None
    
    def perform_smart_login(self, driver: uc.Chrome, username: str, password: str) -> bool:
        """Perform human-like login with anti-detection measures"""
        try:
            print("🔐 Starting smart login process...")
            
            # Navigate to login page
            driver.get(f"{self.base_url}/Login.aspx")
            
            # Wait for page load with random delay
            time.sleep(random.uniform(2, 4))
            
            # Human-like typing simulation
            def human_type(element, text):
                for char in text:
                    element.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.15))
            
            # Find and fill username
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "txtUserName"))
            )
            
            # Simulate human behavior
            username_field.click()
            time.sleep(random.uniform(0.5, 1.0))
            human_type(username_field, username)
            
            # Random pause
            time.sleep(random.uniform(1, 2))
            
            # Find and fill password
            password_field = driver.find_element(By.NAME, "txtPassword")
            password_field.click()
            time.sleep(random.uniform(0.5, 1.0))
            human_type(password_field, password)
            
            # Random pause before submit
            time.sleep(random.uniform(1, 2))
            
            # Submit form
            submit_button = driver.find_element(By.NAME, "btnSubmit")
            submit_button.click()
            
            # Wait for redirect or error
            time.sleep(random.uniform(3, 5))
            
            # Check if login successful
            if "main_page.aspx" in driver.current_url or "Main.aspx" in driver.current_url:
                print("✅ Login successful!")
                return True
            else:
                print("❌ Login failed - checking for errors...")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def extract_session_data(self, driver: uc.Chrome) -> Dict:
        """Extract comprehensive session data"""
        try:
            cookies = driver.get_cookies()
            
            # Get local storage and session storage
            local_storage = driver.execute_script("return window.localStorage;")
            session_storage = driver.execute_script("return window.sessionStorage;")
            
            # Extract authentication tokens
            auth_tokens = {}
            for cookie in cookies:
                if any(keyword in cookie['name'].lower() for keyword in 
                      ['session', 'auth', 'token', 'login', 'asp.net']):
                    auth_tokens[cookie['name']] = cookie['value']
            
            # Get current fingerprint
            fingerprint = self.generate_browser_fingerprint(driver)
            
            return {
                "cookies": cookies,
                "local_storage": local_storage,
                "session_storage": session_storage,
                "auth_tokens": auth_tokens,
                "fingerprint": fingerprint,
                "user_agent": driver.execute_script("return navigator.userAgent;"),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to extract session data: {e}")
            return {}
    
    def generate_browser_fingerprint(self, driver: uc.Chrome) -> str:
        """Generate unique browser fingerprint"""
        try:
            fingerprint_data = driver.execute_script("""
                return {
                    userAgent: navigator.userAgent,
                    language: navigator.language,
                    platform: navigator.platform,
                    screen: screen.width + 'x' + screen.height,
                    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
                    webgl: (function() {
                        try {
                            var canvas = document.createElement('canvas');
                            var gl = canvas.getContext('webgl');
                            return gl.getParameter(gl.RENDERER);
                        } catch(e) { return 'unavailable'; }
                    })(),
                    plugins: Array.from(navigator.plugins).map(p => p.name).join(',')
                }
            """)
            
            fingerprint_string = json.dumps(fingerprint_data, sort_keys=True)
            return hashlib.md5(fingerprint_string.encode()).hexdigest()
            
        except Exception as e:
            print(f"❌ Fingerprint generation failed: {e}")
            return "unknown"
    
    def save_session(self, profile_name: str, session_data: Dict, credentials: Dict = None):
        """Save session to database"""
        conn = sqlite3.connect(self.session_db)
        cursor = conn.cursor()
        
        # Calculate expiry time (24 hours from now)
        expiry_time = datetime.now() + timedelta(hours=24)
        
        cursor.execute('''
            INSERT OR REPLACE INTO sessions 
            (profile_name, cookies, session_tokens, user_agent, viewport, 
             created_at, last_used, expiry_time, status, login_credentials, fingerprint)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile_name,
            json.dumps(session_data.get('cookies', [])),
            json.dumps(session_data.get('auth_tokens', {})),
            session_data.get('user_agent', ''),
            json.dumps(session_data.get('viewport', {})),
            datetime.now(),
            datetime.now(),
            expiry_time,
            'active',
            json.dumps(credentials) if credentials else None,
            session_data.get('fingerprint', '')
        ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 Session saved: {profile_name}")
    
    def load_existing_sessions(self):
        """Load existing sessions from database"""
        conn = sqlite3.connect(self.session_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT profile_name, cookies, session_tokens, user_agent, expiry_time, status
            FROM sessions 
            WHERE status = 'active' AND expiry_time > ?
        ''', (datetime.now(),))
        
        sessions = cursor.fetchall()
        
        for session in sessions:
            profile_name, cookies, tokens, user_agent, expiry, status = session
            self.session_pool.append({
                "profile_name": profile_name,
                "cookies": json.loads(cookies),
                "tokens": json.loads(tokens),
                "user_agent": user_agent,
                "expiry": expiry
            })
        
        conn.close()
        print(f"📂 Loaded {len(self.session_pool)} existing sessions")
    
    def test_session_validity(self, session_data: Dict) -> bool:
        """Test if a session is still valid"""
        try:
            session = requests.Session()
            
            # Set cookies
            for cookie in session_data['cookies']:
                session.cookies.set(cookie['name'], cookie['value'], domain=cookie.get('domain'))
            
            # Set headers
            session.headers.update({
                'User-Agent': session_data['user_agent'],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive'
            })
            
            # Test with load board API
            response = session.get(f"{self.base_url}/II14_managepostedloads.asp", timeout=10)
            
            # Check if we get valid response (not redirected to login)
            if response.status_code == 200 and 'Login.aspx' not in response.url:
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Session validation failed: {e}")
            return False
    
    def get_valid_session(self) -> Optional[Dict]:
        """Get a valid session from the pool"""
        for session in self.session_pool:
            if self.test_session_validity(session):
                print(f"✅ Found valid session: {session['profile_name']}")
                return session
        
        print("⚠️  No valid sessions found in pool")
        return None
    
    def refresh_session(self, profile_name: str, credentials: Dict) -> Optional[Dict]:
        """Refresh a session using stored credentials"""
        try:
            driver = self.create_stealth_driver(f"{profile_name}_refresh")
            
            if not driver:
                return None
            
            # Perform login
            if self.perform_smart_login(driver, credentials['username'], credentials['password']):
                # Extract new session data
                session_data = self.extract_session_data(driver)
                
                # Save updated session
                self.save_session(profile_name, session_data, credentials)
                
                # Clean up
                driver.quit()
                
                return session_data
            
            driver.quit()
            return None
            
        except Exception as e:
            print(f"❌ Session refresh failed: {e}")
            return None
    
    def create_new_session(self, username: str, password: str, profile_name: str = None) -> Optional[Dict]:
        """Create a completely new session"""
        if not profile_name:
            profile_name = f"profile_{int(time.time())}"
        
        try:
            print(f"🔄 Creating new session: {profile_name}")
            
            driver = self.create_stealth_driver(profile_name)
            if not driver:
                return None
            
            # Perform login
            if self.perform_smart_login(driver, username, password):
                # Navigate to load board to establish full session
                driver.get(f"{self.base_url}/II14_managepostedloads.asp")
                time.sleep(random.uniform(2, 4))
                
                # Extract session data
                session_data = self.extract_session_data(driver)
                
                # Save session
                credentials = {"username": username, "password": password}
                self.save_session(profile_name, session_data, credentials)
                
                # Add to session pool
                session_data['profile_name'] = profile_name
                self.session_pool.append(session_data)
                
                print(f"✅ New session created successfully: {profile_name}")
                
                # Keep driver alive for continuous use
                # driver.quit()  # Comment out to keep persistent
                
                return session_data
            
            driver.quit()
            return None
            
        except Exception as e:
            print(f"❌ Failed to create new session: {e}")
            return None
    
    def get_session_for_scraper(self, username: str = None, password: str = None) -> Optional[str]:
        """Get a valid session cookie string for the scraper"""
        # Try to get existing valid session
        session = self.get_valid_session()
        
        if not session and username and password:
            # Create new session if credentials provided
            session = self.create_new_session(username, password)
        
        if session:
            # Convert cookies to string format for scraper
            cookie_string = "; ".join([f"{c['name']}={c['value']}" for c in session['cookies']])
            return cookie_string
        
        return None
    
    def start_session_monitor(self, check_interval: int = 3600):
        """Start background thread to monitor and refresh sessions"""
        def monitor_loop():
            while True:
                try:
                    print("🔍 Monitoring session health...")
                    
                    # Check each session in pool
                    for session in self.session_pool[:]:  # Copy list to avoid modification during iteration
                        if not self.test_session_validity(session):
                            print(f"⚠️  Session expired: {session['profile_name']}")
                            
                            # Try to refresh if credentials available
                            conn = sqlite3.connect(self.session_db)
                            cursor = conn.cursor()
                            cursor.execute(
                                'SELECT login_credentials FROM sessions WHERE profile_name = ?',
                                (session['profile_name'],)
                            )
                            result = cursor.fetchone()
                            conn.close()
                            
                            if result and result[0]:
                                credentials = json.loads(result[0])
                                print(f"🔄 Attempting to refresh session: {session['profile_name']}")
                                
                                new_session = self.refresh_session(session['profile_name'], credentials)
                                if new_session:
                                    # Update session pool
                                    self.session_pool.remove(session)
                                    new_session['profile_name'] = session['profile_name']
                                    self.session_pool.append(new_session)
                                    print(f"✅ Session refreshed: {session['profile_name']}")
                    
                    print(f"💤 Session monitor sleeping for {check_interval/3600:.1f} hours...")
                    time.sleep(check_interval)
                    
                except Exception as e:
                    print(f"❌ Session monitor error: {e}")
                    time.sleep(60)  # Short sleep on error
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        print("🔄 Session monitor started")
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions and drivers"""
        try:
            # Clean up database
            conn = sqlite3.connect(self.session_db)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE expiry_time < ?', (datetime.now(),))
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            # Clean up session pool
            self.session_pool = [s for s in self.session_pool if 
                               datetime.fromisoformat(s.get('expiry', '1970-01-01')) > datetime.now()]
            
            # Clean up active drivers
            for profile_name, driver_data in list(self.active_drivers.items()):
                try:
                    driver_data['driver'].quit()
                except:
                    pass
                del self.active_drivers[profile_name]
            
            print(f"🧹 Cleaned up {deleted_count} expired sessions")
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")

def main():
    """Demo of the Advanced Session Manager"""
    manager = AdvancedSessionManager()
    
    print("🔐 Advanced Persistent Session Manager")
    print("=" * 50)
    
    # Example usage
    username = input("Enter Sylectus username: ").strip()
    password = input("Enter Sylectus password: ").strip()
    
    if username and password:
        # Create new session
        session = manager.create_new_session(username, password)
        
        if session:
            print("✅ Session created successfully!")
            
            # Start monitoring
            manager.start_session_monitor()
            
            # Get cookie string for scraper
            cookie_string = manager.get_session_for_scraper()
            print(f"🍪 Cookie string: {cookie_string[:100]}...")
            
            print("🔄 Session manager running. Press Ctrl+C to stop.")
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
                manager.cleanup_expired_sessions()
        else:
            print("❌ Failed to create session")
    else:
        print("❌ Username and password required")

if __name__ == "__main__":
    main()