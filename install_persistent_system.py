#!/usr/bin/env python3
"""
Installation Script for Persistent Session Management System
Installs all dependencies and sets up the automated session management
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    
    packages = [
        "undetected-chromedriver",
        "selenium",
        "requests",
        "schedule",
        "python-dotenv",
        "beautifulsoup4"
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✅ {package} installed")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def setup_chrome():
    """Setup Chrome for undetected automation"""
    print("🌐 Setting up Chrome for automation...")
    
    try:
        # Check if Chrome is installed
        result = subprocess.run(["google-chrome", "--version"], 
                              capture_output=True, text=True)
        print(f"✅ Chrome found: {result.stdout.strip()}")
    except FileNotFoundError:
        print("⚠️ Chrome not found. Installing...")
        
        # Install Chrome on Ubuntu/Debian
        try:
            subprocess.run([
                "wget", "-q", "-O", "-", 
                "https://dl.google.com/linux/linux_signing_key.pub"
            ], check=True)
            
            subprocess.run([
                "sudo", "apt-key", "add", "-"
            ], check=True)
            
            subprocess.run([
                "sudo", "sh", "-c", 
                'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
            ], check=True)
            
            subprocess.run(["sudo", "apt", "update"], check=True)
            subprocess.run(["sudo", "apt", "install", "-y", "google-chrome-stable"], check=True)
            
            print("✅ Chrome installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Chrome automatically")
            print("Please install Chrome manually: https://www.google.com/chrome/")
            return False
    
    return True

def create_service_file():
    """Create systemd service file for persistent session management"""
    print("⚙️ Creating systemd service...")
    
    service_content = f"""[Unit]
Description=Sylectus Persistent Session Manager
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={Path.cwd()}
ExecStart={sys.executable} smart_session_integration.py
Restart=always
RestartSec=30
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target
"""
    
    try:
        service_file = Path("/etc/systemd/system/sylectus-session-manager.service")
        
        # Write service file (requires sudo)
        with open("sylectus-session-manager.service", "w") as f:
            f.write(service_content)
        
        subprocess.run([
            "sudo", "cp", "sylectus-session-manager.service", 
            str(service_file)
        ], check=True)
        
        # Reload systemd
        subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "sylectus-session-manager"], check=True)
        
        print("✅ Systemd service created and enabled")
        
        # Clean up temp file
        os.remove("sylectus-session-manager.service")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create service: {e}")
        print("You can manually start the session manager with:")
        print(f"python3 {Path.cwd()}/smart_session_integration.py")
        return False

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    
    # Check if credentials exist
    username = os.getenv('SYLECTUS_USERNAME')
    password = os.getenv('SYLECTUS_PASSWORD')
    
    if not username:
        username = input("Enter Sylectus username: ").strip()
    if not password:
        password = input("Enter Sylectus password: ").strip()
    
    if not username or not password:
        print("⚠️ Username and password are required for automated session management")
        return False
    
    # Create/update .env file
    env_content = f"""# Sylectus Credentials
SYLECTUS_USERNAME={username}
SYLECTUS_PASSWORD={password}

# Telegram Configuration
TELEGRAM_BOT_TOKEN=6331983207:AAEzrXpH7ISNP7dz9ZgXBfBadE6TpDxWwLw
TELEGRAM_CHAT_ID=6547104920

# Scraper Configuration
CHECK_INTERVAL=120

# Session Management
SESSION_CHECK_INTERVAL=7200
MAX_SESSIONS=3
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print("✅ Environment configuration saved")
    return True

