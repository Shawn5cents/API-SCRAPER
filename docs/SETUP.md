# Sylectus Load Monitor Setup with OmniParser

## What This Extension Does

✅ **Takes screenshots** of your Sylectus load board  
✅ **Uses OmniParser V2 AI** to extract load data from screenshots  
✅ **Sends to Telegram** with all required fields:
- Pickup city & state + date/time
- Delivery city & state + date/time  
- Vehicle type (cargo van/sprinter)
- Miles, weight, pieces
- Company name and contact info

✅ **First run**: Sends all current loads  
✅ **Ongoing**: Only sends new loads every 2 minutes  
✅ **Fallback**: Uses table parsing if OmniParser fails

## Setup Steps

### 1. Get Replicate API Key

1. Go to https://replicate.com
2. Sign up/login
3. Go to Account Settings → API Tokens
4. Create a new token
5. Copy the token (starts with `r8_`)

### 2. Update Extension

1. Open `browser-extension/content.js`
2. Find line 924: `'Authorization': 'Token r8_YOUR_REPLICATE_API_KEY_HERE'`
3. Replace `r8_YOUR_REPLICATE_API_KEY_HERE` with your actual API key

### 3. Load Extension in Chrome

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (top right)
4. Click "Load unpacked"
5. Select the `browser-extension` folder
6. Pin the extension to your toolbar

### 4. Use Extension

1. Navigate to your Sylectus load board
2. Make sure loads are visible
3. Click the extension icon to start monitoring
4. Check your Telegram for load alerts!

## How It Works

1. **Screenshot Method**: Takes screenshot → Sends to OmniParser AI → Extracts structured data → Sends to Telegram
2. **Fallback Method**: If screenshot fails, tries traditional table parsing
3. **Auto-refresh**: Refreshes every 2 minutes to stay active

## Troubleshooting

- **No loads detected**: Check console logs, ensure you're on the right page
- **API errors**: Verify your Replicate API key is correct
- **Telegram not working**: Check Telegram token and chat ID
- **Extension not loading**: Check console for JavaScript errors

## Cost

- OmniParser on Replicate: ~$0.01-0.05 per screenshot
- For monitoring every 2 minutes: ~$0.50-2.50 per day
- Much cheaper than manual monitoring!

## Security

✅ **Your data stays secure** - only screenshots are sent to OmniParser  
✅ **No login credentials** stored or transmitted  
✅ **Open source** - you can review all code  
✅ **No third-party extensions** with unknown security

Ready to monitor loads automatically!