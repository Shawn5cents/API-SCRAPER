# Changelog

All notable changes to the Sylectus Load Board API Scraper project.

## [2.1.1] - 2025-07-07

### 🚀 Added
- **SSH Key Documentation**: Complete SSH setup guide in `SSH-SETUP.md`
- **Repository SSH Configuration**: Automated SSH key generation for secure Git operations
- **Enhanced Documentation**: Updated README and DEPLOYMENT with SSH instructions

### 🔧 Changed
- **Git Configuration**: Repository configured to use dedicated SSH key
- **Security**: ED25519 key type for modern encryption standards

## [2.1.0] - 2025-07-07

### 🚀 Added
- **Automated DigitalOcean Deployment**: Complete cloud deployment with `deploy_digitalocean.py`
- **Cloud-init Configuration**: Automated server provisioning with `cloud-init.yaml`
- **Systemd Service**: Automatic startup and service management
- **SSH Key Management**: Automated SSH key generation and deployment
- **Deployment Documentation**: Comprehensive deployment guide in `DEPLOYMENT.md`

### 🐛 Fixed
- **Miles Parsing Error**: Fixed critical bug where miles were incorrectly parsed from HTML table columns
  - Column 6 now correctly handles vehicle type + miles (max 4 digits)
  - Column 7 now correctly handles pieces + weight
  - Fixed issue where 700-mile routes showed as 7000+ miles
- **Enhanced Parser Logic**: Improved HTML table parsing with proper column detection
- **Weight/Miles Reversal**: Fixed cases where miles and weight values were swapped

### 🔧 Changed
- **Parser Column Logic**: Updated `enhanced_parser.py` with correct column mapping
- **Miles Validation**: Added 4-digit maximum limit for miles (9999 max)
- **Error Handling**: Better error messages for parsing failures

### 📋 Technical Details
- **Server**: Ubuntu 22.04 LTS on DigitalOcean
- **Cost**: $4/month (1 vCPU, 1GB RAM, 10GB SSD)
- **Monitoring**: Systemd service with automatic restart
- **Logs**: Available at `/tmp/scraper.log` and via `journalctl`

## [2.0.0] - 2025-07-06

### 🚀 Added
- **Direct API Integration**: Bypasses browser automation completely
- **Email Extraction**: Fetches company email addresses from profile pages
- **Enhanced Parser**: Extracts 40+ fields from load data
- **Startup Mode**: Shows all current loads on first run
- **Telegram Integration**: Rich notifications with complete load details
- **Rate Limiting**: Intelligent delays to prevent API abuse

### 🔧 Changed
- **Architecture**: Moved from browser automation to direct API calls
- **Performance**: ~5-10x faster than browser-based scraping
- **Reliability**: No more Cloudflare or browser dependency issues

### 📋 Features
- Company information extraction
- Load details (ID, locations, dates, times)
- Vehicle requirements and specifications
- Weight, pieces, and dimensions
- Payment terms and credit scores
- Contact information including emails

## [1.0.0] - 2025-07-05

### 🚀 Initial Release
- **Browser Automation**: Selenium-based scraping
- **Basic Parsing**: Load information extraction
- **Telegram Notifications**: Simple load alerts
- **Session Management**: Cookie-based authentication

### 📋 Features
- Basic load monitoring
- Simple text notifications
- Manual session setup
- Local operation only

---

## 🔮 Upcoming Features

### v2.2.0 (Planned)
- **Multi-region Deployment**: Support for multiple cloud providers
- **Advanced Filtering**: Custom load filtering rules
- **Analytics Dashboard**: Web-based monitoring interface
- **Database Integration**: Historical load data storage
- **API Webhooks**: Custom notification endpoints

### v2.3.0 (Planned)
- **Machine Learning**: Load pattern analysis
- **Predictive Alerts**: Rate and availability predictions
- **Mobile App**: iOS/Android companion app
- **Team Management**: Multi-user access controls

---

**🚀 Built for the logistics community**
**💰 Cloud-ready • 24/7 Operation**