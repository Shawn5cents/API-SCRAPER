#!/bin/bash
# Fast Bidding System Quick Startup Script
# Run this script to start the system after computer boot

echo "🚀 Starting Fast Bidding System..."
echo "=================================="

# Change to the project directory
cd /home/nichols-ai/API-SCRAPER/API-SCRAPER

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your Telegram bot credentials"
    exit 1
fi

# Check if session cookies exist
if [ ! -f "extracted_cookies_latest.env" ]; then
    echo "⚠️  No session cookies found!"
    echo "🔧 Starting session capture..."
    echo "📝 You'll need to log into Sylectus manually in the browser"
    echo ""
    read -p "Press Enter to start session capture (or Ctrl+C to exit)..."
    python3 auto_monitor.py
    
    # After session capture, copy the latest cookies
    LATEST_COOKIE=$(ls -t extracted_cookies_*.env | grep -v latest | head -n 1)
    if [ -n "$LATEST_COOKIE" ]; then
        cp "$LATEST_COOKIE" extracted_cookies_latest.env
        echo "✅ Session cookies updated!"
    else
        echo "❌ Session capture failed!"
        exit 1
    fi
fi

# Test session validity
echo "🧪 Testing session validity..."
python3 -c "
from bidding_scraper import BiddingSylectusAPIClient
client = BiddingSylectusAPIClient()
try:
    loads = client.get_loads()
    print(f'✅ Session valid - ready to monitor!')
except Exception as e:
    print(f'❌ Session invalid: {e}')
    exit(1)
" || {
    echo "⚠️  Session expired or invalid!"
    echo "🔧 Need to refresh session cookies..."
    echo ""
    read -p "Run session capture now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 auto_monitor.py
        # Copy latest cookies after capture
        LATEST_COOKIE=$(ls -t extracted_cookies_*.env | grep -v latest | head -n 1)
        if [ -n "$LATEST_COOKIE" ]; then
            cp "$LATEST_COOKIE" extracted_cookies_latest.env
            echo "✅ Session cookies refreshed!"
        fi
    else
        echo "❌ Cannot start without valid session!"
        exit 1
    fi
}

echo ""
echo "🎯 Starting Fast Bidding System in normal mode..."
echo "📱 Check your Telegram for load notifications!"
echo "💡 Press Ctrl+C to stop the system"
echo ""

# Start the Fast Bidding System
python3 fast_bid_system.py --normal