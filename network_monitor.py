#!/usr/bin/env python3
"""
Network Monitor + Cookie Extractor
Captures all network requests and extracts session cookies while you're logged in
"""

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime
import re

class NetworkMonitor:
    def __init__(self):
        self.requests = []
        self.responses = []
        self.cookies = {}
        self.api_calls = []
        
    def save_data(self, filename_prefix):
        """Save all captured data to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save requests
        with open(f"{filename_prefix}_requests_{timestamp}.json", "w") as f:
            json.dump(self.requests, f, indent=2)
        
        # Save responses  
        with open(f"{filename_prefix}_responses_{timestamp}.json", "w") as f:
            json.dump(self.responses, f, indent=2)
            
        # Save cookies
        with open(f"{filename_prefix}_cookies_{timestamp}.json", "w") as f:
            json.dump(self.cookies, f, indent=2)
            
        # Save potential API calls
        with open(f"{filename_prefix}_api_calls_{timestamp}.json", "w") as f:
            json.dump(self.api_calls, f, indent=2)
        
        print(f"💾 Data saved with timestamp: {timestamp}")
        
    def is_potential_api_call(self, url, method, content_type):
        """Identify potential API calls"""
        api_indicators = [
            'api', 'json', 'ajax', 'xhr', 'load', 'posting', 'board',
            'search', 'fetch', 'data', 'service', 'endpoint'
        ]
        
        # Check URL for API indicators
        url_lower = url.lower()
        for indicator in api_indicators:
            if indicator in url_lower:
                return True
                
        # Check if it returns JSON
        if content_type and 'json' in content_type.lower():
            return True
            
        # Check if it's a POST/PUT request (often API calls)
        if method in ['POST', 'PUT', 'PATCH']:
            return True
            
        return False

    def monitor_requests(self, page):
        """Set up request monitoring"""
        def handle_request(request):
            try:
                request_data = {
                    'url': request.url,
                    'method': request.method,
                    'headers': dict(request.headers),
                    'post_data': request.post_data,
                    'timestamp': datetime.now().isoformat()
                }
                self.requests.append(request_data)
                
                # Print interesting requests in real-time
                if any(keyword in request.url.lower() for keyword in ['load', 'post', 'search', 'api', 'ajax']):
                    print(f"🔍 REQUEST: {request.method} {request.url}")
                    if request.post_data:
                        print(f"   📝 POST DATA: {request.post_data[:200]}...")
                        
            except Exception as e:
                print(f"❌ Request monitoring error: {e}")
        
        def handle_response(response):
            try:
                content_type = response.headers.get('content-type', '')
                
                response_data = {
                    'url': response.url,
                    'status': response.status,
                    'headers': dict(response.headers),
                    'content_type': content_type,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Try to get response body for API-like calls
                if self.is_potential_api_call(response.url, 'GET', content_type):
                    try:
                        body = response.body()
                        if body:
                            body_text = body.decode('utf-8')
                            response_data['body'] = body_text[:10000]  # Limit size
                            
                            # Check if it's JSON with load data
                            if 'json' in content_type.lower():
                                try:
                                    json_data = json.loads(body_text)
                                    response_data['json_data'] = json_data
                                    
                                    # Look for load-related data
                                    body_str = str(json_data).lower()
                                    if any(keyword in body_str for keyword in ['load', 'pickup', 'delivery', 'freight', 'truck']):
                                        print(f"🎯 POTENTIAL LOAD API: {response.url}")
                                        print(f"   📊 JSON DATA: {str(json_data)[:300]}...")
                                        self.api_calls.append({
                                            'url': response.url,
                                            'method': 'GET',
                                            'json_data': json_data,
                                            'timestamp': datetime.now().isoformat()
                                        })
                                        
                                except json.JSONDecodeError:
                                    pass
                    except Exception as e:
                        print(f"⚠️ Could not get response body: {e}")
                
                self.responses.append(response_data)
                
                # Print interesting responses
                if any(keyword in response.url.lower() for keyword in ['load', 'post', 'search', 'api', 'ajax']):
                    print(f"✅ RESPONSE: {response.status} {response.url} ({content_type})")
                    
            except Exception as e:
                print(f"❌ Response monitoring error: {e}")
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
    def extract_cookies(self, context):
        """Extract all cookies from browser context"""
        try:
            cookies = context.cookies()
            self.cookies = {cookie['name']: cookie['value'] for cookie in cookies}
            
            # Also save in .env format
            cookie_string = "; ".join([f"{name}={value}" for name, value in self.cookies.items()])
            
            with open("extracted_cookies.env", "w") as f:
                f.write(f'SYLECTUS_COOKIE="{cookie_string}"\n')
                
            print(f"🍪 Extracted {len(self.cookies)} cookies")
            print("💾 Cookies saved to extracted_cookies.env")
            
        except Exception as e:
            print(f"❌ Cookie extraction error: {e}")

def main():
    print("🕵️ Network Monitor + Cookie Extractor")
    print("📝 This will monitor ALL network traffic while you navigate")
    
    monitor = NetworkMonitor()
    
    with sync_playwright() as p:
        # Launch visible browser
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        # Start monitoring
        monitor.monitor_requests(page)
        
        print("\n🌐 Navigate to Sylectus and log in manually...")
        page.goto("https://www.sylectus.net/")
        
        print("\n🎮 INSTRUCTIONS:")
        print("1. Log in to Sylectus manually")
        print("2. Navigate to Load Board")
        print("3. Click refresh/search buttons")
        print("4. Let it load completely")
        print("5. Press Enter here when done")
        
        try:
            input("\n➡️ Press Enter when you've finished navigating: ")
            
            # Extract cookies
            print("\n🍪 Extracting cookies...")
            monitor.extract_cookies(context)
            
            # Save all captured data
            print("\n💾 Saving network data...")
            monitor.save_data("sylectus_network")
            
            print(f"\n📊 CAPTURE SUMMARY:")
            print(f"   🔍 Total Requests: {len(monitor.requests)}")
            print(f"   ✅ Total Responses: {len(monitor.responses)}")
            print(f"   🎯 Potential API Calls: {len(monitor.api_calls)}")
            print(f"   🍪 Cookies Extracted: {len(monitor.cookies)}")
            
            if monitor.api_calls:
                print("\n🎯 POTENTIAL LOAD APIs FOUND:")
                for api_call in monitor.api_calls:
                    print(f"   📡 {api_call['url']}")
            
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
        finally:
            browser.close()
            print("✅ Network monitoring complete!")

if __name__ == "__main__":
    main()