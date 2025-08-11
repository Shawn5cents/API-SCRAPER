#!/bin/bash
# Complete Load Monitoring System
# Starts both Sylectus scraping AND email monitoring

echo "🚀 COMPLETE LOAD MONITORING SYSTEM"
echo "=================================="

cd /home/nichols-ai/API-SCRAPER/API-SCRAPER

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    exit 1
fi

source venv/bin/activate

echo "📋 Starting TWO monitoring systems:"
echo "1. 📡 Sylectus Fast Bidding System (API scraping)"
echo "2. 📧 Thunderbird Email Monitor (inbox watching)"
echo ""

# Start Fast Bidding System in background
echo "🚀 Starting Sylectus monitoring..."
python3 fast_bid_system.py --normal &
SYLECTUS_PID=$!

# Wait a moment
sleep 3

# Start Email Monitor in background  
echo "📧 Starting email monitoring..."
python3 -c "
from thunderbird_monitor import ThunderbirdLoadMonitor
monitor = ThunderbirdLoadMonitor()
monitor.start_monitoring()
" &
EMAIL_PID=$!

echo ""
echo "✅ BOTH SYSTEMS RUNNING!"
echo "📡 Sylectus monitoring PID: $SYLECTUS_PID" 
echo "📧 Email monitoring PID: $EMAIL_PID"
echo ""
echo "📱 Check Telegram for loads from BOTH sources:"
echo "   🔸 Sylectus API loads (with bidding buttons)"
echo "   🔸 Email loads (with reply buttons)"
echo ""
echo "📁 To add email loads: Save .eml files to email_loads/ folder"
echo "⌨️  Press Ctrl+C to stop both systems"

# Wait for user to stop
trap "echo '🛑 Stopping all monitoring...'; kill $SYLECTUS_PID $EMAIL_PID 2>/dev/null; exit 0" INT

# Keep script running
while true; do
    sleep 10
    # Check if processes are still running
    if ! kill -0 $SYLECTUS_PID 2>/dev/null; then
        echo "⚠️  Sylectus monitoring stopped unexpectedly"
    fi
    if ! kill -0 $EMAIL_PID 2>/dev/null; then
        echo "⚠️  Email monitoring stopped unexpectedly"  
    fi
done