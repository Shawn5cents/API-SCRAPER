#!/usr/bin/env python3
"""
Thunderbird Email Monitor - Monitor for load emails
Simple approach using Thunderbird's saved emails or manual import
"""

import os
import re
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

class ThunderbirdLoadMonitor:
    def __init__(self):
        self.watch_folder = "email_loads"  # Folder to watch for saved emails
        self.processed_files = set()
        
        # Create watch folder if it doesn't exist
        if not os.path.exists(self.watch_folder):
            os.makedirs(self.watch_folder)
            
        print(f"📧 Thunderbird Load Monitor initialized")
        print(f"📁 Watching folder: {self.watch_folder}")
        print("💡 Save load emails as .eml files in this folder!")

    def extract_load_from_eml(self, file_path):
        """Extract load information from .eml file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Basic email parsing
            load_info = {
                'source': 'thunderbird_email',
                'file': os.path.basename(file_path),
                'found_time': datetime.now().strftime("%H:%M:%S"),
                'pickup_location': 'Unknown',
                'delivery_location': 'Unknown',
                'pickup_date': 'Unknown',
                'miles': '0',
                'rate': '0',
                'company': 'Unknown',
                'email': 'Unknown',
                'vehicle_type': 'VAN',
                'weight': '0',
                'pieces': '0'
            }

            # Extract sender
            from_match = re.search(r'From:.*?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', content)
            if from_match:
                load_info['email'] = from_match.group(1)
                # Try to extract company from email domain
                domain = from_match.group(1).split('@')[1]
                load_info['company'] = domain.split('.')[0].upper()

            # Extract subject
            subject_match = re.search(r'Subject: (.+)', content)
            subject = subject_match.group(1) if subject_match else ""

            # Extract locations (state codes)
            pickup_matches = re.findall(r'\b([A-Z]{2})\s*(?:to|TO|-|→)\s*([A-Z]{2})\b', content)
            if pickup_matches:
                load_info['pickup_location'] = pickup_matches[0][0]
                load_info['delivery_location'] = pickup_matches[0][1]

            # Alternative location extraction
            if load_info['pickup_location'] == 'Unknown':
                locations = re.findall(r'\b[A-Z]{2}\b', content)
                if len(locations) >= 2:
                    load_info['pickup_location'] = locations[0]
                    load_info['delivery_location'] = locations[1]

            # Extract miles
            miles_patterns = [
                r'(\d+)\s*(?:miles|mi\b)',
                r'(\d+)\s*mile',
                r'miles?:?\s*(\d+)',
            ]
            for pattern in miles_patterns:
                miles_match = re.search(pattern, content, re.IGNORECASE)
                if miles_match:
                    load_info['miles'] = miles_match.group(1)
                    break

            # Extract rate/money
            rate_patterns = [
                r'\$(\d+(?:\.\d{2})?)',
                r'(\d+)\s*dollars',
                r'rate.*?(\d+)',
            ]
            for pattern in rate_patterns:
                rate_match = re.search(pattern, content, re.IGNORECASE)
                if rate_match:
                    load_info['rate'] = rate_match.group(1)
                    break

            # Extract weight
            weight_match = re.search(r'(\d+)\s*(?:lbs|pounds|#)', content, re.IGNORECASE)
            if weight_match:
                load_info['weight'] = weight_match.group(1)

            # Extract pieces
            pieces_match = re.search(r'(\d+)\s*(?:pieces|pcs|pc)', content, re.IGNORECASE)
            if pieces_match:
                load_info['pieces'] = pieces_match.group(1)

            # Detect vehicle type
            content_lower = content.lower()
            if 'cargo van' in content_lower:
                load_info['vehicle_type'] = 'CARGO VAN'
            elif 'sprinter' in content_lower:
                load_info['vehicle_type'] = 'SPRINTER'
            elif 'expedite' in content_lower:
                load_info['vehicle_type'] = 'EXPEDITED VAN'

            # Extract date
            date_patterns = [
                r'(\d{1,2}/\d{1,2}/\d{4})',
                r'(\d{1,2}-\d{1,2}-\d{4})',
            ]
            for pattern in date_patterns:
                date_match = re.search(pattern, content)
                if date_match:
                    load_info['pickup_date'] = date_match.group(1)
                    break

            return load_info

        except Exception as e:
            print(f"❌ Error parsing {file_path}: {e}")
            return None

    def is_valid_load(self, load_info):
        """Check if extracted info looks like a real load"""
        if not load_info:
            return False
            
        # Must have basic info
        required_fields = ['pickup_location', 'delivery_location']
        for field in required_fields:
            if load_info[field] == 'Unknown':
                return False
                
        # Must have either miles or rate
        if load_info['miles'] == '0' and load_info['rate'] == '0':
            return False
            
        return True

    def send_email_load_to_telegram(self, load_info):
        """Send email load to Telegram with bidding options"""
        try:
            # Calculate per-mile rate if possible
            per_mile = "?"
            if load_info['miles'] != '0' and load_info['rate'] != '0':
                try:
                    per_mile = f"${float(load_info['rate'])/float(load_info['miles']):.2f}"
                except:
                    per_mile = "?"

            message = f"""📧 NEW EMAIL LOAD - {load_info['vehicle_type']}

