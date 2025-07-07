# Playwright Website Scraper Setup Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install playwright requests python-dotenv
   playwright install
   ```

2. **Configure Environment**
   - Update `.env` file with your credentials:
   ```
   WEBSITE_USERNAME=your_username
   WEBSITE_PASSWORD=your_password
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_CHAT_ID=your_chat_id
   ```

3. **Run the Scraper**
   ```bash
   python playwright_scraper.py
   ```

## Detailed Setup Steps

### Step 1: Get Telegram Bot Credentials

1. **Create Bot:**
   - Talk to [@BotFather](https://t.me/BotFather) on Telegram
   - Use `/newbot` command
   - Save the Bot Token

2. **Get Chat ID:**
   - For personal chat: Use [@userinfobot](https://t.me/userinfobot)
   - For channel: Use `@channel_name` format
   - For group: Add [@RawDataBot](https://t.me/RawDataBot) to get ID

### Step 2: Record Actions with Playwright Codegen (Optional)

If you need to customize the scraper for a different website:

```bash
playwright codegen https://your-target-website.com/login
```

1. Perform login actions in the browser
2. Navigate to the page with items to scrape
3. Click on item containers to identify selectors
4. Copy the generated code for reference

### Step 3: Environment Variables

Update your `.env` file:

```bash
# Website Credentials
WEBSITE_USERNAME=your_username_here
WEBSITE_PASSWORD=your_password_here

# Telegram Configuration  
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Scraping Configuration
CHECK_INTERVAL=300  # 5 minutes
HEADLESS=true       # Set to false for debugging
WEBSITE_URL=https://your-website.com/login
```

### Step 4: Run and Monitor

```bash
# Run the scraper
python playwright_scraper.py

# Run in background (Linux/Mac)
nohup python playwright_scraper.py &

# Run with logging
python playwright_scraper.py 2>&1 | tee scraper.log
```

## Features

- ✅ **Automatic Login**: Uses username/password from environment
- ✅ **Duplicate Prevention**: Tracks sent items in `sent_items.txt`
- ✅ **Telegram Notifications**: Rich formatted messages
- ✅ **Error Handling**: Robust error recovery
- ✅ **Flexible Item Detection**: Multiple selector strategies
- ✅ **Data Extraction**: Title, price, location, date, links
- ✅ **Rate Limiting**: Prevents spam

## Customization

### Adding New Websites

1. Update `WEBSITE_URL` in `.env`
2. Test login flow with `playwright codegen`
3. Modify selectors in `extract_item_data()` method
4. Test with `HEADLESS=false` first

### Modifying Item Detection

Edit these arrays in `scrape_items()`:

```python
item_selectors = [
    '.your-item-class',
    '[data-item]',
    '.listing-row'
]
```

### Changing Message Format

Modify `format_item_message()` method to customize Telegram messages.

## Scheduling

### Linux/Mac (Cron)
```bash
# Edit crontab
crontab -e

# Run every 5 minutes
*/5 * * * * cd /path/to/scraper && python playwright_scraper.py

# Or run once and let it loop
@reboot cd /path/to/scraper && python playwright_scraper.py
```

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., every 5 minutes)
4. Set action: `python C:\path\to\playwright_scraper.py`

## Troubleshooting

### Common Issues

1. **Login Failed**
   - Check credentials in `.env`
   - Run with `HEADLESS=false` to see what's happening
   - Update selectors if website changed

2. **No Items Found**
   - Check if website structure changed
   - Use `playwright codegen` to identify new selectors
   - Verify you're on the correct page after login

3. **Telegram Messages Not Sending**
   - Verify bot token and chat ID
   - Check if bot is added to channel/group
   - Test with a simple message first

### Debug Mode

Set `HEADLESS=false` in `.env` to see the browser in action.

## Security Notes

- Never commit `.env` file to version control
- Use environment variables for sensitive data
- Keep bot token secure
- Consider using proxy if needed

## Performance Tips

- Adjust `CHECK_INTERVAL` based on how frequently items are posted
- Use `HEADLESS=true` for production
- Monitor resource usage if running continuously
- Consider running on a VPS for 24/7 monitoring