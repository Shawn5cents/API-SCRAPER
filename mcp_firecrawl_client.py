#!/usr/bin/env python3
"""
Firecrawl MCP Client for enhanced web scraping
Integrates with Firecrawl MCP server for reliable content extraction
"""

import subprocess
import json
import sys
from typing import Dict, List, Optional

class FirecrawlMCPClient:
    def __init__(self):
        self.mcp_process = None
        self.session_id = None
    
    def start_mcp_server(self):
        """Start the Firecrawl MCP server"""
        try:
            print("🔥 Starting Firecrawl MCP server...")
            
            # Start Firecrawl MCP server process
            self.mcp_process = subprocess.Popen(
                ['npx', 'firecrawl-mcp'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0
            )
            
            print("✅ Firecrawl MCP server started")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start MCP server: {e}")
            return False
    
    def send_mcp_request(self, method: str, params: Dict) -> Optional[Dict]:
        """Send a request to the MCP server"""
        if not self.mcp_process:
            print("❌ MCP server not running")
            return None
        
        try:
            # Prepare JSON-RPC request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params
            }
            
            # Send request
            request_json = json.dumps(request) + '\n'
            self.mcp_process.stdin.write(request_json)
            self.mcp_process.stdin.flush()
            
            # Read response
            response_line = self.mcp_process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                return response
            
            return None
            
        except Exception as e:
            print(f"❌ MCP request failed: {e}")
            return None
    
    def initialize_session(self):
        """Initialize MCP session"""
        try:
            response = self.send_mcp_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "sylectus-hybrid-scraper",
                    "version": "1.0.0"
                }
            })
            
            if response and "result" in response:
                print("✅ MCP session initialized")
                return True
            else:
                print("❌ MCP session initialization failed")
                return False
                
        except Exception as e:
            print(f"❌ Session initialization error: {e}")
            return False
    
    def scrape_url(self, url: str, cookies: Dict = None, options: Dict = None) -> Optional[Dict]:
        """Scrape a URL using Firecrawl with optional cookies and options"""
        try:
            # Prepare scraping parameters
            params = {
                "url": url,
                "options": options or {}
            }
            
            # Add cookies if provided
            if cookies:
                params["options"]["headers"] = {
                    "Cookie": "; ".join([f"{k}={v}" for k, v in cookies.items()])
                }
            
            print(f"🔥 Scraping {url} with Firecrawl...")
            
            # Send scraping request
            response = self.send_mcp_request("tools/call", {
                "name": "firecrawl_scrape",
                "arguments": params
            })
            
            if response and "result" in response:
                print("✅ Firecrawl scraping completed")
                return response["result"]
            else:
                print("❌ Firecrawl scraping failed")
                return None
                
        except Exception as e:
            print(f"❌ Scraping error: {e}")
            return None
    
    def extract_load_data(self, content: str) -> List[Dict]:
        """Extract structured load data from scraped content"""
        try:
            # Use Firecrawl's AI-powered extraction
            extraction_params = {
                "content": content,
                "schema": {
                    "type": "object",
                    "properties": {
                        "loads": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "company": {"type": "string"},
                                    "load_id": {"type": "string"},
                                    "pickup_city": {"type": "string"},
                                    "pickup_date": {"type": "string"},
                                    "delivery_city": {"type": "string"},
                                    "delivery_date": {"type": "string"},
                                    "miles": {"type": "string"},
                                    "pieces": {"type": "string"},
                                    "weight": {"type": "string"},
                                    "vehicle_type": {"type": "string"},
                                    "email": {"type": "string"},
                                    "bid_available": {"type": "boolean"}
                                }
                            }
                        }
                    }
                }
            }
            
            response = self.send_mcp_request("tools/call", {
                "name": "firecrawl_extract",
                "arguments": extraction_params
            })
            
            if response and "result" in response:
                extracted_data = response["result"]
                if "loads" in extracted_data:
                    print(f"✅ Extracted {len(extracted_data['loads'])} loads")
                    return extracted_data["loads"]
            
            print("⚠️ No load data extracted")
            return []
            
        except Exception as e:
            print(f"❌ Data extraction error: {e}")
            return []
    
    def stop_mcp_server(self):
        """Stop the MCP server"""
        if self.mcp_process:
            try:
                self.mcp_process.terminate()
                self.mcp_process.wait(timeout=5)
                print("✅ MCP server stopped")
            except subprocess.TimeoutExpired:
                self.mcp_process.kill()
                print("⚠️ MCP server force killed")
            except Exception as e:
                print(f"❌ Error stopping MCP server: {e}")

def test_firecrawl_mcp():
    """Test function for Firecrawl MCP client"""
    client = FirecrawlMCPClient()
    
    try:
        # Start MCP server
        if not client.start_mcp_server():
            return False
        
        # Initialize session
        if not client.initialize_session():
            return False
        
        # Test scraping a simple page
        test_url = "https://example.com"
        result = client.scrape_url(test_url)
        
        if result:
            print("✅ Firecrawl MCP test successful")
            return True
        else:
            print("❌ Firecrawl MCP test failed")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    finally:
        client.stop_mcp_server()

if __name__ == "__main__":
    test_firecrawl_mcp()