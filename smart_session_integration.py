#!/usr/bin/env python3
"""
Smart Session Integration - Connects persistent session management with the scraper
Automatically maintains sessions and provides fresh cookies to the API scraper
"""

import os
import time
import json
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

from persistent_session_manager import AdvancedSessionManager
from stealth_session_keeper import StealthSessionKeeper

class SmartSessionIntegration:
    def __init__(self, username: str = None, password: str = None):
        self.username = username
        self.password = password
        self.session_manager = AdvancedSessionManager()
        self.stealth_keeper = StealthSessionKeeper()
        self.monitoring_active = False
        self.last_cookie_update = None
        
        # Load credentials from environment if not provided
        if not self.username:
            self.username = os.getenv('SYLECTUS_USERNAME')
        if not self.password:
            self.password = os.getenv('SYLECTUS_PASSWORD')
    
    def get_fresh_cookies(self) -> str:
        """Get fresh valid cookies from the best available source"""
        print("🔍 Searching for valid session cookies...")
        
        # Strategy 1: Try existing valid sessions
        cookie_string = self.session_manager.get_session_for_scraper()
        if cookie_string and self.validate_cookie_string(cookie_string):
            print("✅ Found valid session from session manager")
            return cookie_string
        
        # Strategy 2: Try stealth keeper sessions
        best_session = self.stealth_keeper.get_best_session()
        if best_session:
            cookie_string = self.stealth_keeper.get_session_cookies(best_session)
            if cookie_string and self.validate_cookie_string(cookie_string):
                print("✅ Found valid session from stealth keeper")
                return cookie_string
        
        # Strategy 3: Create new session if credentials available
        if self.username and self.password:
            print("🔄 Creating new session...")
            session = self.session_manager.create_new_session(self.username, self.password)
            if session:
                cookie_string = self.session_manager.get_session_for_scraper()
                if cookie_string:
                    print("✅ Created new valid session")
                    return cookie_string
        
        print("❌ Unable to obtain valid cookies")
        return None
    
    def validate_cookie_string(self, cookie_string: str) -> bool:
        """Validate cookie string by testing API access"""
        try:
            import requests
            
            headers = {
                'Cookie': cookie_string,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            }
            
            response = requests.get(
                'https://www.sylectus.com/II14_managepostedloads.asp',
                headers=headers,
                timeout=10
            )
            
            return response.status_code == 200 and 'Login.aspx' not in response.url
            
        except Exception as e:
            print(f"⚠️ Cookie validation failed: {e}")
            return False
    
    def update_scraper_cookies(self, cookie_string: str):
        """Update the .env file with fresh cookies"""
        try:
            env_file = Path("/opt/sylectus-scraper/.env")
            local_env = Path(".env")
            
            # Read existing env content
            env_content = []
            if local_env.exists():
                with open(local_env, 'r') as f:
                    env_content = f.readlines()
            
            # Update SYLECTUS_COOKIE line
            updated = False
            for i, line in enumerate(env_content):
                if line.startswith('SYLECTUS_COOKIE='):
                    env_content[i] = f'SYLECTUS_COOKIE="{cookie_string}"\n'
                    updated = True
                    break
            
            # Add if not found
            if not updated:
                env_content.append(f'SYLECTUS_COOKIE="{cookie_string}"\n')
            
            # Ensure other required variables exist
            required_vars = {
                'TELEGRAM_BOT_TOKEN': '6331983207:AAEzrXpH7ISNP7dz9ZgXBfBadE6TpDxWwLw',
                'TELEGRAM_CHAT_ID': '6547104920',
                'CHECK_INTERVAL': '120'
            }
            
            for var, default in required_vars.items():
                found = any(line.startswith(f'{var}=') for line in env_content)
                if not found:
                    env_content.append(f'{var}={default}\n')
            
            # Write local .env
            with open(local_env, 'w') as f:
                f.writelines(env_content)
            
            # Upload to server if SSH key available
            ssh_key = Path("~/.ssh/sylectus_key").expanduser()
            if ssh_key.exists():
                try:
                    subprocess.run([
                        'scp', '-i', str(ssh_key), 
                        str(local_env), 
                        'root@157.245.242.222:/opt/sylectus-scraper/.env'
                    ], check=True, timeout=30)
                    
                    print("✅ Updated scraper .env file on server")
                    self.last_cookie_update = datetime.now()
                    
                except subprocess.SubprocessError as e:
                    print(f"⚠️ Failed to upload .env to server: {e}")
            
        except Exception as e:
            print(f"❌ Failed to update cookies: {e}")
    
    def restart_scraper(self):
        """Restart the scraper process on the server"""
        try:
            ssh_key = Path("~/.ssh/sylectus_key").expanduser()
            if not ssh_key.exists():
                print("⚠️ SSH key not found, cannot restart scraper")
                return False
            
            # Kill existing scraper
            subprocess.run([
                'ssh', '-i', str(ssh_key),
                'root@157.245.242.222',
                'pkill -f api_scraper'
            ], timeout=30)
            
            time.sleep(2)
            
            # Start new scraper
            subprocess.run([
                'ssh', '-i', str(ssh_key),
                'root@157.245.242.222',
                'cd /opt/sylectus-scraper && nohup python3 api_scraper.py --startup > /tmp/scraper.log 2>&1 &'
            ], timeout=30)
            
            print("🔄 Scraper restarted with fresh cookies")
            return True
            
        except Exception as e:
            print(f"❌ Failed to restart scraper: {e}")
            return False
    
    def monitor_and_refresh(self, check_interval: int = 7200):  # 2 hours
        """Monitor sessions and refresh as needed"""
        print(f"👁️ Starting session monitor (checking every {check_interval/3600:.1f} hours)")
        
        while self.monitoring_active:
            try:
                print(f"\n🔍 Session health check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Check if current scraper is working
                scraper_working = self.check_scraper_health()
                
                if not scraper_working:
                    print("⚠️ Scraper appears to be having issues, refreshing session...")
                    
                    # Get fresh cookies
                    fresh_cookies = self.get_fresh_cookies()
                    
                    if fresh_cookies:
                        # Update scraper with fresh cookies
                        self.update_scraper_cookies(fresh_cookies)
                        
                        # Restart scraper
                        if self.restart_scraper():
                            print("✅ Scraper refreshed successfully")
                        else:
                            print("❌ Failed to restart scraper")
                    else:
                        print("❌ Could not obtain fresh cookies")
                        self.send_alert("Cookie refresh failed - manual intervention needed")
                else:
                    print("✅ Scraper appears to be working normally")
                
                # Maintain session pools
                self.session_manager.cleanup_expired_sessions()
                self.stealth_keeper.maintain_sessions()
                
                print(f"💤 Sleeping for {check_interval/3600:.1f} hours...")
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(300)  # 5 minute error delay
    
    def check_scraper_health(self) -> bool:
        """Check if the scraper is working properly"""
        try:
            ssh_key = Path("~/.ssh/sylectus_key").expanduser()
            if not ssh_key.exists():
                return True  # Can't check, assume it's working
            
            # Check if process is running
            result = subprocess.run([
                'ssh', '-i', str(ssh_key),
                'root@157.245.242.222',
                'ps aux | grep api_scraper | grep -v grep'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print("⚠️ Scraper process not running")
                return False
            
            # Check recent log activity
            log_result = subprocess.run([
                'ssh', '-i', str(ssh_key),
                'root@157.245.242.222',
                'tail -20 /tmp/scraper.log | grep -E "(Found|loads|API call successful)" | tail -5'
            ], capture_output=True, text=True, timeout=30)
            
            if "Found 0 total loads" in log_result.stdout:
                print("⚠️ Scraper finding 0 loads - possible session issue")
                return False
            
            if "API call successful" in log_result.stdout:
                print("✅ Recent API activity detected")
                return True
            
            # If no recent activity, consider it potentially problematic
            print("⚠️ No recent scraper activity detected")
            return False
            
        except Exception as e:
            print(f"⚠️ Health check error: {e}")
            return True  # Assume it's working if we can't check
    
    def send_alert(self, message: str):
        """Send alert via Telegram"""
        try:
            import requests
            
            bot_token = "6331983207:AAEzrXpH7ISNP7dz9ZgXBfBadE6TpDxWwLw"
            chat_id = "6547104920"
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': f"🚨 SESSION ALERT\n\n{message}\n\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                'parse_mode': 'HTML'
            }
            
            requests.post(url, json=payload, timeout=10)
            print("📱 Alert sent via Telegram")
            
        except Exception as e:
            print(f"❌ Failed to send alert: {e}")
    
    def start_monitoring(self):
        """Start the monitoring system"""
        if self.monitoring_active:
            print("⚠️ Monitoring already active")
            return
        
        self.monitoring_active = True
        
        # Start session manager monitoring
        self.session_manager.start_session_monitor()
        
        # Start our integration monitoring
        monitor_thread = threading.Thread(target=self.monitor_and_refresh, daemon=True)
        monitor_thread.start()
        
        print("🚀 Smart session integration monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_active = False
        print("🛑 Monitoring stopped")
    
    def manual_refresh(self):
        """Manually refresh the scraper session"""
        print("🔄 Manual session refresh initiated...")
        
        fresh_cookies = self.get_fresh_cookies()
        if fresh_cookies:
            self.update_scraper_cookies(fresh_cookies)
            if self.restart_scraper():
                print("✅ Manual refresh completed successfully")
                return True
        
        print("❌ Manual refresh failed")
        return False

def main():
    """Main function for smart session integration"""
    print("🧠 Smart Session Integration System")
    print("=" * 50)
    
    # Check if credentials are available
    username = os.getenv('SYLECTUS_USERNAME')
    password = os.getenv('SYLECTUS_PASSWORD')
    
    if not username or not password:
        print("⚠️ SYLECTUS_USERNAME and SYLECTUS_PASSWORD environment variables not set")
        print("Please set them or provide credentials manually")
        username = input("Username (or press Enter to skip): ").strip()
        password = input("Password (or press Enter to skip): ").strip()
    
    # Initialize integration
    integration = SmartSessionIntegration(username, password)
    
    print("\n📋 Available actions:")
    print("1. Get fresh cookies")
    print("2. Manual refresh scraper")
    print("3. Start monitoring")
    print("4. Check scraper health")
    
    while True:
        try:
            choice = input("\nEnter choice (1-4) or 'q' to quit: ").strip()
            
            if choice == 'q':
                integration.stop_monitoring()
                break
            elif choice == '1':
                cookies = integration.get_fresh_cookies()
                if cookies:
                    print(f"🍪 Fresh cookies: {cookies[:100]}...")
            elif choice == '2':
                integration.manual_refresh()
            elif choice == '3':
                integration.start_monitoring()
                print("🔄 Monitoring started. Press Ctrl+C to stop.")
                try:
                    while True:
                        time.sleep(60)
                except KeyboardInterrupt:
                    integration.stop_monitoring()
                    print("\n👋 Monitoring stopped")
            elif choice == '4':
                health = integration.check_scraper_health()
                print(f"📊 Scraper health: {'✅ Good' if health else '❌ Issues detected'}")
            else:
                print("❌ Invalid choice")
                
        except KeyboardInterrupt:
            integration.stop_monitoring()
            print("\n👋 Exiting...")
            break

if __name__ == "__main__":
    main()