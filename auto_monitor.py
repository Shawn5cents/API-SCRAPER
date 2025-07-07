#!/usr/bin/env python3
"""
Auto Network Monitor - Runs for specified time and saves data automatically
"""

from playwright.sync_api import sync_playwright
import json
import time
from datetime import datetime
import threading

def save_monitoring_data(requests, responses, api_calls, cookies):
    """Save all captured data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save everything
    with open(f"monitor_requests_{timestamp}.json", "w") as f:
        json.dump(requests, f, indent=2)
    
    with open(f"monitor_responses_{timestamp}.json", "w") as f:
        json.dump(responses, f, indent=2)
        
    with open(f"monitor_api_calls_{timestamp}.json", "w") as f:
        json.dump(api_calls, f, indent=2)
        
    with open(f"monitor_cookies_{timestamp}.json", "w") as f:
        json.dump(cookies, f, indent=2)
    
    # Save cookies in .env format
    if cookies:
        cookie_string = "; ".join([f"{name}={value}" for name, value in cookies.items()])
        with open(f"extracted_cookies_{timestamp}.env", "w") as f:
            f.write(f'SYLECTUS_COOKIE="{cookie_string}"\n')
    
    print(f"💾 All data saved with timestamp: {timestamp}")
    return timestamp

def main():
    print("🤖 Auto Network Monitor")
    print("📝 Will monitor network traffic for 10 minutes then save everything")
    
    requests = []
    responses = []
    api_calls = []
    cookies = {}
    
    def handle_request(request):
        try:
            request_data = {
                'url': request.url,
                'method': request.method,
                'headers': dict(request.headers),
                'post_data': request.post_data,
                'timestamp': datetime.now().isoformat()
            }
            requests.append(request_data)
            
            # Print load-related requests
            if any(keyword in request.url.lower() for keyword in ['load', 'posting', 'search', 'board', 'api']):
                print(f"🔍 {request.method} {request.url}")
                
        except Exception as e:
            print(f"❌ Request error: {e}")
    
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
            
            # Capture JSON responses that might contain load data
            if 'json' in content_type.lower() and response.status == 200:
                try:
                    body = response.body()
                    if body:
                        body_text = body.decode('utf-8')
                        json_data = json.loads(body_text)
                        
                        # Check if it contains load-related data
                        body_str = str(json_data).lower()
                        if any(keyword in body_str for keyword in ['load', 'pickup', 'delivery', 'freight', 'truck', 'sylectus']):
                            print(f"🎯 LOAD DATA API: {response.url}")
                            api_calls.append({
                                'url': response.url,
                                'method': 'GET',
                                'json_data': json_data,
                                'timestamp': datetime.now().isoformat()
                            })
                            
                except:
                    pass
            
            responses.append(response_data)
            
        except Exception as e:
            print(f"❌ Response error: {e}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        # Set up monitoring
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # Go to Sylectus
        print("🌐 Loading Sylectus...")
        page.goto("https://www.sylectus.net/")
        
        print("\n🎮 PLEASE LOG IN MANUALLY AND NAVIGATE TO LOAD BOARD")
        print("💡 I'll monitor for 10 minutes and save everything automatically")
        
        # Monitor for 10 minutes
        start_time = time.time()
        duration = 600  # 10 minutes
        
        try:
            while time.time() - start_time < duration:
                remaining = duration - (time.time() - start_time)
                print(f"⏰ Monitoring... {remaining/60:.1f} minutes remaining", end='\r')
                time.sleep(30)  # Update every 30 seconds
                
                # Extract cookies periodically
                try:
                    browser_cookies = context.cookies()
                    cookies = {cookie['name']: cookie['value'] for cookie in browser_cookies}
                except:
                    pass
            
            print(f"\n⏰ Monitoring complete!")
            
        except KeyboardInterrupt:
            print(f"\n🛑 Monitoring stopped early")
        
        finally:
            # Save everything
            timestamp = save_monitoring_data(requests, responses, api_calls, cookies)
            
            print(f"\n📊 FINAL SUMMARY:")
            print(f"   🔍 Requests captured: {len(requests)}")
            print(f"   ✅ Responses captured: {len(responses)}")
            print(f"   🎯 API calls found: {len(api_calls)}")
            print(f"   🍪 Cookies extracted: {len(cookies)}")
            
            if api_calls:
                print(f"\n🎯 POTENTIAL LOAD APIS:")
                for api in api_calls:
                    print(f"   📡 {api['url']}")
            
            browser.close()

if __name__ == "__main__":
    main()