#!/usr/bin/env python3
"""
Automated Cookie Refresh Daemon for Sylectus
Runs in background and automatically refreshes cookies before expiration
"""
import os
import time
import schedule
import subprocess
import datetime
from pathlib import Path

class AutoCookieRefresh:
    def __init__(self):
        self.server_ip = "157.245.242.222"
        self.ssh_key = os.path.expanduser("~/.ssh/sylectus_key")
        self.local_monitor = "/home/nichols-ai/sylectus-monitor/auto_monitor.py"
        
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def check_server_status(self):
        """Check if scraper is running and working"""
        try:
            # Check if process is running
            result = subprocess.run([
                'ssh', '-i', self.ssh_key, f'root@{self.server_ip}',
                'ps aux | grep api_scraper | grep -v grep'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return False, "Scraper process not running"
            
            # Check recent log for activity
            log_result = subprocess.run([
                'ssh', '-i', self.ssh_key, f'root@{self.server_ip}',
                'tail -10 /tmp/scraper.log | grep -E "(Found|loads|new)"'
            ], capture_output=True, text=True, timeout=30)
            
            if "Found 0 total loads" in log_result.stdout:
                return False, "Scraper finding 0 loads - cookies likely expired"
            
            return True, "Scraper running and active"
            
        except Exception as e:
            return False, f"Error checking status: {e}"
    
    def send_telegram_notification(self, message):
        """Send notification via Telegram"""
        try:
            # Get telegram config from server
            result = subprocess.run([
                'ssh', '-i', self.ssh_key, f'root@{self.server_ip}',
                'grep -E "TELEGRAM_BOT_TOKEN|TELEGRAM_CHAT_ID" /opt/sylectus-scraper/.env'
            ], capture_output=True, text=True, timeout=30)
            
            config = {}
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key] = value.strip('"')
            
            bot_token = config.get('TELEGRAM_BOT_TOKEN')
            chat_id = config.get('TELEGRAM_CHAT_ID')
            
            if bot_token and chat_id:
                import requests
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    'chat_id': chat_id,
                    'text': f"🤖 AUTO REFRESH\n\n{message}",
                    'parse_mode': 'HTML'
                }
                requests.post(url, json=payload, timeout=10)
                self.log("✅ Telegram notification sent")
            
        except Exception as e:
            self.log(f"❌ Telegram notification failed: {e}")
    
    def refresh_cookies_automatically(self):
        """Attempt automatic cookie refresh"""
        self.log("🔄 Starting automatic cookie refresh...")
        
        try:
            # Run auto monitor to capture fresh cookies
            self.log("🌐 Starting browser session for cookie capture...")
            
            # Start auto monitor in background
            monitor_process = subprocess.Popen([
                'python3', self.local_monitor
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for it to complete or timeout after 10 minutes
            try:
                stdout, stderr = monitor_process.communicate(timeout=600)
                
                # Check if cookies were captured
                cookie_files = list(Path('.').glob('extracted_cookies_*.env'))
                if cookie_files:
                    # Get the most recent cookie file
                    latest_cookie = max(cookie_files, key=lambda p: p.stat().st_mtime)
                    self.log(f"✅ Captured fresh cookies: {latest_cookie}")
                    
                    # Upload to server
                    self.upload_cookies_to_server(latest_cookie)
                    
                    return True
                else:
                    self.log("❌ No cookie files found after auto monitor")
                    return False
                    
            except subprocess.TimeoutExpired:
                monitor_process.kill()
                self.log("⏰ Auto monitor timed out")
                return False
                
        except Exception as e:
            self.log(f"❌ Auto refresh failed: {e}")
            return False
    
    def upload_cookies_to_server(self, cookie_file):
        """Upload fresh cookies to server and restart scraper"""
        try:
            self.log(f"📤 Uploading {cookie_file} to server...")
            
            # Add telegram config to cookie file
            with open(cookie_file, 'r') as f:
                content = f.read()
            
            if 'TELEGRAM_BOT_TOKEN' not in content:
                content += "\nTELEGRAM_BOT_TOKEN=6331983207:AAEzrXpH7ISNP7dz9ZgXBfBadE6TpDxWwLw"
                content += "\nTELEGRAM_CHAT_ID=6547104920"
                content += "\nCHECK_INTERVAL=120"
                
                with open(cookie_file, 'w') as f:
                    f.write(content)
            
            # Upload to server
            subprocess.run([
                'scp', '-i', self.ssh_key, str(cookie_file),
                f'root@{self.server_ip}:/opt/sylectus-scraper/.env'
            ], check=True, timeout=60)
            
            self.log("✅ Cookies uploaded to server")
            
            # Restart scraper
            self.log("🔄 Restarting scraper...")
            subprocess.run([
                'ssh', '-i', self.ssh_key, f'root@{self.server_ip}',
                'pkill -f api_scraper; cd /opt/sylectus-scraper && python3 api_scraper.py --startup > /tmp/scraper.log 2>&1 &'
            ], timeout=60)
            
            self.log("✅ Scraper restarted with fresh cookies")
            
            # Send success notification
            self.send_telegram_notification(
                "✅ Cookies automatically refreshed!\n"
                "🔄 Scraper restarted\n"
                "📊 Should start receiving loads again"
            )
            
            return True
            
        except Exception as e:
            self.log(f"❌ Upload failed: {e}")
            return False
    
    def manual_refresh_reminder(self):
        """Send manual refresh reminder"""
        message = """
🍪 MANUAL COOKIE REFRESH NEEDED

The automatic cookie refresh system needs your attention.

📋 Please run:
1. python3 capture_cookies.py
2. Follow browser login instructions
3. System will auto-upload fresh cookies

💻 Server: 157.245.242.222
⏰ Time: {timestamp}

The scraper will resume load notifications once cookies are refreshed.
        """.format(timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        self.send_telegram_notification(message)
        self.log("📨 Manual refresh reminder sent")
    
    def daily_health_check(self):
        """Perform daily health check"""
        self.log("🏥 Performing daily health check...")
        
        running, status = self.check_server_status()
        
        if running:
            self.log(f"✅ Health check passed: {status}")
            self.send_telegram_notification(
                f"✅ Daily Health Check\n\n"
                f"📊 Status: {status}\n"
                f"🕐 Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                f"💻 Server: {self.server_ip}"
            )
        else:
            self.log(f"❌ Health check failed: {status}")
            
            # Try automatic refresh first
            if "cookies" in status.lower() or "0 loads" in status:
                self.log("🔄 Attempting automatic cookie refresh...")
                
                if self.refresh_cookies_automatically():
                    self.log("✅ Automatic refresh successful")
                else:
                    self.log("❌ Automatic refresh failed, sending manual reminder")
                    self.manual_refresh_reminder()
            else:
                # Other issues - just notify
                self.send_telegram_notification(
                    f"❌ Daily Health Check Failed\n\n"
                    f"🚨 Issue: {status}\n"
                    f"💻 Server: {self.server_ip}\n"
                    f"🔧 Manual intervention may be required"
                )
    
    def start_daemon(self):
        """Start the background daemon"""
        self.log("🚀 Starting Auto Cookie Refresh Daemon...")
        
        # Schedule checks
        schedule.every().day.at("06:00").do(self.daily_health_check)  # Morning check
        schedule.every().day.at("18:00").do(self.daily_health_check)  # Evening check
        schedule.every(6).hours.do(self.check_and_refresh)  # Every 6 hours
        
        self.log("📅 Scheduled checks:")
        self.log("   - Daily health check: 06:00 and 18:00")
        self.log("   - Cookie refresh check: Every 6 hours")
        
        # Initial health check
        self.daily_health_check()
        
        # Main loop
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def check_and_refresh(self):
        """Check if refresh is needed and attempt it"""
        self.log("🔍 Checking if cookie refresh is needed...")
        
        running, status = self.check_server_status()
        
        if not running and ("cookies" in status.lower() or "0 loads" in status):
            self.log("🔄 Cookie refresh needed, attempting automatic refresh...")
            
            if not self.refresh_cookies_automatically():
                self.log("❌ Automatic refresh failed, sending manual reminder...")
                self.manual_refresh_reminder()
        else:
            self.log(f"✅ No refresh needed: {status}")

if __name__ == "__main__":
    daemon = AutoCookieRefresh()
    
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "check":
            daemon.daily_health_check()
        elif sys.argv[1] == "refresh":
            daemon.refresh_cookies_automatically()
        elif sys.argv[1] == "daemon":
            daemon.start_daemon()
        else:
            print("Usage: python3 cookie_auto_refresh.py [check|refresh|daemon]")
    else:
        # Default to health check
        daemon.daily_health_check()