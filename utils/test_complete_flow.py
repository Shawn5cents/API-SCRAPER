#!/usr/bin/env python3
"""
Test complete flow: API call -> load extraction -> email extraction -> Telegram formatting
"""

import os
import json
from api_scraper import SylectusAPIClient

def test_complete_flow():
    print("🧪 Testing complete API scraper flow...")
    
    # Create API client
    client = SylectusAPIClient()
    
    # Load session cookies
    if not client.load_session_cookies():
        print("❌ No session cookies found")
        return
    
    print("✅ Session cookies loaded")
    
    # Test with saved HTML data (simulating API call)
    test_html_files = [f for f in os.listdir('.') if f.startswith('raw_html_') and f.endswith('.html')]
    
    if test_html_files:
        # Use most recent HTML file
        html_file = sorted(test_html_files)[-1]
        print(f"📂 Using test data from: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract loads using our enhanced parser
        print("🔍 Extracting loads from HTML...")
        loads = client.extract_loads_from_html(html_content)
        
        print(f"📊 Found {len(loads)} loads")
        
        # Test with first load that has a profile URL
        for load_info in loads:
            if 'profile_url' in load_info and load_info.get('load_id', 'Unknown') != 'Unknown':
                print(f"\n🎯 Testing with load: {load_info['company']} - {load_info['load_id']}")
                
                # Format Telegram message
                message = client.format_telegram_message(load_info)
                print(f"\n📱 Telegram message preview:")
                print("=" * 50)
                print(message[:500] + "..." if len(message) > 500 else message)
                print("=" * 50)
                
                # Check if email was extracted
                email = load_info.get('contact_email', 'Unknown')
                if email != 'Unknown':
                    print(f"✅ Email found: {email}")
                else:
                    print(f"⚠️ No email found - would attempt profile extraction")
                
                return True
        
        print("❌ No loads with profile URLs found in test data")
        return False
    
    else:
        print("❌ No test HTML files found. Run the API scraper first to generate test data.")
        return False

def test_email_priority():
    """Test email extraction priority and fallback"""
    print("\n🧪 Testing email extraction priority...")
    
    # Test data with different email scenarios
    test_scenarios = [
        {
            'name': 'Direct email in load data',
            'load': {'contact_email': 'direct@company.com', 'profile_url': 'test.asp'},
            'expected': 'direct@company.com'
        },
        {
            'name': 'No email, has profile URL',
            'load': {'contact_email': 'Unknown', 'profile_url': 'test.asp'},
            'expected': 'Profile extraction would be attempted'
        },
        {
            'name': 'No email, no profile URL',
            'load': {'contact_email': 'Unknown'},
            'expected': 'No email available'
        }
    ]
    
    client = SylectusAPIClient()
    
    for scenario in test_scenarios:
        print(f"\n📋 {scenario['name']}:")
        load_info = scenario['load']
        load_info.update({
            'company': 'TEST COMPANY',
            'load_id': '123456',
            'pickup_city': 'TEST',
            'pickup_state': 'TX',
            'pickup_date': '07/07/2025',
            'pickup_time': '12:00',
            'delivery_city': 'TEST',
            'delivery_state': 'CA',
            'delivery_date': '07/07/2025',
            'delivery_time': '18:00',
            'miles': '1000',
            'pieces': 'Unknown',
            'weight': 'Unknown',
            'vehicle_type': 'Unknown',
            'credit_score': 'Unknown',
            'days_to_pay': 'Unknown',
            'found_time': '12:00'
        })
        
        message = client.format_telegram_message(load_info)
        
        if 'Email:' in message:
            print(f"✅ Email included in message")
        elif 'NO EMAIL FOUND' in message:
            print(f"⚠️ No email warning shown")
        elif 'Profile:' in message:
            print(f"🔗 Profile URL provided for manual check")
        
        print(f"Expected: {scenario['expected']}")

if __name__ == "__main__":
    success = test_complete_flow()
    test_email_priority()
    
    if success:
        print(f"\n✅ Complete flow test successful!")
        print(f"🚀 The enhanced API scraper is ready to run with email extraction!")
    else:
        print(f"\n⚠️ Complete flow test had issues - check the logs above")