🏢 Company: {load_info['company']}
📧 Email: {load_info['email']}

📍 PICKUP: {load_info['pickup_location']}
📍 DELIVERY: {load_info['delivery_location']}
📅 Date: {load_info['pickup_date']}

🚛 DETAILS:
📏 Miles: {load_info['miles']}
📦 Pieces: {load_info['pieces']}
⚖️ Weight: {load_info['weight']} lbs

💰 Rate: ${load_info['rate']}
💵 Per Mile: {per_mile}/mi

⏰ Found: {load_info['found_time']}
📨 Source: Email ({load_info['file']})

🎯 This load was sent directly to your email!"""

            # Create simple keyboard for email loads
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "📧 Reply to Email", "callback_data": f"reply_{load_info['file']}"},
                        {"text": "📞 Call Company", "callback_data": f"call_{load_info['email']}"}
                    ],
                    [
                        {"text": "✅ Mark Interested", "callback_data": f"interest_{load_info['file']}"},
                        {"text": "❌ Skip Load", "callback_data": f"skip_{load_info['file']}"}
                    ]
                ]
            }

            # Clean message and send
            clean_message = message.encode('utf-8', 'ignore').decode('utf-8')
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': clean_message[:4096],
                'parse_mode': None,
                'reply_markup': json.dumps(keyboard)
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Email load sent to Telegram: {load_info['file']}")
                return True
            else:
                print(f"❌ Telegram error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending email load: {e}")
            return False

    def check_for_new_emails(self):
        """Check watch folder for new .eml files"""
        new_files = []
        
        try:
            for filename in os.listdir(self.watch_folder):
                if filename.endswith('.eml') and filename not in self.processed_files:
                    file_path = os.path.join(self.watch_folder, filename)
                    new_files.append(file_path)
                    
        except Exception as e:
            print(f"❌ Error checking folder: {e}")
            
        return new_files

    def process_new_email(self, file_path):
        """Process a single new email file"""
        filename = os.path.basename(file_path)
        print(f"📧 Processing: {filename}")
        
        # Extract load information
        load_info = self.extract_load_from_eml(file_path)
        
        if not load_info:
            print(f"❌ Could not parse: {filename}")
            self.processed_files.add(filename)
            return False
            
        if not self.is_valid_load(load_info):
            print(f"⚠️  Not a valid load: {filename}")
            self.processed_files.add(filename)
            return False
            
        print(f"✅ Valid load found: {load_info['pickup_location']} → {load_info['delivery_location']}")
        
        # Send to Telegram
        success = self.send_email_load_to_telegram(load_info)
        
        # Mark as processed
        self.processed_files.add(filename)
        
        return success

    def start_monitoring(self):
        """Start monitoring for email files"""
        print(f"🚀 Starting Thunderbird email monitoring...")
        print(f"📁 Watching: {os.path.abspath(self.watch_folder)}")
        print("💡 To use: Save load emails as .eml files in the watch folder")
        print("⏰ Checking every 30 seconds...")
        
        while True:
            try:
                # Check for new files
                new_files = self.check_for_new_emails()
                
                if new_files:
                    print(f"📬 Found {len(new_files)} new email(s)")
                    
                    for file_path in new_files:
                        self.process_new_email(file_path)
                        time.sleep(1)  # Small delay between processing
                else:
                    print(f"📭 No new emails at {datetime.now().strftime('%H:%M:%S')}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                print("\n👋 Email monitoring stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(30)

def main():
    print("📧 THUNDERBIRD EMAIL LOAD MONITOR")
    print("=" * 50)
    
    monitor = ThunderbirdLoadMonitor()
    
    print(f"\n📁 Watch folder created: {monitor.watch_folder}")
    print("\n🔧 How to use:")
    print("1. When you receive load emails in Thunderbird")
    print("2. Right-click → 'Save As' → Save as .eml file")  
    print(f"3. Save to: {os.path.abspath(monitor.watch_folder)}")
    print("4. This monitor will automatically process them!")
    print()
    
    choice = input("Start monitoring now? (y/n): ").lower()
    if choice == 'y':
        monitor.start_monitoring()
    else:
        print("📧 Monitor ready! Run when you want to start watching.")

if __name__ == "__main__":
    main()