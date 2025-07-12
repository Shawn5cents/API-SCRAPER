#!/usr/bin/env python3
"""
Simple cookie capture tool for Sylectus session
"""
import os
import datetime
import re

def save_cookies_to_env(cookie_string, filename=None):
    """Save cookies to .env format file"""
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"extracted_cookies_{timestamp}.env"
    
    # Clean and format cookie string
    cookie_string = cookie_string.strip()
    if not cookie_string.startswith('"'):
        cookie_string = f'"{cookie_string}"'
    
    env_content = f'SYLECTUS_COOKIE={cookie_string}\n'
    
    with open(filename, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Cookies saved to: {filename}")
    return filename

def validate_cookies(cookie_string):
    """Validate cookie string contains essential Sylectus cookies"""
    required_cookies = ['ASP.NET_SessionId', 'loginid', 'loginuser']
    
    for required in required_cookies:
        if required not in cookie_string:
            print(f"⚠️  Warning: Missing required cookie: {required}")
            return False
    
    print("✅ Cookie validation passed")
    return True

def main():
    print("🍪 Manual Cookie Capture Tool")
    print("=" * 50)
    
    print("\n📋 Instructions:")
    print("1. Open browser to: https://www.sylectus.com/Login.aspx")
    print("2. Log into your Sylectus account")
    print("3. Navigate to the load board")
    print("4. Open Developer Tools (F12)")
    print("5. Go to Application/Storage > Cookies")
    print("6. Copy ALL cookies for sylectus.com")
    print("7. Paste the cookie string below")
    
    print("\n🔍 Format: name1=value1; name2=value2; name3=value3...")
    print("\nEnter cookies (or press Enter to skip):")
    
    cookie_input = input("> ").strip()
    
    if not cookie_input:
        print("❌ No cookies provided. Exiting.")
        return
    
    # Validate cookies
    if not validate_cookies(cookie_input):
        print("⚠️  Proceeding with potentially incomplete cookies...")
    
    # Save cookies
    filename = save_cookies_to_env(cookie_input)
    
    print(f"\n✅ Success! Cookie file created: {filename}")
    print(f"📁 Full path: {os.path.abspath(filename)}")
    
    # Show next steps
    print("\n🚀 Next Steps:")
    print("1. Upload to server:")
    print(f"   scp -i ~/.ssh/sylectus_key {filename} root@157.245.242.222:/opt/sylectus-scraper/")
    print("2. Update server .env:")
    print(f"   ssh -i ~/.ssh/sylectus_key root@157.245.242.222 'cp /opt/sylectus-scraper/{filename} /opt/sylectus-scraper/.env'")
    print("3. Restart scraper:")
    print("   ssh -i ~/.ssh/sylectus_key root@157.245.242.222 'pkill -f api_scraper && cd /opt/sylectus-scraper && python3 api_scraper.py --startup > /tmp/scraper.log 2>&1 &'")

if __name__ == "__main__":
    main()