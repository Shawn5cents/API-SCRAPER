# Sylectus Load Monitor - Testing & Debugging Guide

## Current Status ✅

**The extension is fully configured and ready to use!** Here's what's working:

### ✅ Features Implemented
- **OmniParser V2 AI** for intelligent screenshot analysis
- **Aggressive email filtering** to get POSTER emails only (not your email)
- **First run sends ALL current loads**, then only NEW loads
- **Company profile clicking** to extract real contact emails
- **Comprehensive data extraction** - captures ALL available fields
- **Telegram notifications** with detailed load information
- **Auto-refresh** every 2 minutes to keep session active

### ✅ User Email Protection
The extension now filters out:
- `snichols@gmail.com` (your specific email)
- Any email containing `snichols`
- Any email containing `nichols-ai`
- Generic emails (`support@`, `admin@`, `noreply@`, `info@`)

## Quick Start

### 1. Load Extension
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" 
4. Select the `browser-extension` folder
5. Pin the extension to your toolbar

### 2. Start Monitoring
1. Go to your Sylectus load board page
2. Make sure loads are visible in the table
3. Click the extension icon to start monitoring
4. Check Telegram for load alerts!

## Testing Scripts

### Basic Test (Run in browser console)
```javascript
// Copy and paste this into your browser console on the Sylectus page
if (window.sylectusMonitor) {
    console.log('✅ Extension loaded');
    console.log('State:', {
        monitoring: window.sylectusMonitor.isMonitoring,
        firstRun: window.sylectusMonitor.isFirstRun,
        loads: window.sylectusMonitor.knownLoads.size
    });
    
    // Test manual scan
    window.sylectusMonitor.scanForLoads();
} else {
    console.log('❌ Extension not loaded');
}
```

### Comprehensive Test
Load `/browser-extension/comprehensive-test.js` in your browser console for full testing.

### Verbose Debugging
Load `/browser-extension/debug-verbose.js` for detailed logging during operation.

## Expected Behavior

### First Run
1. Extension sends **ALL current loads** visible on the page
2. Gets poster emails by clicking company names (first 5 loads)
3. Sends comprehensive load data to Telegram
4. Marks all current loads as "known"
5. Switches to "new loads only" mode

### Subsequent Runs (every 2 minutes)
1. Refreshes the load board
2. Scans for **NEW loads only**
3. Gets poster emails for new loads
4. Sends only new load alerts to Telegram

## Telegram Message Format

Each load alert includes:
- 🏢 Company name and contact info
- 📍 Pickup location, date, and time
- 📍 Delivery location, date, and time
- 🚐 Vehicle type and size
- 📏 Miles, weight, pieces, dimensions
- 📧 **POSTER'S email** (not yours!)
- 📞 Phone number (if found)
- 📅 Post date and expiration
- 🔍 All extracted fields
- 📊 Raw data for debugging

## Troubleshooting

### No loads detected
- Ensure you're on the load board page with visible loads
- Check browser console for error messages
- Try the comprehensive test script

### Wrong email showing
- The extension now aggressively filters your email
- If you still see your email, check console logs
- The extension should show "All emails filtered" if only your email is found

### Extension not starting
- Check that you're on a Sylectus page
- Look for the extension icon in your toolbar
- Open Developer Tools and check console for errors

### No Telegram messages
- Verify your Telegram bot token and chat ID
- Check network tab for API call failures
- Test Telegram manually with the debug script

## Success Indicators

You'll know it's working when you see:
- ✅ "Extension loaded" in console
- 📸 Screenshots being taken
- 🤖 OmniParser processing messages
- 📧 Email extraction attempts
- 📱 Telegram message confirmations

## Cost Estimate

- OmniParser: ~$0.01-0.05 per screenshot
- Monitoring every 2 minutes: ~$0.50-2.50 per day
- Much cheaper than manual monitoring!

## Next Steps

1. **Test the extension** using the scripts above
2. **Start monitoring** by clicking the extension icon
3. **Check Telegram** for load alerts
4. **Let it run** - it will automatically refresh and monitor

The extension is designed to work autonomously once started. It will:
- Send all current loads on first run
- Then monitor for new loads every 2 minutes
- Extract real poster contact information
- Keep your session active with auto-refresh

**Ready to monitor loads automatically!** 🚀