#!/usr/bin/env python3
"""
Quick test of API connection
"""

import requests
import glob

def test_connection():
    print("🧪 Testing API connection...")
    
    session = requests.Session()
    
    # Load cookies
    cookie_files = glob.glob("extracted_cookies_*.env")
    if cookie_files:
        cookie_file = sorted(cookie_files)[-1]
        print(f"📂 Loading cookies from {cookie_file}")
        
        with open(cookie_file, 'r') as f:
            for line in f:
                if line.startswith('SYLECTUS_COOKIE='):
                    cookie_string = line.split('=', 1)[1].strip().strip('"')
                    for cookie in cookie_string.split('; '):
                        if '=' in cookie:
                            name, value = cookie.split('=', 1)
                            session.cookies.set(name, value, domain='sylectus.com')
                    break
    
    # Set headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    
    # Test API call
    api_url = "https://www.sylectus.com/II14_managepostedloads.asp"
    
    try:
        print(f"🌐 Testing API call to {api_url}")
        response = session.post(api_url, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Content length: {len(response.text)}")
        
        if "login" in response.text.lower() or "sign in" in response.text.lower():
            print("❌ Cookies expired - need fresh login")
        elif len(response.text) > 1000:
            print("✅ API call successful - got data")
        else:
            print("⚠️ Unexpected response")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()