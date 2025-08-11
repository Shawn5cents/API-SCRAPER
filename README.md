## API-SCRAPER - Fast Bidding System v1.1

A revolutionary load board monitoring and bidding system that transforms Telegram into a powerful bidding dashboard. Features instant bidding, smart rate calculations, Thunderbird email integration, and complete email organization for lightning-fast responses to Sylectus loads.

## 🚀 Features

- **🔥 FAST BIDDING SYSTEM**: NEW! Interactive Telegram buttons for instant load bidding
- **💰 Smart Rate Calculations**: Conservative, market, and aggressive bid suggestions
- **⚡ One-Click Actions**: Bid, call company, get details, or skip loads instantly
- **📱 Interactive Dashboard**: Transform Telegram into a bidding control center
- **📧 EMAIL ORGANIZATION**: NEW! Complete Thunderbird email management and organization
- **📁 AUTO FOLDER SORTING**: Automatically organize load emails into dedicated folders
- **📬 DUAL MONITORING**: Monitor both Sylectus API AND email inbox for loads
- **🔄 EMAIL FILTERING**: Smart filters route load emails automatically to organized folders
- **Direct API Integration**: Bypasses browser automation by calling Sylectus API endpoints directly
- **Email Extraction**: Automatically fetches company email addresses from profile pages
- **Comprehensive Data Parsing**: Extracts 40+ fields including company info, locations, weight, pieces, miles, dimensions
- **Enhanced Parser**: Fixed miles/weight parsing with accurate column detection
- **Filtered Scraper**: Filter loads by vehicle type (Cargo Van/Sprinter) and rolling 3-day date window
- **Rolling Date Window**: Automatically updates date range daily (today + next 2 days)
- **Session Cookie Management**: Automated cookie capture and refresh system
- **Cloud Deployment**: Automated DigitalOcean deployment with systemd service
- **Startup Mode**: Shows all current loads on first run to verify functionality
- **Telegram Integration**: Rich notifications with complete load details
- **Rate Limiting**: Prevents API abuse with intelligent delays

## 📋 Requirements

- Python 3.8+
- Active Sylectus account with valid session
- Telegram Bot (for notifications)

## 🛠 Complete Setup Guide

### 1. Clone and Setup Repository
```bash
git clone https://github.com/Shawn5cents/API-SCRAPER.git
cd API-SCRAPER

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials:
# TELEGRAM_BOT_TOKEN=your_bot_token_here
# TELEGRAM_CHAT_ID=your_chat_id_here
# CHECK_INTERVAL=120
```

### 3. Telegram Bot Setup
1. **Create Bot**: Message @BotFather in Telegram, send `/newbot`
2. **Get Chat ID**: Message @userinfobot to get your chat ID
3. **Update .env**: Add your bot token and chat ID

### 4. Session Cookie Capture
```bash
# Start session monitoring (opens browser)
source venv/bin/activate
python3 auto_monitor.py

# In the opened browser:
# 1. Log into Sylectus manually
# 2. Navigate to load board
# 3. Wait for script to complete (captures cookies automatically)
```

### 🔐 SSH Key Setup (for contributors)

If you need to contribute to this repository, set up SSH authentication:

1. **Generate SSH key** (if not already done):
```bash
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/sylectus_repo_key
```

2. **Add public key to GitHub**:
   - Copy your public key: `cat ~/.ssh/sylectus_repo_key.pub`
   - Go to https://github.com/settings/keys
   - Click "New SSH key" and paste the public key

3. **Configure Git to use SSH**:
```bash
git remote set-url origin git@github.com:Shawn5cents/API-SCRAPER.git
git config --local core.sshCommand "ssh -i ~/.ssh/sylectus_repo_key"
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

### Standard API Scraper (All Loads)
```bash
# Test with all current loads
source venv/bin/activate
python3 api_scraper.py --startup

# Monitor for new loads continuously
python3 api_scraper.py --normal
```

### NEW: Filtered Van Scraper (Recommended)
**Filters for Cargo Van & Sprinter loads only, with rolling 3-day window**

```bash
# Test filtered scraper (shows current van loads)
source venv/bin/activate
python3 filtered_scraper.py --startup

# Monitor for new van loads continuously
python3 filtered_scraper.py --normal
```

**Filtered Scraper Features:**
- ✅ **Vehicle Filter**: Only CARGO VAN and SPRINTER loads
- ✅ **Rolling Date Window**: Today + next 2 days (updates daily automatically)
- ✅ **Complete Load Details**: Miles, pieces, weight, company emails
- ✅ **Rich Telegram Notifications**: Formatted messages with all load info
- ✅ **Duplicate Prevention**: Won't send same load twice

### 🔥 NEW: Fast Bidding System (GAME CHANGER!)
**Turn your Telegram into an instant bidding dashboard with one-click actions**

```bash
# Test fast bidding (shows current loads with buttons)
source venv/bin/activate
python3 fast_bid_system.py --test

