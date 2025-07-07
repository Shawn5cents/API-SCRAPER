# Sylectus Monitor - Setup Guide

This guide will help you set up a reproducible development environment for the Sylectus Monitor application that scrapes load board data and sends notifications via Telegram.

## 🎯 Prerequisites

### Required Software
- **Python 3.8+** - Programming language runtime
- **Node.js 16+** - Required for Firecrawl MCP server
- **npm** - Node.js package manager
- **Git** - Version control (optional but recommended)

### Required Credentials
1. **Sylectus Login Credentials**
   - Corporate ID
   - Corporate Password
   - Username
   - User Password

2. **Telegram Bot Token & Chat ID**
   - Bot token from @BotFather
   - Your personal chat ID

3. **Firecrawl API Key**
   - API key from firecrawl.dev

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Clone or navigate to the project directory
cd sylectus-monitor

# Run the automated setup script
./setup.sh

# Edit the .env file with your credentials
nano .env
```

### Option 2: Manual Setup

1. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Python Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Install Playwright Browsers**
   ```bash
   playwright install chromium
   playwright install-deps chromium
   ```

4. **Create Environment File**
   ```bash
   cp .env.template .env
   # Edit .env with your credentials
   ```

5. **Create Data Directory**
   ```bash
   mkdir -p data
   ```

## 🔐 Credential Setup

### 1. Sylectus Credentials

Contact your Sylectus administrator to obtain:
- Corporate ID (numerical)
- Corporate Password
- Your username
- Your user password

Add these to your `.env` file:
```env
SYLECTUS_CORPORATE_ID="your_corporate_id"
SYLECTUS_CORPORATE_PASSWORD="your_password"
SYLECTUS_USERNAME="your_username"
SYLECTUS_USER_PASSWORD="your_user_password"
```

### 2. Telegram Bot Setup

1. **Create a Bot:**
   - Open Telegram and message @BotFather
   - Send `/newbot` command
   - Follow instructions to create your bot
   - Save the bot token

2. **Get Your Chat ID:**
   - Message @userinfobot in Telegram
   - It will reply with your chat ID

3. **Add to .env:**
   ```env
   TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   TELEGRAM_CHAT_ID="987654321"
   ```

### 3. Firecrawl API Key

1. **Sign up at https://firecrawl.dev/**
2. **Get your API key from the dashboard**
3. **Add to .env:**
   ```env
   FIRECRAWL_API_KEY="fc-your-api-key-here"
   ```

## 🧪 Testing the Setup

### Test Browser Automation
```bash
source venv/bin/activate
python test_browser.py
```

### Test Telegram Connection
```bash
source venv/bin/activate
python -c "
import os
from dotenv import load_dotenv
import requests

load_dotenv()
token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

url = f'https://api.telegram.org/bot{token}/sendMessage'
data = {'chat_id': chat_id, 'text': '🧪 Test message from Sylectus Monitor'}
response = requests.post(url, data=data)
print('✅ Telegram test successful!' if response.status_code == 200 else '❌ Telegram test failed!')
"
```

### Test Firecrawl (requires API key)
```bash
source venv/bin/activate
python -c "
import subprocess
import sys
try:
    result = subprocess.run(['npx', 'firecrawl-mcp', '--help'], 
                          capture_output=True, text=True, timeout=10)
    print('✅ Firecrawl MCP available!' if result.returncode == 0 else '❌ Firecrawl MCP issue!')
except Exception as e:
    print(f'⚠️ Firecrawl test issue: {e}')
"
```

## 🏃‍♂️ Running the Application

### Local Development
```bash
source venv/bin/activate
python hybrid_scraper.py
```

### Background Process
```bash
source venv/bin/activate
nohup python hybrid_scraper.py > output.log 2>&1 &
```

## 🐳 Docker Deployment

### Build and Run with Docker Compose
```bash
# Build the container
docker-compose build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Manual Docker Commands
```bash
# Build image
docker build -t sylectus-monitor .

# Run container
docker run -d \
  --name sylectus-monitor \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  sylectus-monitor
```

## 📁 Project Structure

```
sylectus-monitor/
├── hybrid_scraper.py          # Main application
├── mcp_firecrawl_client.py    # Firecrawl MCP client
├── requirements.txt           # Python dependencies
├── .env.template             # Environment variables template
├── .env                      # Your actual credentials (create this)
├── setup.sh                  # Automated setup script
├── Dockerfile                # Docker container definition
├── docker-compose.yml        # Docker Compose configuration
├── SETUP.md                  # This setup guide
├── venv/                     # Python virtual environment
├── data/                     # Application data storage
└── sent_items.txt            # Track sent notifications
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SYLECTUS_CORPORATE_ID` | Sylectus corporate ID | Yes | - |
| `SYLECTUS_CORPORATE_PASSWORD` | Sylectus corporate password | Yes | - |
| `SYLECTUS_USERNAME` | Sylectus username | Yes | - |
| `SYLECTUS_USER_PASSWORD` | Sylectus user password | Yes | - |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Yes | - |
| `TELEGRAM_CHAT_ID` | Telegram chat ID | Yes | - |
| `FIRECRAWL_API_KEY` | Firecrawl API key | Yes | - |
| `CHECK_INTERVAL` | Scraping interval (seconds) | No | 120 |
| `HEADLESS` | Run browser in headless mode | No | true |
| `MAX_RETRIES` | Maximum retry attempts | No | 3 |
| `RETRY_DELAY` | Delay between retries (seconds) | No | 30 |

## 🐛 Troubleshooting

### Common Issues

1. **Permission Denied on setup.sh**
   ```bash
   chmod +x setup.sh
   ```

2. **Playwright Browser Installation Issues**
   ```bash
   playwright install-deps chromium
   # or with sudo if needed
   sudo playwright install-deps chromium
   ```

3. **Node.js/npm Not Found**
   - Install Node.js from https://nodejs.org/
   - Or use package manager: `sudo apt install nodejs npm`

4. **Python Virtual Environment Issues**
   ```bash
   python3 -m venv --clear venv
   source venv/bin/activate
   pip install --upgrade pip
   ```

5. **Firecrawl MCP Issues**
   - Ensure Node.js 16+ is installed
   - Check internet connection for npx package downloads
   - Verify FIRECRAWL_API_KEY is valid

### Logs and Debugging

- **Local logs**: Check console output
- **Docker logs**: `docker-compose logs -f`
- **Background process**: Check `output.log` file

## 🔄 Updates and Maintenance

### Updating Dependencies
```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
playwright install chromium
```

### Backup Important Files
- `.env` - Your credentials
- `sent_items.txt` - Prevents duplicate notifications
- `data/` - Application data

## 📞 Support

For issues with:
- **Sylectus access**: Contact your Sylectus administrator
- **Telegram bot**: Check @BotFather documentation
- **Firecrawl API**: Visit https://firecrawl.dev/docs
- **Application bugs**: Check logs and configuration

## 🔒 Security Notes

- Never commit `.env` file to version control
- Use strong, unique passwords for all services
- Regularly rotate API keys and tokens
- Run containers with non-root users in production
- Use HTTPS endpoints where available

---

**Happy Load Monitoring! 🚛📱**
