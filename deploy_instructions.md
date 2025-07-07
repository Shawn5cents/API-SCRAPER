# 🌊 DigitalOcean Deployment Instructions

## Quick Deploy

1. **Run the deployment script:**
```bash
python3 deploy_digitalocean.py
```

2. **Wait for setup (5-10 minutes)** - The server will automatically:
   - Install Python, packages, and dependencies
   - Clone your scraper code
   - Set up systemd service
   - Configure monitoring

3. **SSH into your server:**
```bash
ssh root@YOUR_SERVER_IP
```

4. **Configure your credentials:**
```bash
cd /opt/sylectus-scraper
./manage.sh setup
nano .env  # Add your Telegram bot token and chat ID
```

5. **Start the scraper:**
```bash
./manage.sh start
```

## Server Management

### Service Control
```bash
./manage.sh start      # Start scraper
./manage.sh stop       # Stop scraper
./manage.sh restart    # Restart scraper
./manage.sh status     # Check status
./manage.sh logs       # View live logs
```

### Monitoring
```bash
./monitor.sh           # System overview
journalctl -u sylectus-scraper -f  # Live logs
htop                   # Resource usage
```

## Troubleshooting

### If scraper won't start:
1. Check environment file: `cat .env`
2. Test manually: `python3 api_scraper.py --startup`
3. Check service logs: `./manage.sh logs`

### If no loads appear:
1. Verify cookies: `ls -la extracted_cookies_*.env`
2. Run network monitor: `python3 auto_monitor.py`
3. Check Telegram bot setup

### Performance Issues:
- Monitor resources: `./monitor.sh`
- Restart service: `./manage.sh restart`
- Check disk space: `df -h`

## Cost Breakdown
- **Server**: $4/month (s-1vcpu-1gb)
- **Bandwidth**: ~$0.01/GB
- **Snapshots**: $0.05/GB (optional)
- **Total**: ~$4-5/month

## Security
- Firewall configured for SSH only
- Service runs as non-root user
- Logs rotated automatically
- Regular security updates

---

🎉 **Your scraper is now running 24/7 in the cloud!**