#!/usr/bin/env python3
"""
Test profile URL extraction with real load data
"""

import json
import re
from bs4 import BeautifulSoup
from enhanced_parser import SylectusLoadParser

def test_profile_extraction():
    # Load the real data from the JSON file
    with open('load_details_20250706_201715_1031358.json', 'r') as f:
        load_data = json.load(f)
    
    print("🔍 Testing profile URL extraction with real data...")
    print(f"Company: {load_data['company']}")
    print(f"Load ID: {load_data['load_id']}")
    
    # Extract the onclick event from the company link
    company_link = None
    for link in load_data['all_links']:
        if link['text'] == load_data['company']:
            company_link = link
            break
    
    if company_link:
        print(f"\n📋 Company Link onclick: {company_link['onclick']}")
        
        # Extract profile URL using our enhanced patterns
        onclick = company_link['onclick']
        if 'II14_promabprofile.asp' in onclick:
            url_patterns = [
                r"'([^']+II14_promabprofile\.asp[^']+)'",
                r'"([^"]+II14_promabprofile\.asp[^"]+)"',
                r"openawindow\('([^']+)', \d+, \d+\)",
                r"openawindow\(\"([^\"]+)\", \d+, \d+\)"
            ]
            
            for pattern in url_patterns:
                url_match = re.search(pattern, onclick)
                if url_match:
                    profile_url = url_match.group(1)
                    profile_url = profile_url.replace('&amp;', '&')
                    print(f"✅ Profile URL extracted: {profile_url}")
                    
                    # Test if this would work with our API scraper
                    full_url = f"https://www.sylectus.com/{profile_url}"
                    print(f"🌐 Full URL would be: {full_url}")
                    return profile_url
    
    print("❌ No profile URL found")
    return None

def test_with_enhanced_parser():
    print("\n🧪 Testing with enhanced parser...")
    
    # Create HTML from the JSON data
    with open('load_details_20250706_201715_1031358.json', 'r') as f:
        load_data = json.load(f)
    
    # Parse the raw HTML
    soup = BeautifulSoup(load_data['raw_html'], 'html.parser')
    row = soup.find('tr')
    
    if row:
        parser = SylectusLoadParser()
        result = parser.parse_load_row_comprehensive(row)
        
        print(f"Company: {result.get('company', 'Unknown')}")
        print(f"Load ID: {result.get('load_id', 'Unknown')}")
        print(f"Contact Email: {result.get('contact_email', 'Unknown')}")
        print(f"Profile URL: {result.get('profile_url', 'Not found')}")
        
        return result.get('profile_url')
    
    return None

if __name__ == "__main__":
    profile_url = test_profile_extraction()
    enhanced_profile_url = test_with_enhanced_parser()
    
    if profile_url or enhanced_profile_url:
        print(f"\n✅ Success! Profile URL extraction is working")
        if enhanced_profile_url:
            print(f"Enhanced parser found: {enhanced_profile_url}")
    else:
        print(f"\n❌ Profile URL extraction needs more work")