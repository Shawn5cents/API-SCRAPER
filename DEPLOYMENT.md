# Cloud Deployment Guide

This guide covers the automated deployment of the Sylectus Load Board API Scraper to DigitalOcean.

## 🚀 Automated Deployment

### Prerequisites
- DigitalOcean account with API access
- Valid DigitalOcean API token
- Python 3.8+ with required dependencies

### Quick Deploy
```bash
# Deploy with your API token
python3 deploy_digitalocean.py

# Follow prompts to configure:
# - Server region (default: nyc3)
# - Server size (default: s-1vcpu-1gb - $4/month)
# - SSH key setup
```

### What Gets Deployed
- **Ubuntu 22.04 LTS** droplet ($4/month)
- **Python 3.10** with pip and dependencies
- **Systemd service** for automatic startup
- **SSH key authentication**
- **Cloud-init** for automated provisioning

## 📋 Deployment Details

### Server Specifications
- **CPU**: 1 vCPU
- **RAM**: 1GB
- **Storage**: 10GB SSD
- **Network**: 1TB transfer
- **Cost**: $4/month

### Installed Components
```bash
# Core packages
python3
python3-pip
git
curl
wget

# Python dependencies
requests
beautifulsoup4
python-telegram-bot
```

### Service Configuration
```bash
# Service file: /etc/systemd/system/sylectus-scraper.service
[Unit]
Description=Sylectus Load Board API Scraper
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/sylectus-scraper
ExecStart=/usr/bin/python3 api_scraper.py --startup
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

## 🛠 Post-Deployment Setup

### 1. SSH Access
```bash
# Connect to your server
ssh -i ~/.ssh/sylectus_key root@YOUR_SERVER_IP

# Check service status
systemctl status sylectus-scraper
```

### 2. Configure Environment
```bash
# Edit environment variables
nano /opt/sylectus-scraper/.env

# Required variables:
SYLECTUS_COOKIE="your_session_cookie"
TELEGRAM_BOT_TOKEN="your_bot_token"
TELEGRAM_CHAT_ID="your_chat_id"
```

### 3. Start Service
```bash
# Start the service
systemctl start sylectus-scraper

# Enable auto-start
systemctl enable sylectus-scraper

# Check logs
journalctl -u sylectus-scraper -f
```

## 📊 Monitoring

### Service Status
```bash
# Check if service is running
systemctl is-active sylectus-scraper

# View service logs
journalctl -u sylectus-scraper --since "1 hour ago"

# Check process
ps aux | grep api_scraper
```

### Log Files
```bash
# Application logs
tail -f /tmp/scraper.log

# System logs
journalctl -u sylectus-scraper -f
```

## 🔧 Maintenance

### Update Code
```bash
# SSH into server
ssh -i ~/.ssh/sylectus_key root@YOUR_SERVER_IP

# Update repository
cd /opt/sylectus-scraper
git pull origin main

# Restart service
systemctl restart sylectus-scraper
```

### Restart Service
```bash
# Restart service
systemctl restart sylectus-scraper

# Check status
systemctl status sylectus-scraper
```

### View Performance
```bash
# CPU and memory usage
top -p $(pgrep -f api_scraper)

# Network usage
netstat -i
```

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check service logs
journalctl -u sylectus-scraper -f

# Common issues:
# - Missing .env file
# - Invalid Python syntax
# - Missing dependencies
```

### Connection Issues
```bash
# Test API connectivity
curl -I https://www.sylectus.com

# Check DNS resolution
nslookup www.sylectus.com
```

### High Resource Usage
```bash
# Monitor resources
htop

# Check disk space
df -h

# View memory usage
free -h
```

## 💰 Cost Optimization

### Current Costs
- **Server**: $4/month
- **Bandwidth**: Included (1TB)
- **Storage**: Included (10GB)
- **Total**: ~$4/month

### Scaling Options
```bash
# Upgrade server (if needed)
# - s-1vcpu-2gb: $8/month
# - s-2vcpu-2gb: $16/month
# - s-2vcpu-4gb: $24/month
```

## 🔒 Security

### SSH Security
- Key-based authentication only
- Root access (consider creating non-root user)
- Firewall configured for SSH only

### API Security
- Session cookies expire periodically
- Rate limiting prevents abuse
- No sensitive data logged

## 📈 Performance

### Expected Performance
- **Startup time**: ~30 seconds
- **Memory usage**: ~50MB
- **CPU usage**: <5%
- **Network**: ~1MB/hour

### Optimization Tips
- Use startup mode for initial testing
- Monitor Telegram rate limits
- Adjust CHECK_INTERVAL as needed

---

**🚀 Deployed on DigitalOcean**
**💰 $4/month • 24/7 Operation**