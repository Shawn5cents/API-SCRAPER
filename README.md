# Sylectus Load Board API Scraper

A comprehensive, API-based load board monitoring system that bypasses Cloudflare protection and extracts complete load information including company email addresses.

## 🚀 Features

- **Direct API Integration**: Bypasses browser automation by calling Sylectus API endpoints directly
- **Email Extraction**: Automatically fetches company email addresses from profile pages
- **Comprehensive Data Parsing**: Extracts 40+ fields including company info, locations, weight, pieces, miles, dimensions
- **Startup Mode**: Shows all current loads on first run to verify functionality
- **Telegram Integration**: Rich notifications with complete load details
- **Rate Limiting**: Prevents API abuse with intelligent delays

## 📋 Requirements

- Python 3.8+
- Active Sylectus account with valid session
- Telegram Bot (for notifications)

## 🛠 Installation

1. Clone the repository:
```bash
git clone https://github.com/Shawn5cents/API-SCRAPER.git
cd API-SCRAPER
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## ⚙️ Configuration

### Environment Variables (.env)
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
CHECK_INTERVAL=120  # Seconds between checks
```

### Session Setup
1. Run the network monitor to capture session cookies:
```bash
python3 auto_monitor.py
```

2. Log into Sylectus manually in the opened browser
3. Navigate to the load board
4. The script will automatically save your session cookies

## 🚀 Usage

### Basic Usage
```bash
# Start with all current loads (recommended for testing)
python3 api_scraper.py --startup

# Start in normal mode (only new loads)
python3 api_scraper.py --normal
```

### Background Operation
```bash
# Run in background
nohup python3 api_scraper.py --startup > scraper.log 2>&1 &

# Check status
ps aux  < /dev/null |  grep api_scraper

# View logs
tail -f scraper.log
```

## 📊 Sample Output

### Telegram Notification
```
🆕 NEW SYLECTUS LOAD

🏢 Company: Nolan Transportation Group, Inc
🆔 Load ID: 567093

📍 PICKUP:
   📍 MORRISVILLE, NC
   📅 07/06/2025 21:57

📍 DELIVERY:
   📍 ATLANTA, GA
   📅 07/06/2025 22:27

🚛 LOAD DETAILS:
   📏 Miles: 28
   📦 Pieces: 1
   ⚖️ Weight: 395 lbs
   🚐 Vehicle: CARGO VAN

💰 Est. Rate: $1800

PAYMENT INFO:
💳 Credit Score: 82%
📅 Payment Terms: 44 days

CONTACT INFO:
📧 Email: victoria.mcbroom@ntgfreight.com

✅ Email Available

⏰ Found: 21:00
🌐 Via API Scraper
```

## 🧪 Testing

```bash
# Test complete flow
python3 test_complete_flow.py

# Test email extraction
python3 test_email_extraction.py

# Debug mode
python3 debug_scraper.py
```

## 🐛 Troubleshooting

**"No cookies found"**
- Run `auto_monitor.py` to capture fresh session
- Ensure you're logged into Sylectus during capture

**"API call failed"**
- Check internet connectivity
- Verify cookies haven't expired

**"Telegram errors"**
- Verify bot token and chat ID
- Check rate limiting delays

## 📈 Performance

- **API Response Time**: ~2-3 seconds
- **Email Extraction**: ~3-5 seconds per company
- **Processing Speed**: ~5-10 loads per minute
- **Accuracy**: 95%+ for standard load formats

## ⚠️ Disclaimer

This tool is for educational and personal use only. Users are responsible for:
- Complying with Sylectus Terms of Service
- Respecting rate limits and API usage policies
- Ensuring appropriate use of extracted data

---

**Built with ❤️ for the logistics community**
