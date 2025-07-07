#!/usr/bin/env python3
"""
API-Based Sylectus Scraper
Uses discovered API endpoints for direct data access
"""

import requests
import json
import time
import re
import os
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from enhanced_parser import SylectusLoadParser

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 120))

class SylectusAPIClient:
    def __init__(self, startup_mode=False):
        self.session = requests.Session()
        self.base_url = "https://www.sylectus.com"
        self.load_board_api = f"{self.base_url}/II14_managepostedloads.asp"
        self.startup_mode = startup_mode
        self.sent_items = self.load_sent_items() if not startup_mode else set()
        self.enhanced_parser = SylectusLoadParser()
        
        # Set headers to mimic browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def load_sent_items(self):
        """Load previously sent items"""
        try:
            with open('sent_items.txt', 'r') as f:
                return set(line.strip() for line in f.readlines())
        except FileNotFoundError:
            return set()
    
    def save_sent_item(self, item_id):
        """Save item ID to prevent duplicates"""
        with open('sent_items.txt', 'a') as f:
            f.write(f"{item_id}\n")
    
    def save_load_details(self, load_info):
        """Save detailed load information for analysis"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"load_details_{timestamp}_{load_info['load_id']}.json"
            
            with open(filename, 'w') as f:
                json.dump(load_info, f, indent=2)
            
            print(f"💾 Load details saved: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving load details: {e}")
    
    def send_to_telegram(self, message_text):
        """Send message to Telegram with rate limiting"""
        try:
            # Add delay to avoid rate limiting (max 30 messages per second for bots)
            time.sleep(1)
            
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message_text[:4096],  # Telegram max message length
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print("✅ Message sent to Telegram")
                return True
            elif response.status_code == 429:  # Rate limited
                print("⚠️ Telegram rate limit hit, waiting...")
                retry_after = response.json().get('parameters', {}).get('retry_after', 60)
                time.sleep(retry_after)
                # Retry once
                response = requests.post(url, data=data, timeout=10)
                if response.status_code == 200:
                    print("✅ Message sent after retry")
                    return True
                else:
                    print(f"❌ Telegram retry failed: {response.status_code}")
                    return False
            else:
                print(f"❌ Telegram error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Telegram error: {e}")
            return False
    
    def load_session_cookies(self):
        """Load session cookies from extracted files"""
        try:
            # Look for extracted cookie files
            import glob
            cookie_files = glob.glob("extracted_cookies_*.env")
            if cookie_files:
                # Use the most recent one
                cookie_file = sorted(cookie_files)[-1]
                print(f"📂 Loading cookies from {cookie_file}")
                
                with open(cookie_file, 'r') as f:
                    for line in f:
                        if line.startswith('SYLECTUS_COOKIE='):
                            cookie_string = line.split('=', 1)[1].strip().strip('"')
                            
                            # Parse cookie string
                            for cookie in cookie_string.split('; '):
                                if '=' in cookie:
                                    name, value = cookie.split('=', 1)
                                    self.session.cookies.set(name, value, domain='sylectus.com')
                            
                            print(f"✅ Loaded {len(self.session.cookies)} cookies")
                            return True
            
            # Fallback to .env file
            cookie_string = os.getenv('SYLECTUS_COOKIE')
            if cookie_string:
                for cookie in cookie_string.split('; '):
                    if '=' in cookie:
                        name, value = cookie.split('=', 1)
                        self.session.cookies.set(name, value, domain='sylectus.com')
                print(f"✅ Loaded cookies from .env")
                return True
                
            print("❌ No cookies found")
            return False
            
        except Exception as e:
            print(f"❌ Cookie loading error: {e}")
            return False
    
    def get_company_email(self, profile_url):
        """Get company email from profile page"""
        try:
            # Make request to company profile page
            full_url = f"{self.base_url}/{profile_url}"
            print(f"📧 Fetching email from: {profile_url}")
            
            # Add delay to avoid rate limiting
            time.sleep(2)
            
            response = self.session.get(full_url, timeout=15)
            
            if response.status_code == 200:
                # Save profile page for debugging
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(f"profile_debug_{timestamp}.html", "w", encoding='utf-8') as f:
                    f.write(response.text)
                
                # Parse the profile page for email
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for email patterns in the page text
                page_text = soup.get_text()
                
                # Enhanced email patterns
                email_patterns = [
                    r'E-?mail[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                    r'Contact[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                    r'Email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                    r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                ]
                
                for pattern in email_patterns:
                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                    for match in matches:
                        email = match if isinstance(match, str) else match[0]
                        # Clean up email address
                        email = re.sub(r'[A-Z]{3,}$', '', email)  # Remove trailing uppercase text
                        email = email.strip()
                        
                        # Skip common false positives
                        if not any(skip in email.lower() for skip in ['example.com', 'test.com', 'domain.com']):
                            # Validate email format
                            if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                                print(f"✅ Email found in profile text: {email}")
                                return email
                
                # Check for mailto links
                mailto_links = soup.find_all('a', href=re.compile(r'mailto:'))
                for link in mailto_links:
                    href = link.get('href', '')
                    email = href.replace('mailto:', '').strip()
                    if '@' in email and '.' in email:
                        print(f"✅ Email found in mailto: {email}")
                        return email
                
                # Check for emails in form fields or input values
                inputs = soup.find_all('input')
                for input_tag in inputs:
                    value = input_tag.get('value', '')
                    if '@' in value and '.' in value:
                        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', value)
                        if email_match:
                            email = email_match.group(1)
                            print(f"✅ Email found in input field: {email}")
                            return email
                
                # Check for emails in JavaScript or hidden elements
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', script.string)
                        if email_match:
                            email = email_match.group(1)
                            print(f"✅ Email found in JavaScript: {email}")
                            return email
                
                print("❌ No email found in company profile")
                print(f"📄 Profile page saved for debugging: profile_debug_{timestamp}.html")
                return None
            else:
                print(f"❌ Profile page request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching company email: {e}")
            return None
    
    def call_load_board_api(self):
        """Call the load board API to get fresh data"""
        try:
            print("📡 Calling load board API...")
            
            # First try to get the load board page to establish session
            load_board_url = f"{self.base_url}/Main.aspx?page=II14_managepostedloads.asp?loadboard=True"
            
            # Make API call to refresh load data
            response = self.session.post(self.load_board_api, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ API call successful ({len(response.text)} bytes)")
                
                # Also save raw HTML for analysis
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(f"raw_html_{timestamp}.html", "w", encoding='utf-8') as f:
                    f.write(response.text)
                print(f"💾 Raw HTML saved for analysis")
                
                return response.text
            else:
                print(f"❌ API call failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ API call error: {e}")
            return None
    
    def extract_loads_from_html(self, html_content):
        """Extract load data from HTML response"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            loads = []
            
            # Look for table rows containing load data
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) > 5:  # Likely a load row
                        row_text = row.get_text().strip()
                        
                        if len(row_text) > 50:  # Filter out header/empty rows
                            # Use enhanced parser for comprehensive data extraction
                            load_info = self.enhanced_parser.parse_load_row_comprehensive(row)
                            if load_info and load_info['load_id'] != 'Unknown':
                                # Try to get email from company profile if available
                                if 'profile_url' in load_info and load_info.get('contact_email', 'Unknown') == 'Unknown':
                                    print(f"🔍 Attempting email extraction for {load_info.get('company', 'Unknown')}")
                                    email = self.get_company_email(load_info['profile_url'])
                                    if email:
                                        load_info['contact_email'] = email
                                        print(f"✅ Email extracted: {email}")
                                    else:
                                        print(f"❌ No email found for {load_info.get('company', 'Unknown')}")
                                elif 'profile_url' not in load_info:
                                    print(f"⚠️ No profile URL found for {load_info.get('company', 'Unknown')}")
                                loads.append(load_info)
            
            return loads
            
        except Exception as e:
            print(f"❌ HTML parsing error: {e}")
            return []
    
    def parse_load_row(self, row_text, row_element):
        """Parse individual load row - extract EVERYTHING"""
        try:
            load_info = {
                'raw_text': row_text,
                'html_content': str(row_element),
                'company': 'Unknown',
                'pickup_city': 'Unknown',
                'pickup_state': 'Unknown', 
                'pickup_zip': 'Unknown',
                'pickup_date': 'Unknown',
                'pickup_time': 'Unknown',
                'delivery_city': 'Unknown',
                'delivery_state': 'Unknown',
                'delivery_zip': 'Unknown', 
                'delivery_date': 'Unknown',
                'delivery_time': 'Unknown',
                'load_id': 'Unknown',
                'reference_number': 'Unknown',
                'order_number': 'Unknown',
                'po_number': 'Unknown',
                'miles': 'Unknown',
                'deadhead_miles': 'Unknown',
                'pieces': 'Unknown',
                'weight': 'Unknown',
                'dimensions': 'Unknown',
                'length': 'Unknown',
                'width': 'Unknown', 
                'height': 'Unknown',
                'vehicle_type': 'Unknown',
                'equipment_type': 'Unknown',
                'trailer_type': 'Unknown',
                'rate': 'Unknown',
                'rate_per_mile': 'Unknown',
                'fuel_surcharge': 'Unknown',
                'total_rate': 'Unknown',
                'payment_terms': 'Unknown',
                'credit_score': 'Unknown',
                'days_to_pay': 'Unknown',
                'broker_name': 'Unknown',
                'contact_name': 'Unknown',
                'contact_phone': 'Unknown',
                'contact_email': 'Unknown',
                'contact_fax': 'Unknown',
                'special_instructions': 'Unknown',
                'commodity': 'Unknown',
                'hazmat': 'Unknown',
                'temperature': 'Unknown',
                'appointment_required': 'Unknown',
                'team_driver': 'Unknown',
                'detention_rate': 'Unknown',
                'loading_time': 'Unknown',
                'unloading_time': 'Unknown',
                'posted_date': 'Unknown',
                'posted_time': 'Unknown',
                'expires_date': 'Unknown',
                'safer_score': 'Unknown',
                'mc_number': 'Unknown',
                'dot_number': 'Unknown',
                'load_type': 'Unknown',
                'urgency': 'Unknown',
                'found_time': datetime.now().strftime("%H:%M"),
                'timestamp': datetime.now().isoformat(),
                'all_cells': [],
                'all_links': [],
                'all_attributes': {}
            }
            
            # Get all table cells for detailed extraction
            cells = row_element.find_all(['td', 'th'])
            cell_texts = [cell.get_text().strip() for cell in cells]
            load_info['all_cells'] = cell_texts
            
            # Extract all links and their attributes
            links = row_element.find_all('a')
            for link in links:
                link_info = {
                    'text': link.get_text().strip(),
                    'href': link.get('href', ''),
                    'title': link.get('title', ''),
                    'onclick': link.get('onclick', '')
                }
                load_info['all_links'].append(link_info)
            
            # Extract all HTML attributes for detailed analysis
            for attr_name, attr_value in row_element.attrs.items():
                load_info['all_attributes'][attr_name] = attr_value
            
            # Extract company name and contact info
            if links:
                load_info['company'] = links[0].get_text().strip()
                load_info['broker_name'] = links[0].get_text().strip()
                
                # Try to get email from link href
                for link in links:
                    href = link.get('href', '')
                    if 'mailto:' in href:
                        load_info['contact_email'] = href.replace('mailto:', '')
                    
                    # Extract more contact info from onclick events
                    onclick = link.get('onclick', '')
                    if onclick:
                        # Look for phone numbers in onclick
                        phone_match = re.search(r'(\d{3}[-.]?\d{3}[-.]?\d{4})', onclick)
                        if phone_match:
                            load_info['contact_phone'] = phone_match.group(1)
            
            # Extract all numbers for various fields
            all_numbers = re.findall(r'\b(\d+)\b', row_text)
            
            # Extract load ID (usually 6-7 digits)
            load_id_patterns = [
                r'Load[#\s]*:?\s*(\d{6,8})',
                r'ID[#\s]*:?\s*(\d{6,8})',
                r'\b(\d{7})\b',  # 7-digit numbers are usually load IDs
                r'\b(\d{6})\b'   # 6-digit numbers might be load IDs
            ]
            for pattern in load_id_patterns:
                match = re.search(pattern, row_text, re.IGNORECASE)
                if match:
                    load_info['load_id'] = match.group(1)
                    break
            
            # Extract cities and states with more detail
            city_state_pattern = r'([A-Z][A-Z\s&]+),\s*([A-Z]{2})(?:\s+(\d{5}))?'
            cities = re.findall(city_state_pattern, row_text)
            
            if len(cities) >= 2:
                load_info['pickup_city'] = cities[0][0].strip()
                load_info['pickup_state'] = cities[0][1]
                load_info['delivery_city'] = cities[1][0].strip()
                load_info['delivery_state'] = cities[1][1]
            elif len(cities) == 1:
                load_info['pickup_city'] = cities[0][0].strip()
                load_info['pickup_state'] = cities[0][1]
            
            # Extract dates and times
            date_patterns = [
                r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})',  # MM/DD/YYYY HH:MM
                r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
                r'(ASAP)',  # ASAP pickups
                r'(\d{1,2}/\d{1,2})\s+(\d{1,2}:\d{2})'  # MM/DD HH:MM
            ]
            
            dates_found = []
            for pattern in date_patterns:
                matches = re.findall(pattern, row_text)
                dates_found.extend(matches)
            
            if len(dates_found) >= 2:
                if isinstance(dates_found[0], tuple):
                    load_info['pickup_date'] = dates_found[0][0] if dates_found[0][0] else 'Unknown'
                    load_info['pickup_time'] = dates_found[0][1] if len(dates_found[0]) > 1 else 'Unknown'
                    load_info['delivery_date'] = dates_found[1][0] if dates_found[1][0] else 'Unknown'  
                    load_info['delivery_time'] = dates_found[1][1] if len(dates_found[1]) > 1 else 'Unknown'
                else:
                    load_info['pickup_date'] = str(dates_found[0])
                    load_info['delivery_date'] = str(dates_found[1])
            
            # Extract vehicle/equipment type
            vehicle_patterns = [
                r'(STRAIGHT|TRUCK|VAN|FLATBED|REEFER|DRY VAN|BOX TRUCK|CARGO VAN)',
                r'(SMALL STRAIGHT|LARGE STRAIGHT)',
                r'(53\s*FT|48\s*FT|26\s*FT|24\s*FT|20\s*FT)',
                r'(EXPEDITED|TEAM|SOLO)'
            ]
            
            for pattern in vehicle_patterns:
                match = re.search(pattern, row_text, re.IGNORECASE)
                if match:
                    load_info['vehicle_type'] = match.group(1)
                    break
            
            # Extract weight, pieces, miles from cell positions or patterns
            weight_match = re.search(r'(\d+)\s*(lbs?|pounds?)', row_text, re.IGNORECASE)
            if weight_match:
                load_info['weight'] = f"{weight_match.group(1)} lbs"
            
            pieces_match = re.search(r'(\d+)\s*(pieces?|pcs?|units?)', row_text, re.IGNORECASE)
            if pieces_match:
                load_info['pieces'] = pieces_match.group(1)
            
            miles_match = re.search(r'(\d+)\s*(miles?|mi)', row_text, re.IGNORECASE)
            if miles_match:
                load_info['miles'] = miles_match.group(1)
            
            # Extract dimensions
            dim_patterns = [
                r'(\d+)\s*[xX×]\s*(\d+)\s*[xX×]\s*(\d+)',  # LxWxH
                r'(\d+)["\']?\s*[xX×]\s*(\d+)["\']?\s*[xX×]\s*(\d+)["\']?',  # with quotes
                r'(\d+)\s*L\s*[xX×]\s*(\d+)\s*W\s*[xX×]\s*(\d+)\s*H'  # LxWxH format
            ]
            
            for pattern in dim_patterns:
                match = re.search(pattern, row_text, re.IGNORECASE)
                if match:
                    load_info['dimensions'] = f"{match.group(1)}x{match.group(2)}x{match.group(3)}"
                    break
            
            # Extract payment terms and credit info
            credit_match = re.search(r'Credit\s*Score[:\s]*(\d+)%?', row_text, re.IGNORECASE)
            if credit_match:
                load_info['credit_score'] = f"{credit_match.group(1)}%"
            
            pay_days_match = re.search(r'(\d+)\s*days?\s*to\s*pay', row_text, re.IGNORECASE)
            if pay_days_match:
                load_info['days_to_pay'] = f"{pay_days_match.group(1)} days"
            
            # Extract rate information
            rate_patterns = [
                r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $1,500.00
                r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*\$',  # 1500$
                r'Rate[:\s]*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'  # Rate: $1500
            ]
            
            for pattern in rate_patterns:
                match = re.search(pattern, row_text, re.IGNORECASE)
                if match:
                    load_info['rate'] = f"${match.group(1)}"
                    break
            
            # Extract phone numbers
            phone_match = re.search(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', row_text)
            if phone_match:
                load_info['contact_phone'] = phone_match.group(1)
            
            # Extract email addresses (comprehensive patterns)
            email_patterns = [
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Standard email
                r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Mailto links
                r'E-?mail[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Email: prefix
                r'Contact[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'  # Contact: prefix
            ]
            
            for pattern in email_patterns:
                email_match = re.search(pattern, row_text, re.IGNORECASE)
                if email_match:
                    load_info['contact_email'] = email_match.group(1)
                    break
            
            # Also check link hrefs for email addresses
            for link in links:
                href = link.get('href', '')
                if 'mailto:' in href.lower():
                    email = href.lower().replace('mailto:', '')
                    if '@' in email:
                        load_info['contact_email'] = email
            
            # Extract special instructions/notes
            instruction_patterns = [
                r'(EMAIL ONLY)',
                r'(NO DISPATCH)',
                r'(TEAM REQUIRED)',
                r'(HAZMAT)',
                r'(EXPEDITED)',
                r'(APPOINTMENT)',
                r'(DETENTION)',
                r'(INSIDE DELIVERY)'
            ]
            
            instructions = []
            for pattern in instruction_patterns:
                if re.search(pattern, row_text, re.IGNORECASE):
                    instructions.append(pattern.strip('()'))
            
            if instructions:
                load_info['special_instructions'] = ', '.join(instructions)
            
            # Extract additional info from the debug cell data we can see
            # Cell 0: Company + payment info
            # Cell 1: Load type + Load ID  
            # Cell 2: Reference number
            
            if len(cell_texts) >= 3:
                # Parse first cell for company and payment details
                first_cell = cell_texts[0] if cell_texts[0] else ""
                
                # Extract company name (before payment info)
                company_parts = first_cell.split('VF')[0] if 'VF' in first_cell else first_cell
                company_parts = company_parts.split('Days to Pay')[0] if 'Days to Pay' in company_parts else company_parts
                if company_parts.strip() and load_info['company'] == 'Unknown':
                    load_info['company'] = company_parts.strip()
                
                # Parse second cell for load ID
                second_cell = cell_texts[1] if len(cell_texts) > 1 else ""
                load_id_match = re.search(r'(\d{6,})', second_cell)
                if load_id_match and load_info['load_id'] == 'Unknown':
                    load_info['load_id'] = load_id_match.group(1)
                
                # Look for actual miles, pieces, weight in remaining cells
                for i, cell in enumerate(cell_texts[2:], 2):  # Start from cell 2
                    if cell and cell.isdigit():
                        num = int(cell)
                        
                        # Miles are usually 100-3000
                        if 100 <= num <= 3000 and load_info['miles'] == 'Unknown':
                            load_info['miles'] = cell
                        
                        # Pieces are usually 1-50  
                        elif 1 <= num <= 50 and load_info['pieces'] == 'Unknown':
                            load_info['pieces'] = cell
                        
                        # Weight is usually over 500
                        elif num > 500 and load_info['weight'] == 'Unknown':
                            load_info['weight'] = f"{cell} lbs"
            
            # Additional email extraction from all cell content
            for cell_text in cell_texts:
                if '@' in cell_text and '.' in cell_text:
                    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', cell_text)
                    if email_match and load_info['contact_email'] == 'Unknown':
                        load_info['contact_email'] = email_match.group(1)
                        break
            
            return load_info
            
        except Exception as e:
            print(f"❌ Load parsing error: {e}")
            return None
    
    def format_telegram_message(self, load_info):
        """Format comprehensive load info for Telegram"""
        message = f"""🆕 **NEW SYLECTUS LOAD**

🏢 **Company:** {load_info['company']}
🆔 **Load ID:** {load_info['load_id']}

📍 **PICKUP:**
   📍 {load_info['pickup_city']}, {load_info['pickup_state']}
   📅 {load_info['pickup_date']} {load_info['pickup_time']}

📍 **DELIVERY:**
   📍 {load_info['delivery_city']}, {load_info['delivery_state']}
   📅 {load_info['delivery_date']} {load_info['delivery_time']}

🚛 **LOAD DETAILS:**
   📏 Miles: {load_info['miles']}
   📦 Pieces: {load_info['pieces']}
   ⚖️ Weight: {load_info['weight']}"""

        if load_info.get('vehicle_type') != 'Unknown':
            message += f"\n   🚐 Vehicle: {load_info['vehicle_type']}"
        
        if load_info.get('dimensions') != 'Unknown':
            message += f"\n   📐 Dimensions: {load_info['dimensions']}"
        
        if load_info.get('rate', 'Unknown') != 'Unknown':
            message += f"\n\n💰 **Rate:** {load_info['rate']}"
        else:
            # Calculate rate estimate
            try:
                miles_val = load_info.get('miles', 'Unknown')
                if miles_val != 'Unknown' and str(miles_val).isdigit():
                    miles = int(miles_val)
                    rate = miles * 0.75  # $0.75 per mile estimate
                    message += f"\n\n💰 **Est. Rate:** ${rate:.0f}"
            except:
                pass
        
        # Payment terms
        payment_section = ""
        if load_info.get('credit_score', 'Unknown') != 'Unknown':
            payment_section += f"\n💳 Credit Score: {load_info['credit_score']}"
        
        if load_info.get('days_to_pay', 'Unknown') != 'Unknown':
            payment_section += f"\n📅 Payment Terms: {load_info['days_to_pay']}"
        
        if payment_section:
            message += f"\n\n**PAYMENT INFO:**{payment_section}"
        
        # Contact information (prioritize email)
        contact_section = ""
        has_email = False
        
        if load_info.get('contact_email', 'Unknown') != 'Unknown':
            contact_section += f"\n📧 **Email: {load_info['contact_email']}**"
            has_email = True
        
        if load_info.get('contact_phone', 'Unknown') != 'Unknown':
            contact_section += f"\n📞 Phone: {load_info['contact_phone']}"
        
        broker_email = load_info.get('broker_email', 'Unknown')
        contact_email = load_info.get('contact_email', 'Unknown')
        if broker_email != 'Unknown' and broker_email != contact_email:
            contact_section += f"\n📧 Broker Email: {broker_email}"
            has_email = True
        
        if contact_section:
            message += f"\n\n**CONTACT INFO:**{contact_section}"
        
        # Add email status indicator
        if not has_email:
            message += f"\n\n⚠️ **NO EMAIL FOUND** - Check company profile"
            if 'profile_url' in load_info:
                message += f"\n🔗 Profile: {load_info['profile_url']}"
        else:
            message += f"\n\n✅ **Email Available**"
        
        # Special instructions
        if load_info.get('special_instructions', 'Unknown') != 'Unknown':
            message += f"\n\n⚠️ **Special Instructions:** {load_info['special_instructions']}"
        
        message += f"\n\n⏰ **Found:** {load_info.get('found_time', 'Unknown')}"
        message += f"\n🌐 **Via API Scraper**"
        
        # Add debug info for development (optional)
        debug_cells = load_info.get('all_cells', [])
        if debug_cells:
            message += f"\n\n🔧 **Debug:** {len(debug_cells)} cells analyzed"
        
        return message
    
    def monitor_loads(self):
        """Main monitoring loop"""
        print("🚀 Starting API-based monitoring...")
        
        # Load session cookies
        if not self.load_session_cookies():
            self.send_to_telegram("❌ No session cookies found. Please run network_monitor.py first.")
            return
        
        self.send_to_telegram("🚀 API Scraper started - monitoring load board...")
        
        while True:
            try:
                # Call the API
                html_data = self.call_load_board_api()
                
                if html_data:
                    # Extract loads
                    loads = self.extract_loads_from_html(html_data)
                    
                    new_loads_count = 0
                    new_loads_batch = []
                    
                    # First collect all new loads (or all loads if startup mode)
                    for load_info in loads:
                        # Create unique identifier
                        unique_id = f"{load_info['load_id']}_{load_info['pickup_city']}, {load_info['pickup_state']}_{load_info['delivery_city']}, {load_info['delivery_state']}"
                        
                        if self.startup_mode or unique_id not in self.sent_items:
                            new_loads_batch.append((load_info, unique_id))
                    
                    # Send new loads with rate limiting
                    if new_loads_batch:
                        if self.startup_mode:
                            # Send startup summary
                            summary_msg = f"🚀 **STARTUP SCAN COMPLETE** - Found {len(new_loads_batch)} loads available - Sending details..."
                            self.send_to_telegram(summary_msg)
                        elif len(new_loads_batch) > 5:
                            # If too many new loads, send summary first
                            summary_msg = f"🚨 **{len(new_loads_batch)} NEW LOADS FOUND** - Sending details..."
                            self.send_to_telegram(summary_msg)
                        
                        for load_info, unique_id in new_loads_batch:
                            # Save detailed load data for analysis
                            self.save_load_details(load_info)
                            
                            # Format and send message
                            message = self.format_telegram_message(load_info)
                            
                            if self.send_to_telegram(message):
                                self.save_sent_item(unique_id)
                                new_loads_count += 1
                                print(f"✅ New load sent: {load_info['company']} - {load_info['load_id']}")
                            else:
                                print(f"❌ Failed to send load: {load_info['load_id']}")
                                break  # Stop sending if Telegram fails
                    
                    if self.startup_mode:
                        print(f"📊 Startup scan complete. Found {len(loads)} total loads, sent {new_loads_count}")
                        self.startup_mode = False  # Switch to normal mode after first scan
                    else:
                        print(f"📊 Scan complete. Found {len(loads)} total loads, {new_loads_count} new")
                
                else:
                    print("⚠️ API call failed, retrying in 60 seconds...")
                    time.sleep(60)
                    continue
                
                # Wait for next check
                print(f"⏰ Waiting {CHECK_INTERVAL} seconds...")
                time.sleep(CHECK_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n🛑 Monitoring stopped by user")
                self.send_to_telegram("🛑 API Scraper stopped")
                break
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                self.send_to_telegram(f"⚠️ API Scraper error: {e}")
                time.sleep(60)  # Wait before retrying

def main():
    """Main entry point"""
    import sys
    startup_mode = '--startup' in sys.argv or len(sys.argv) == 1  # Default to startup mode
    client = SylectusAPIClient(startup_mode=startup_mode)
    client.monitor_loads()

if __name__ == "__main__":
    main()