#!/usr/bin/env python3
"""
Test email extraction from company profile pages
"""

import requests
import glob
import re
from bs4 import BeautifulSoup
from datetime import datetime

def test_email_extraction():
    print("🧪 Testing email extraction from company profile...")
    
    # Create session and load cookies
    session = requests.Session()
    
    # Load extracted cookies
    cookie_files = glob.glob("extracted_cookies_*.env")
    if cookie_files:
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
                            session.cookies.set(name, value, domain='sylectus.com')
                    
                    print(f"✅ Loaded {len(session.cookies)} cookies")
                    break
    else:
        print("❌ No cookie files found")
        return
    
    # Test profile URL from our test
    profile_url = "II14_promabprofile.asp?pronumuk=3931502&mabcode=2134651&postedby=13337"
    full_url = f"https://www.sylectus.com/{profile_url}"
    
    print(f"🌐 Fetching profile: {full_url}")
    
    # Set headers to mimic browser
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    try:
        response = session.get(full_url, timeout=15)
        
        if response.status_code == 200:
            print(f"✅ Successfully fetched profile page ({len(response.text)} bytes)")
            
            # Save for debugging
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_file = f"profile_debug_{timestamp}.html"
            with open(debug_file, "w", encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 Profile page saved: {debug_file}")
            
            # Parse and look for emails
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            
            # Enhanced email patterns
            email_patterns = [
                r'E-?mail[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'Contact[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'Email[:\s]*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ]
            
            emails_found = []
            
            for pattern in email_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                for match in matches:
                    email = match if isinstance(match, str) else match[0]
                    # Skip common false positives
                    if not any(skip in email.lower() for skip in ['example.com', 'test.com', 'domain.com']):
                        emails_found.append(email)
            
            # Check for mailto links
            mailto_links = soup.find_all('a', href=re.compile(r'mailto:'))
            for link in mailto_links:
                href = link.get('href', '')
                email = href.replace('mailto:', '').strip()
                if '@' in email and '.' in email:
                    emails_found.append(email)
            
            # Check for emails in form fields
            inputs = soup.find_all('input')
            for input_tag in inputs:
                value = input_tag.get('value', '')
                if '@' in value and '.' in value:
                    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', value)
                    if email_match:
                        emails_found.append(email_match.group(1))
            
            # Check JavaScript
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', script.string)
                    if email_match:
                        emails_found.append(email_match.group(1))
            
            # Remove duplicates
            unique_emails = list(set(emails_found))
            
            if unique_emails:
                print(f"✅ Found {len(unique_emails)} email(s):")
                for email in unique_emails:
                    print(f"   📧 {email}")
                return unique_emails[0]  # Return first email
            else:
                print("❌ No emails found in profile page")
                print(f"📄 Check {debug_file} for manual inspection")
                return None
        
        else:
            print(f"❌ Failed to fetch profile: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching profile: {e}")
        return None

if __name__ == "__main__":
    email = test_email_extraction()
    if email:
        print(f"\n✅ Email extraction test successful! Found: {email}")
    else:
        print(f"\n❌ Email extraction test failed")