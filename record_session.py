#!/usr/bin/env python3
"""
Simple session recorder - records your actions and page content
"""

from playwright.sync_api import sync_playwright
import time
import json

def record_session():
    with sync_playwright() as p:
        # Launch browser in non-headless mode so you can interact
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()
        page = context.new_page()
        
        print("🎬 Recording session started!")
        print("📝 Navigate to Sylectus and perform your actions")
        print("📄 I'll capture page content at each step")
        
        step = 1
        
        try:
            while True:
                print(f"\n🔍 Step {step}: Current URL: {page.url}")
                print("📸 Taking screenshot...")
                page.screenshot(path=f"step_{step}_screenshot.png")
                
                print("💾 Saving page content...")
                with open(f"step_{step}_content.html", "w") as f:
                    f.write(page.content())
                
                print("🔧 Saving page info...")
                page_info = {
                    "step": step,
                    "url": page.url,
                    "title": page.title(),
                    "timestamp": time.time()
                }
                
                with open(f"step_{step}_info.json", "w") as f:
                    json.dump(page_info, f, indent=2)
                
                print(f"✅ Step {step} recorded")
                print("➡️  Perform your next action, then press Enter (or Ctrl+C to stop)")
                
                try:
                    input()
                    step += 1
                except KeyboardInterrupt:
                    print("\n🛑 Recording stopped by user")
                    break
                    
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            browser.close()
            print("🎬 Recording session ended!")

if __name__ == "__main__":
    record_session()