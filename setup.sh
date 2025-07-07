#!/bin/bash

# Sylectus Monitor - Development Environment Setup Script
# This script sets up a reproducible development environment

set -e  # Exit on any error

echo "🚀 Setting up Sylectus Monitor development environment..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python $(python3 --version) found"

# Check if Node.js is available (required for Firecrawl MCP)
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "✅ Node.js $(node --version) found"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed. Please install npm."
    exit 1
fi

echo "✅ npm $(npm --version) found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers (just Chromium for headless operation)
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Install Playwright system dependencies
echo "🔧 Installing Playwright system dependencies..."
playwright install-deps chromium || echo "⚠️ Could not install system dependencies. You may need to run this with sudo or install manually."

# Check if Firecrawl MCP is available globally
echo "🔥 Checking Firecrawl MCP availability..."
if ! command -v npx &> /dev/null; then
    echo "❌ npx is required but not available. Please ensure Node.js is properly installed."
    exit 1
fi

# Test if firecrawl-mcp package can be accessed
echo "🔥 Testing Firecrawl MCP package availability..."
npx firecrawl-mcp --help &> /dev/null || echo "⚠️ Firecrawl MCP may need to be installed. It will be installed on first use via npx."

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo "📁 Creating data directory..."
    mkdir -p data
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ No .env file found. Creating from template..."
    cp .env.template .env
    echo "📝 Please edit .env file with your actual credentials before running the script."
else
    echo "✅ .env file exists"
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   - Sylectus login credentials"
echo "   - Telegram bot token and chat ID"
echo "   - Firecrawl API key"
echo ""
echo "2. Test the setup:"
echo "   source venv/bin/activate"
echo "   python test_browser.py"
echo ""
echo "3. Run the hybrid scraper:"
echo "   source venv/bin/activate"
echo "   python hybrid_scraper.py"
echo ""
echo "🔗 Useful links:"
echo "   - Telegram Bot Creation: https://t.me/BotFather"
echo "   - Get Chat ID: https://t.me/userinfobot"
echo "   - Firecrawl API: https://firecrawl.dev/"
echo ""
