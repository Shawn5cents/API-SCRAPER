#!/bin/bash

echo "🚀 Starting Hybrid Sylectus Monitor"
echo "===================================="
echo ""
echo "📋 This will:"
echo "1. Login to Sylectus using Playwright"
echo "2. Extract load data using Firecrawl MCP"
echo "3. Send enhanced alerts to Telegram"
echo "4. Run continuously with improved reliability"
echo ""
echo "⏹️  Press Ctrl+C anytime to stop"
echo ""

# Check if we're in the right directory
if [ ! -f "hybrid_scraper.py" ]; then
    echo "❌ hybrid_scraper.py not found. Please run from the correct directory."
    exit 1
fi

# Check environment file
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your Telegram credentials."
    exit 1
fi

# Set environment variables for headless operation
export DISPLAY=""
export PLAYWRIGHT_BROWSERS_PATH=""

echo "🔧 Configuring headless environment..."

# Install Playwright browsers if needed
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    echo "📥 Installing Playwright browsers..."
    python -m playwright install chromium
fi

echo "🔄 Launching hybrid monitor..."
echo ""

# Run the hybrid scraper with proper error handling
python -u hybrid_scraper.py 2>&1 | while IFS= read -r line; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') $line"
done