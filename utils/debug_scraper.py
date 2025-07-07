#!/usr/bin/env python3
"""
Debug version of API scraper to see what's happening
"""

from api_scraper import SylectusAPIClient
import time

def debug_run():
    print("🔍 Debug API Scraper")
    
    client = SylectusAPIClient()
    
    # Load cookies
    print("1. Loading cookies...")
    if client.load_session_cookies():
        print("✅ Cookies loaded")
    else:
        print("❌ No cookies found")
        return
    
    # Test API call
    print("2. Testing API call...")
    html_data = client.call_load_board_api()
    
    if html_data:
        print(f"✅ Got {len(html_data)} bytes of HTML")
        
        # Test parsing
        print("3. Testing load extraction...")
        loads = client.extract_loads_from_html(html_data)
        print(f"✅ Found {len(loads)} loads")
        
        if loads:
            load = loads[0]
            print(f"   Sample load: {load.get('company', 'Unknown')} - {load.get('load_id', 'Unknown')}")
            print(f"   Email: {load.get('contact_email', 'Unknown')}")
        
        # Test Telegram
        print("4. Testing Telegram...")
        test_msg = "🧪 Debug test from enhanced API scraper"
        if client.send_to_telegram(test_msg):
            print("✅ Telegram working")
        else:
            print("❌ Telegram failed")
    
    else:
        print("❌ API call failed")

if __name__ == "__main__":
    debug_run()