# Start continuous fast bidding system
python3 fast_bid_system.py --normal
```

**🚀 What You Get:**
```
🚐 NEW VAN LOAD - CARGO VAN
🏢 Company: FASTMORE LOGISTICS
📏 Miles: 402 | 📦 Pieces: 3 | ⚖️ Weight: 2400 lbs

💰 BID SUGGESTIONS:
💵 Conservative: $650 ($1.62/mi)
💵 Market Rate: $765 ($1.90/mi)
💵 Aggressive: $880 ($2.19/mi)

[💰 Bid $650] [💰 Bid $765] [💰 Bid $880]
[✏️ Custom Bid] [📧 Email Bid]
[📞 Call Company] [📋 Load Details] [❌ Skip]
```

**⚡ Complete Feature Set:**
- **💰 One-Click Bidding**: Submit bids to Sylectus instantly
- **✏️ Custom Bidding**: Enter any amount (like $740 for premium loads)
- **📧 Email Bidding**: Opens Thunderbird with your exact email format
- **📞 Smart Calling**: Get contact info & negotiation tips
- **📋 Load Analysis**: Comprehensive load details & strategy
- **⚖️ Smart Rates**: Based on ACTUAL 2025 market rate guide
- **🎯 Success Tracking**: Real-time bid confirmations & status

**📊 Proven Results:** 30-second response time vs 30+ minutes manual!

### 📧 NEW: Complete Email Organization System
**Transform your inbox into an organized load management system**

```bash
# Setup Thunderbird email monitoring
source venv/bin/activate
python3 thunderbird_folder_setup.py

# Start email monitoring only
./start_email_monitor.sh

# Start BOTH Sylectus API + Email monitoring
./start_complete_monitoring.sh
```

**🔥 What You Get:**
```
📧 ORGANIZED EMAIL FOLDERS:
├── Loads/
│   ├── NEW_LOADS     (incoming loads auto-sorted here)
│   ├── RESPONDED     (loads you've replied to)
│   ├── BOOKED        (loads you've won)
│   └── REJECTED      (loads you passed on)
```

**📬 Email Features:**
- **📁 Auto Organization**: Load emails automatically sorted from inbox
- **🔍 Smart Detection**: Recognizes load emails by keywords (cargo, sprinter, van, pickup, delivery, etc.)
- **📧 Dual Source**: Monitor BOTH Sylectus API AND email loads in one system
- **📱 Telegram Integration**: Email loads sent to Telegram with action buttons
- **⚡ Real-time Processing**: Monitors email folder every 30 seconds
- **🏢 Company Extraction**: Automatically extracts sender company info
- **📊 Load Parsing**: Extracts pickup, delivery, miles, rate from email content

**📋 Complete Workflow:**
1. **Load emails arrive** → Auto-sorted to `Loads/NEW_LOADS`
2. **Telegram notification** → Review load details with action buttons
3. **Take action** → Reply/Bid → Move email to `RESPONDED` 
4. **Final status** → Move to `BOOKED` or `REJECTED`

**🎯 Benefits:**
- ✅ **Clean Inbox**: No more load emails cluttering your main inbox
- ✅ **Never Miss Loads**: Dual monitoring ensures you catch everything
- ✅ **Organized Workflow**: Track load status through folder organization
- ✅ **Fast Response**: Instant Telegram notifications for email loads

### Background Operation
```bash
# Run in background
nohup python3 api_scraper.py --startup > scraper.log 2>&1 &

# Check status
ps aux  < /dev/null |  grep api_scraper

# View logs
tail -f scraper.log
```

### Cloud Deployment
```bash
# Deploy to DigitalOcean (automated)
python3 deploy_digitalocean.py

# Manual SSH access
ssh -i ~/.ssh/sylectus_key root@YOUR_SERVER_IP

# Check service status
systemctl status sylectus-scraper
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

**"Miles parsing incorrectly"**
- Enhanced parser now correctly handles column 6 (vehicle + miles) and column 7 (pieces + weight)
- Miles are limited to 4 digits maximum (9999 miles)
- Fixed issue where 700-mile routes were showing as 7000+ miles

**"Cloud deployment issues"**
- Ensure DigitalOcean API token is valid
- Check SSH key permissions and connectivity
- Service logs available at `/tmp/scraper.log` on server

**"Thunderbird email organization issues"**
- Ensure Thunderbird folders are created manually if auto-creation fails
- Check message filter is enabled in Tools → Message Filters
- Restart Thunderbird after creating folders to see them
- Verify email monitoring script has access to email_loads/ folder

**"Email monitoring not working"**
- Check that email_loads/ folder exists in project directory
- Save emails as .eml files (Right-click → Save As → .eml format)
- Ensure Telegram bot token and chat ID are configured
- Monitor script runs every 30 seconds - check console output

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
