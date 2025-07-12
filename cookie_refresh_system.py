#!/usr/bin/env python3
"""
Automatic Cookie Refresh System for Sylectus Scraper
Monitors cookie expiration and provides alerts for manual refresh
"""
import os
import re
import time
import datetime
import requests
import subprocess
from pathlib import Path

class CookieMonitor:
    def __init__(self, cookie_file_path="/opt/sylectus-scraper/.env"):
        self.cookie_file = cookie_file_path
        self.server_ip = "157.245.242.222"
        self.ssh_key = "~/.ssh/sylectus_key"
        self.check_interval = 3600  # Check every hour
        self.warning_hours = 2  # Warn when 2 hours left
        
    def extract_cookie_from_env(self, env_file):
        """Extract SYLECTUS_COOKIE from .env file"""
        try:
            with open(env_file, 'r') as f:
                content = f.read()
            
            # Find SYLECTUS_COOKIE line
            match = re.search(r'SYLECTUS_COOKIE=["\'](.*?)["\']', content)
            if match:
                return match.group(1)
            
            print(f"⚠️  No SYLECTUS_COOKIE found in {env_file}")
            return None
            
        except FileNotFoundError:
            print(f"❌ Cookie file not found: {env_file}")
            return None
    
    def test_cookie_validity(self, cookie_string):
        """Test if cookie is still valid by making API call"""
        headers = {
            'Cookie': cookie_string,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        try:
            # Test with Sylectus load board API
            response = requests.get(
                'https://www.sylectus.com/Load.aspx',
                headers=headers,
                timeout=10
            )
            
            # Check if we're redirected to login page
            if 'Login.aspx' in response.url or response.status_code == 401:
                return False, "Redirected to login - cookie expired"
            
            if response.status_code == 200:
                return True, "Cookie valid"
            
            return False, f"HTTP {response.status_code}"
            
        except Exception as e:
            return False, f"Network error: {str(e)}"
    
    def get_cookie_age(self, env_file):
        """Get age of cookie file in hours"""
        try:
            stat = os.stat(env_file)
            age_seconds = time.time() - stat.st_mtime
            age_hours = age_seconds / 3600
            return age_hours
        except:
            return None
    
    def send_telegram_alert(self, message):
        """Send alert via Telegram (using scraper's bot config)"""
        try:
            # Get telegram config from server
            result = subprocess.run([
                'ssh', '-i', os.path.expanduser(self.ssh_key), 
                f'root@{self.server_ip}',
                'grep -E "TELEGRAM_BOT_TOKEN|TELEGRAM_CHAT_ID" /opt/sylectus-scraper/.env'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                print("⚠️  Could not get Telegram config")
                return
            
            # Parse config
            config = {}
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value
            
            bot_token = config.get('TELEGRAM_BOT_TOKEN')
            chat_id = config.get('TELEGRAM_CHAT_ID')
            
            if not bot_token or not chat_id:
                print("⚠️  Telegram config incomplete")
                return
            
            # Send message
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': f"🍪 COOKIE ALERT\n\n{message}",
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                print("✅ Telegram alert sent")
            else:
                print(f"❌ Telegram alert failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Telegram alert error: {e}")
    
    def check_server_cookie_status(self):
        """Check cookie status on remote server"""
        try:
            # Get cookie file from server
            result = subprocess.run([
                'ssh', '-i', os.path.expanduser(self.ssh_key),
                f'root@{self.server_ip}',
                f'cat {self.cookie_file}'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return False, "Could not read cookie file on server"
            
            cookie = self.extract_cookie_from_env_content(result.stdout)
            if not cookie:
                return False, "No valid cookie found on server"
            
            # Test cookie validity
            valid, reason = self.test_cookie_validity(cookie)
            
            # Get cookie age
            age_result = subprocess.run([
                'ssh', '-i', os.path.expanduser(self.ssh_key),
                f'root@{self.server_ip}',
                f'stat -c %Y {self.cookie_file}'
            ], capture_output=True, text=True)
            
            age_hours = None
            if age_result.returncode == 0:
                try:
                    mtime = int(age_result.stdout.strip())
                    age_seconds = time.time() - mtime
                    age_hours = age_seconds / 3600
                except:
                    pass
            
            return valid, {
                'reason': reason,
                'age_hours': age_hours,
                'cookie_present': True
            }
            
        except Exception as e:
            return False, f"Server check error: {str(e)}"
    
    def extract_cookie_from_env_content(self, content):
        """Extract cookie from .env file content"""
        match = re.search(r'SYLECTUS_COOKIE=["\'](.*?)["\']', content)
        return match.group(1) if match else None
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print("🍪 Cookie Refresh Monitor Started")
        print(f"📊 Checking every {self.check_interval/3600:.1f} hours")
        print(f"⚠️  Warning threshold: {self.warning_hours} hours")
        print("=" * 50)
        
        while True:
            try:
                print(f"\n🔍 Cookie Status Check - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                valid, details = self.check_server_cookie_status()
                
                if valid:
                    age = details.get('age_hours', 0)
                    print(f"✅ Cookie valid (age: {age:.1f} hours)")
                    
                    # Check if cookie is getting old (warn after 20 hours)
                    if age > 20:
                        message = f"""
Cookie is getting old and may expire soon.

🕐 Cookie Age: {age:.1f} hours
⚠️  Recommended: Refresh cookies manually

📋 Steps to refresh:
1. Run: python3 capture_cookies.py
2. Follow the manual login instructions
3. Upload new cookies to server

💻 Server: {self.server_ip}
                        """
                        print("⚠️  Cookie age warning sent")
                        self.send_telegram_alert(message)
                
                else:
                    reason = details if isinstance(details, str) else details.get('reason', 'Unknown error')
                    print(f"❌ Cookie invalid: {reason}")
                    
                    message = f"""
🚨 URGENT: Sylectus cookies have expired!

❌ Status: {reason}
🛑 Scraper Status: Not receiving loads

📋 Action Required:
1. Run: python3 capture_cookies.py  
2. Log into Sylectus manually
3. Capture fresh cookies
4. Upload to server and restart scraper

💻 Server: {self.server_ip}
⏰ Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    """
                    print("🚨 Cookie expiration alert sent")
                    self.send_telegram_alert(message)
                
                print(f"⏰ Next check in {self.check_interval/3600:.1f} hours...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n👋 Cookie monitor stopped")
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                print(f"🔄 Retrying in {self.check_interval/3600:.1f} hours...")
                time.sleep(self.check_interval)

def main():
    monitor = CookieMonitor()
    
    print("🍪 Sylectus Cookie Refresh System")
    print("=" * 40)
    print("1. Monitor cookie status")
    print("2. Check current cookie status")
    print("3. Test specific cookie")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        monitor.monitor_loop()
    elif choice == "2":
        valid, details = monitor.check_server_cookie_status()
        print(f"\n📊 Cookie Status: {'✅ Valid' if valid else '❌ Invalid'}")
        print(f"🔍 Details: {details}")
    elif choice == "3":
        cookie = input("Enter cookie string: ").strip()
        if cookie:
            valid, reason = monitor.test_cookie_validity(cookie)
            print(f"\n📊 Cookie Test: {'✅ Valid' if valid else '❌ Invalid'}")
            print(f"🔍 Reason: {reason}")
    else:
        print("❌ Invalid option")

if __name__ == "__main__":
    main()