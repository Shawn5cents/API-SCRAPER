#!/usr/bin/env python3
"""
Simple test of hybrid scraper components
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_environment():
    """Test environment setup"""
    print("🔧 Testing environment...")
    
    # Check environment variables
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if bot_token and chat_id:
        print("✅ Telegram credentials found")
    else:
        print("❌ Missing Telegram credentials")
        return False
    
    return True

def test_telegram():
    """Test Telegram functionality"""
    print("📱 Testing Telegram...")
    
    import requests
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': '🧪 **Hybrid Scraper Test**\n\nTesting Telegram connectivity...'
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            print("✅ Telegram test successful")
            return True
        else:
            print(f"❌ Telegram test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

def test_mcp_client():
    """Test MCP client"""
    print("🔥 Testing MCP client...")
    
    try:
        from mcp_firecrawl_client import FirecrawlMCPClient
        
        client = FirecrawlMCPClient()
        print("✅ MCP client created")
        
        # Quick test
        if client.start_mcp_server():
            print("✅ MCP server started")
            client.stop_mcp_server()
            print("✅ MCP server stopped")
            return True
        else:
            print("❌ MCP server failed to start")
            return False
            
    except Exception as e:
        print(f"❌ MCP client error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Hybrid Scraper Component Tests...\n")
    
    tests = [
        ("Environment", test_environment),
        ("Telegram", test_telegram),
        ("MCP Client", test_mcp_client)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- Testing {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS:")
    print("="*50)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Hybrid scraper components are ready.")
    else:
        print("\n⚠️ Some tests failed. Check the issues above.")
    
    return all_passed

if __name__ == "__main__":
    main()