def test_installation():
    """Test the installation"""
    print("🧪 Testing installation...")
    
    try:
        # Test imports
        import undetected_chromedriver as uc
        from selenium import webdriver
        import requests
        
        print("✅ All imports successful")
        
        # Test Chrome driver creation
        options = uc.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = uc.Chrome(options=options)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"✅ Chrome automation test successful: {title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def deploy_to_server():
    """Deploy the persistent session system to DigitalOcean server"""
    print("🚀 Deploying to DigitalOcean server...")
    
    ssh_key = Path("~/.ssh/sylectus_key").expanduser()
    if not ssh_key.exists():
        print("❌ SSH key not found. Cannot deploy to server.")
        return False
    
    server_ip = "157.245.242.222"
    
    try:
        # Create directory on server
        subprocess.run([
            "ssh", "-i", str(ssh_key), f"root@{server_ip}",
            "mkdir -p /opt/session-manager"
        ], check=True, timeout=30)
        
        # Upload files
        files_to_upload = [
            "persistent_session_manager.py",
            "stealth_session_keeper.py", 
            "smart_session_integration.py",
            "install_persistent_system.py",
            ".env"
        ]
        
        for file in files_to_upload:
            if Path(file).exists():
                subprocess.run([
                    "scp", "-i", str(ssh_key), file,
                    f"root@{server_ip}:/opt/session-manager/"
                ], check=True, timeout=60)
                print(f"✅ Uploaded {file}")
        
        # Install dependencies on server
        subprocess.run([
            "ssh", "-i", str(ssh_key), f"root@{server_ip}",
            "cd /opt/session-manager && python3 -m pip install undetected-chromedriver selenium requests schedule python-dotenv beautifulsoup4"
        ], check=True, timeout=300)
        
        print("✅ Dependencies installed on server")
        
        # Install Chrome on server
        subprocess.run([
            "ssh", "-i", str(ssh_key), f"root@{server_ip}",
            "wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && "
            "echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list && "
            "apt update && apt install -y google-chrome-stable"
        ], check=True, timeout=300)
        
        print("✅ Chrome installed on server")
        
        # Create systemd service on server
        service_content = f"""[Unit]
Description=Sylectus Persistent Session Manager
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/session-manager
ExecStart=/usr/bin/python3 smart_session_integration.py
Restart=always
RestartSec=30
Environment=DISPLAY=:99

[Install]
WantedBy=multi-user.target
"""
        
        # Write and install service
        with open("temp_service", "w") as f:
            f.write(service_content)
        
        subprocess.run([
            "scp", "-i", str(ssh_key), "temp_service",
            f"root@{server_ip}:/etc/systemd/system/sylectus-session-manager.service"
        ], check=True, timeout=30)
        
        subprocess.run([
            "ssh", "-i", str(ssh_key), f"root@{server_ip}",
            "systemctl daemon-reload && systemctl enable sylectus-session-manager"
        ], check=True, timeout=30)
        
        os.remove("temp_service")
        
        print("✅ Systemd service created on server")
        print("🚀 Deployment completed successfully!")
        
        print("\n📋 Server Management Commands:")
        print(f"Start service: ssh -i {ssh_key} root@{server_ip} 'systemctl start sylectus-session-manager'")
        print(f"Check status: ssh -i {ssh_key} root@{server_ip} 'systemctl status sylectus-session-manager'")
        print(f"View logs: ssh -i {ssh_key} root@{server_ip} 'journalctl -u sylectus-session-manager -f'")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def main():
    """Main installation function"""
    print("🔧 Sylectus Persistent Session Management System Installer")
    print("=" * 60)
    
    # Check if running as root for some operations
    if os.geteuid() != 0:
        print("⚠️ Some operations may require sudo privileges")
    
    steps = [
        ("Installing Python dependencies", install_dependencies),
        ("Setting up Chrome", setup_chrome),
        ("Setting up environment", setup_environment),
        ("Testing installation", test_installation),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ {step_name} failed!")
            return False
        print(f"✅ {step_name} completed")
    
    # Optional service installation
    print(f"\n📋 Installation Options:")
    print("1. Create local systemd service")
    print("2. Deploy to DigitalOcean server")
    print("3. Manual setup only")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice == "1":
        create_service_file()
    elif choice == "2":
        deploy_to_server()
    elif choice == "3":
        print("✅ Manual setup completed")
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Run: python3 smart_session_integration.py")
    print("2. Choose option 3 to start monitoring")
    print("3. The system will automatically maintain sessions")
    
    print("\n🔧 Manual Commands:")
    print("- Test session: python3 persistent_session_manager.py")
    print("- Check stealth: python3 stealth_session_keeper.py")
    print("- Integration: python3 smart_session_integration.py")

if __name__ == "__main__":
    main()