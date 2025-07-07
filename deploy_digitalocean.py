#!/usr/bin/env python3
"""
DigitalOcean Deployment Script for Sylectus Scraper
Creates a $4/month droplet with automatic setup
"""

import requests
import json
import time
import base64
import os
from typing import Dict, Any

class DigitalOceanDeployer:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://api.digitalocean.com/v2'
        
    def create_droplet(self, name: str, region: str = 'nyc1') -> Dict[str, Any]:
        """Create a new droplet with cloud-init setup"""
        
        # Read cloud-init configuration
        with open('cloud-init.yaml', 'r') as f:
            cloud_init = f.read()
        
        # Get SSH keys
        ssh_keys = self.get_ssh_keys()
        ssh_key_ids = [key['id'] for key in ssh_keys] if ssh_keys else []
        
        droplet_config = {
            'name': name,
            'region': region,
            'size': 's-1vcpu-1gb',  # $4/month droplet
            'image': 'ubuntu-22-04-x64',
            'ssh_keys': ssh_key_ids,
            'backups': False,
            'ipv6': True,
            'user_data': cloud_init,
            'monitoring': True,
            'tags': ['sylectus-scraper', 'automated']
        }
        
        print(f"🚀 Creating droplet '{name}' in {region}...")
        response = requests.post(
            f'{self.base_url}/droplets',
            headers=self.headers,
            json=droplet_config
        )
        
        if response.status_code == 202:
            droplet = response.json()['droplet']
            print(f"✅ Droplet created! ID: {droplet['id']}")
            return droplet
        else:
            print(f"❌ Failed to create droplet: {response.text}")
            return None
    
    def wait_for_droplet(self, droplet_id: int, timeout: int = 300) -> Dict[str, Any]:
        """Wait for droplet to be ready"""
        print("⏳ Waiting for droplet to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            response = requests.get(
                f'{self.base_url}/droplets/{droplet_id}',
                headers=self.headers
            )
            
            if response.status_code == 200:
                droplet = response.json()['droplet']
                if droplet['status'] == 'active':
                    print(f"✅ Droplet is ready! IP: {droplet['networks']['v4'][0]['ip_address']}")
                    return droplet
            
            print("⏳ Still waiting...")
            time.sleep(10)
        
        print("❌ Timeout waiting for droplet")
        return None
    
    def get_ssh_keys(self):
        """Get available SSH keys"""
        response = requests.get(
            f'{self.base_url}/account/keys',
            headers=self.headers
        )
        
        if response.status_code == 200:
            keys = response.json()['ssh_keys']
            if keys:
                print(f"📋 Available SSH keys: {len(keys)}")
                for key in keys:
                    print(f"  - {key['name']} (ID: {key['id']})")
                return keys
        
        print("⚠️  No SSH keys found. You'll need to access via console.")
        return []
    
    def deploy_complete_system(self, droplet_name: str = None):
        """Deploy complete Sylectus scraper system"""
        
        if not droplet_name:
            droplet_name = f"sylectus-scraper-{int(time.time())}"
        
        print("🚀 Starting DigitalOcean deployment...")
        print(f"💰 Cost: $4/month + $0.007/hour during setup")
        
        # Get SSH keys
        ssh_keys = self.get_ssh_keys()
        
        # Create droplet
        droplet = self.create_droplet(droplet_name)
        if not droplet:
            return None
        
        # Wait for droplet to be ready
        droplet = self.wait_for_droplet(droplet['id'])
        if not droplet:
            return None
        
        ip_address = droplet['networks']['v4'][0]['ip_address']
        
        print(f"""
🎉 Deployment initiated successfully!

📋 Droplet Details:
   Name: {droplet['name']}
   ID: {droplet['id']}
   IP: {ip_address}
   Region: {droplet['region']['name']}
   Size: {droplet['size']['slug']} (${droplet['size']['price_monthly']}/month)

⏳ Setup Progress:
   The server is now installing and configuring:
   - Python 3.8+
   - Required packages
   - Sylectus scraper
   - Systemd service
   - Monitoring tools

🔧 Next Steps:
   1. Wait 5-10 minutes for cloud-init to complete
   2. SSH into server: ssh root@{ip_address}
   3. Configure .env file with your credentials
   4. Start the scraper service

📊 Monitoring:
   - Service status: systemctl status sylectus-scraper
   - Logs: journalctl -u sylectus-scraper -f
   - Resource usage: htop
        """)
        
        return {
            'droplet_id': droplet['id'],
            'ip_address': ip_address,
            'name': droplet['name']
        }

def main():
    # DigitalOcean API token
    API_TOKEN = "dop_v1_cc6741d9cff4eaaebe9983e510e532d3f05572e7d6eb8525bd5e0a99337cf5e1"
    
    deployer = DigitalOceanDeployer(API_TOKEN)
    
    print("🌊 DigitalOcean Sylectus Scraper Deployment")
    print("=" * 50)
    
    # Deploy the system
    result = deployer.deploy_complete_system()
    
    if result:
        print("\n✅ Deployment completed successfully!")
        print(f"🔗 Access your server: ssh root@{result['ip_address']}")
        print(f"📋 Droplet ID: {result['droplet_id']}")
        
        # Save deployment info
        with open('deployment_info.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print("\n💾 Deployment info saved to deployment_info.json")
    else:
        print("\n❌ Deployment failed!")

if __name__ == "__main__":
    main()