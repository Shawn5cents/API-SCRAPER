#!/bin/bash

# Simple script to run the Sylectus Telegram Monitor
# Clean production version

echo "🚀 Starting Sylectus Telegram Monitor"
echo "====================================="
echo ""
echo "📋 This will:"
echo "1. Login to Sylectus automatically"
echo "2. Monitor load board for new loads"
echo "3. Send detailed alerts to Telegram"
echo "4. Run continuously every 5 minutes"
echo ""
echo "⏹️  Press Ctrl+C anytime to stop"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your Telegram credentials"
    exit 1
fi

# Run the scraper
echo "🔄 Launching monitor..."
python scraper_complete.py