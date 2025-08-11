#!/bin/bash
# Start Thunderbird Email Load Monitor

echo "📧 Starting Thunderbird Email Load Monitor..."
echo "=" * 50

cd /home/nichols-ai/API-SCRAPER/API-SCRAPER
source venv/bin/activate

echo "📁 Email watch folder: $(pwd)/email_loads"
echo "💡 Save load emails as .eml files in the email_loads folder"
echo "🚀 Starting monitor..."

python3 -c "
from thunderbird_monitor import ThunderbirdLoadMonitor
monitor = ThunderbirdLoadMonitor()
monitor.start_monitoring()
"