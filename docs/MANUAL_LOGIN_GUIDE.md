# Manual Login Scraper Guide

## 🎯 Perfect Solution for CloudFlare & Login Issues

This approach uses **you** to handle CloudFlare verification and login, then keeps the session active for automated monitoring.

## ✅ Quick Start

```bash
# Make sure you're in the right directory
cd /home/nichols-ai/sylectus-monitor

# Run the scraper
./run_manual_scraper.sh
```

## 🔄 How It Works

1. **Browser Opens**: Script opens a visible browser window
2. **Manual Login**: You handle CloudFlare + login manually  
3. **Navigation**: You navigate to the load board page
4. **Automation Starts**: Script takes over and monitors automatically
5. **Session Maintained**: Browser stays open, session stays active

## 📋 Step-by-Step Process

### Step 1: Start the Script
```bash
./run_manual_scraper.sh
```

### Step 2: Complete Manual Setup
When browser opens:
1. ✅ Complete any CloudFlare verification
2. ✅ Login with your Sylectus credentials  
3. ✅ Navigate to the load board page
4. ✅ Verify you can see the loads/items
5. ✅ Press ENTER in the terminal

### Step 3: Automated Monitoring
The script will now:
- ✅ Refresh the page every 5 minutes
- ✅ Scan for new loads automatically  
- ✅ Send Telegram alerts for new items
- ✅ Prevent duplicate notifications
- ✅ Keep session active

## 🔧 Configuration

Edit your `.env` file:
```bash
# Telegram Configuration (Required)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Check interval in seconds (Default: 300 = 5 minutes)
CHECK_INTERVAL=300
```

## 🚀 Production Use

### Run in Background
```bash
# Run with logging
nohup ./run_manual_scraper.sh > scraper.log 2>&1 &

# Check if running
ps aux | grep scraper_manual_login
```

### Monitor Logs
```bash
# Watch live logs
tail -f scraper.log

# Check recent activity
tail -20 scraper.log
```

## 🛠️ Troubleshooting

### Browser Closes Accidentally
- Just restart the script
- Complete manual login again
- Monitoring resumes

### No Loads Found
- Check browser window - make sure you're on load board
- Verify loads are visible on the page
- Check `debug_screenshot_*.png` files

### Telegram Messages Not Sending
- Verify bot token and chat ID in `.env`
- Test with a simple message first
- Check network connectivity

## 📱 Expected Telegram Notifications

```
🆕 NEW SYLECTUS LOAD

🏢 Company: ABC LOGISTICS LLC

📍 PICKUP: CHICAGO, IL
📍 DELIVERY: ATLANTA, GA

📏 Miles: 587
⚖️ Weight: 26000 lbs

🔗 Link: https://www.sylectus.net/...

📊 Raw Data: ABC LOGISTICS LLC | CHICAGO, IL | ATLANTA, GA | 587 mi | 26000 lbs

⏰ Found: 2:30 PM

🌐 Via Manual Login Scraper
```

## 🔄 Scheduling Options

### Option 1: Keep Browser Open (Recommended)
- Run the script once
- Let it monitor continuously
- Most reliable for maintaining session

### Option 2: Cron Job (Advanced)
```bash
# Edit crontab
crontab -e

# Run every hour (you'll need to login each time)
0 * * * * cd /home/nichols-ai/sylectus-monitor && ./run_manual_scraper.sh
```

## 🎯 Advantages of This Approach

✅ **Bypasses CloudFlare**: You handle verification manually
✅ **Maintains Session**: Browser stays logged in  
✅ **Reliable**: No automation detection issues
✅ **Flexible**: You control when monitoring starts
✅ **Debug Friendly**: Can see exactly what's happening

## 🔒 Security Notes

- Browser window stays open (don't leave unattended on shared computers)
- Session cookies are maintained in browser
- Telegram credentials stored in `.env` file
- No passwords stored in scripts

## ⚡ Performance Tips

- Close other browser windows to save memory
- Monitor system resources if running 24/7
- Consider running on a dedicated VPS
- Use `screen` or `tmux` for persistent sessions

## 🎉 Ready to Go!

Your scraper is now set up following the exact plan structure with the perfect solution for CloudFlare and login challenges!