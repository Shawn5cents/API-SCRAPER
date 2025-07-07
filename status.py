#!/usr/bin/env python3
"""
Sylectus Monitor - Environment Status
Shows current environment setup and configuration
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def show_environment_info():
    """Display environment information"""
    print("🌍 Environment Information")
    print("-" * 30)
    
    # Python version
    print(f"Python: {sys.version.split()[0]}")
    
    # Virtual environment
    venv_path = os.environ.get('VIRTUAL_ENV')
    if venv_path:
        print(f"Virtual Env: {venv_path}")
    else:
        print("Virtual Env: Not activated")
    
    # Node.js version
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Node.js: {result.stdout.strip()}")
        else:
            print("Node.js: Not found")
    except:
        print("Node.js: Not found")
    
    # Working directory
    print(f"Working Dir: {os.getcwd()}")
    print()

def show_installed_packages():
    """Show key installed packages"""
    print("📦 Key Installed Packages")
    print("-" * 30)
    
    key_packages = [
        'playwright', 'requests', 'beautifulsoup4',
        'python-dotenv', 'python-telegram-bot', 'selenium',
        'aiohttp', 'httpx'
    ]
    
    try:
        result = subprocess.run(['pip', 'list'], capture_output=True, text=True)
        installed = result.stdout.lower()
        
        for package in key_packages:
            package_lower = package.replace('-', '_').replace('_', '-')
            if package_lower in installed or package.replace('-', '_') in installed:
                # Get version
                version_result = subprocess.run(['pip', 'show', package], 
                                              capture_output=True, text=True)
                if version_result.returncode == 0:
                    for line in version_result.stdout.split('\n'):
                        if line.startswith('Version:'):
                            version = line.split(':')[1].strip()
                            print(f"  ✅ {package}: {version}")
                            break
                else:
                    print(f"  ✅ {package}: installed")
            else:
                print(f"  ❌ {package}: not installed")
    except:
        print("  ⚠️ Could not check package versions")
    
    print()

def show_credentials_status():
    """Show credentials configuration status"""
    print("🔐 Credentials Status")
    print("-" * 30)
    
    load_dotenv()
    
    credentials = {
        'TELEGRAM_BOT_TOKEN': 'Telegram Bot Token',
        'TELEGRAM_CHAT_ID': 'Telegram Chat ID',
        'FIRECRAWL_API_KEY': 'Firecrawl API Key',
        'SYLECTUS_CORPORATE_ID': 'Sylectus Corporate ID',
        'SYLECTUS_CORPORATE_PASSWORD': 'Sylectus Corporate Password',
        'SYLECTUS_USERNAME': 'Sylectus Username',
        'SYLECTUS_USER_PASSWORD': 'Sylectus User Password'
    }
    
    for var, description in credentials.items():
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            # Show partial value for security
            if len(value) > 20:
                display_value = value[:10] + "..." + value[-5:]
            else:
                display_value = value[:5] + "..."
            print(f"  ✅ {description}: {display_value}")
        else:
            print(f"  ❌ {description}: Not configured")
    
    print()

def show_file_status():
    """Show important file status"""
    print("📁 File Status")
    print("-" * 30)
    
    important_files = {
        '.env': 'Environment configuration',
        'requirements.txt': 'Python dependencies',
        'hybrid_scraper.py': 'Main application',
        'mcp_firecrawl_client.py': 'Firecrawl client',
        'venv/': 'Virtual environment',
        'data/': 'Data directory',
        'sent_items.txt': 'Sent items tracking'
    }
    
    for file_path, description in important_files.items():
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  ✅ {description}: {size} bytes")
            else:
                print(f"  ✅ {description}: Directory exists")
        else:
            print(f"  ❌ {description}: Missing")
    
    print()

def show_next_steps():
    """Show next steps"""
    print("🚀 Next Steps")
    print("-" * 30)
    
    load_dotenv()
    
    steps = []
    
    # Check if .env needs configuration
    if not os.path.exists('.env'):
        steps.append("1. Create .env file from .env.template")
        steps.append("2. Configure credentials in .env file")
    else:
        missing_creds = []
        required_creds = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
        
        for cred in required_creds:
            value = os.getenv(cred)
            if not value or value == f"your_{cred.lower()}_here":
                missing_creds.append(cred)
        
        if missing_creds:
            steps.append(f"1. Configure missing credentials: {', '.join(missing_creds)}")
    
    # Check if validation passed
    if not steps:
        steps.append("1. Run validation: python validate_setup.py")
        steps.append("2. Start monitoring: python hybrid_scraper.py")
        steps.append("3. Monitor logs for any issues")
    
    if steps:
        for step in steps:
            print(f"  {step}")
    else:
        print("  🎉 Setup is complete! Ready to run.")
    
    print()

def main():
    """Main function"""
    print("📊 Sylectus Monitor - Environment Status")
    print("=" * 50)
    print()
    
    show_environment_info()
    show_installed_packages()
    show_credentials_status()
    show_file_status()
    show_next_steps()
    
    print("=" * 50)
    print("📖 For detailed setup instructions, see SETUP.md")
    print("🔍 To validate setup, run: python validate_setup.py")
    print()

if __name__ == "__main__":
    main()
