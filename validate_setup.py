#!/usr/bin/env python3
"""
Sylectus Monitor - Setup Validation Script
Validates all required credentials and dependencies
"""

import os
import sys
import subprocess
import requests
from dotenv import load_dotenv

def check_python_packages():
    """Check if all required Python packages are installed"""
    print("🐍 Checking Python packages...")
    
    required_packages = [
        'playwright', 'requests', 'beautifulsoup4', 
        'python-dotenv', 'selenium', 'aiohttp',
        'python-telegram-bot', 'httpx'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'beautifulsoup4':
                __import__('bs4')
            elif package == 'python-dotenv':
                __import__('dotenv')
            elif package == 'python-telegram-bot':
                __import__('telegram')
            else:
                __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All Python packages installed")
    return True

def check_system_dependencies():
    """Check system dependencies"""
    print("\n🔧 Checking system dependencies...")
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ Node.js {result.stdout.strip()}")
        else:
            print("  ❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("  ❌ Node.js not found")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✅ npm {result.stdout.strip()}")
        else:
            print("  ❌ npm not found")
            return False
    except FileNotFoundError:
        print("  ❌ npm not found")
        return False
    
    # Check Playwright browsers
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                browser.close()
                print("  ✅ Playwright Chromium browser")
            except Exception as e:
                print(f"  ❌ Playwright Chromium browser: {e}")
                return False
    except Exception as e:
        print(f"  ❌ Playwright issue: {e}")
        return False
    
    print("✅ All system dependencies available")
    return True

def check_firecrawl_mcp():
    """Check Firecrawl MCP availability"""
    print("\n🔥 Checking Firecrawl MCP...")
    
    try:
        result = subprocess.run(['npx', 'firecrawl-mcp', '--help'], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("  ✅ Firecrawl MCP available")
            return True
        else:
            print(f"  ❌ Firecrawl MCP issue: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("  ⚠️ Firecrawl MCP check timed out (may still work)")
        return True
    except Exception as e:
        print(f"  ❌ Firecrawl MCP error: {e}")
        return False

def validate_credentials():
    """Validate environment variables and credentials"""
    print("\n🔐 Checking credentials...")
    
    load_dotenv()
    
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
    ]
    
    optional_vars = [
        'SYLECTUS_CORPORATE_ID',
        'SYLECTUS_CORPORATE_PASSWORD', 
        'SYLECTUS_USERNAME',
        'SYLECTUS_USER_PASSWORD',
        'FIRECRAWL_API_KEY'
    ]
    
    missing_required = []
    missing_optional = []
    
    # Check required credentials
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"  ✅ {var}")
        else:
            print(f"  ❌ {var}")
            missing_required.append(var)
    
    # Check optional credentials
    for var in optional_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"  ✅ {var}")
        else:
            print(f"  ⚠️ {var} (recommended)")
            missing_optional.append(var)
    
    if missing_required:
        print(f"\n❌ Missing required credentials: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n⚠️ Missing optional credentials: {', '.join(missing_optional)}")
    
    print("✅ Required credentials configured")
    return True

def test_telegram_connection():
    """Test Telegram bot connection"""
    print("\n📱 Testing Telegram connection...")
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("  ⚠️ Skipping - credentials not configured")
        return True
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_name = bot_info['result']['username']
                print(f"  ✅ Bot connected: @{bot_name}")
                
                # Test sending a message
                test_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                test_data = {
                    'chat_id': chat_id,
                    'text': '🧪 Setup validation test - Sylectus Monitor'
                }
                
                test_response = requests.post(test_url, data=test_data, timeout=10)
                if test_response.status_code == 200:
                    print("  ✅ Test message sent successfully")
                    return True
                else:
                    print(f"  ❌ Failed to send test message: {test_response.status_code}")
                    return False
            else:
                print(f"  ❌ Bot API error: {bot_info}")
                return False
        else:
            print(f"  ❌ Bot connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Telegram test error: {e}")
        return False

def main():
    """Main validation function"""
    print("🔍 Sylectus Monitor - Setup Validation")
    print("=" * 50)
    
    checks = [
        check_python_packages(),
        check_system_dependencies(),
        check_firecrawl_mcp(),
        validate_credentials(),
        test_telegram_connection()
    ]
    
    print("\n" + "=" * 50)
    
    if all(checks):
        print("🎉 All checks passed! Setup is ready.")
        print("\n🚀 You can now run:")
        print("   python hybrid_scraper.py")
        return 0
    else:
        failed_count = len([c for c in checks if not c])
        print(f"❌ {failed_count} check(s) failed. Please fix the issues above.")
        print("\n📖 See SETUP.md for detailed instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
