#!/usr/bin/env python3
"""
Enhanced fix for miles/weight parsing in Sylectus HTML table
"""

import re

# Read the current parser
with open('/home/nichols-ai/sylectus-monitor/enhanced_parser.py', 'r') as f:
    content = f.read()

# Better logic for parsing table cells based on column position
new_parsing_logic = '''            # Cell 6: Vehicle size and miles (VEH. SIZE<BR>MILES)
            elif i == 6:  # Miles column
                if '<br>' in html.lower() or '<br/>' in html.lower():
                    # Split by <br> tags - vehicle is first, miles is second
                    parts = re.split(r'<br/?>', html, flags=re.IGNORECASE)
                    if len(parts) >= 2:
                        # First part is vehicle type
                        vehicle_text = re.sub(r'<[^>]+>', '', parts[0]).strip()
                        load_data['vehicle_type'] = vehicle_text
                        print(f"✅ Vehicle type extracted: {vehicle_text}")
                        
                        # Second part is miles - extract only digits
                        miles_text = re.sub(r'<[^>]+>', '', parts[1]).strip()
                        miles_match = re.search(r'^(\d{1,4})', miles_text)  # Limit to 4 digits max
                        if miles_match:
                            load_data['miles'] = miles_match.group(1)
                            print(f"✅ Miles extracted: {load_data['miles']}")
                        else:
                            print(f"⚠️ Could not extract miles from: {miles_text}")
                else:
                    # Single value - try to extract miles
                    text = re.sub(r'<[^>]+>', '', html).strip()
                    miles_match = re.search(r'(\d{1,4})', text)  # Limit to 4 digits
                    if miles_match:
                        load_data['miles'] = miles_match.group(1)
                        print(f"✅ Miles extracted: {load_data['miles']}")
            
            # Cell 7: Pieces and weight (PCS<BR>WT)
            elif i == 7:  # Weight/Pieces column  
                if '<br>' in html.lower() or '<br/>' in html.lower():
                    # Split by <br> tags - pieces is first, weight is second
                    parts = re.split(r'<br/?>', html, flags=re.IGNORECASE)
                    if len(parts) >= 2:
                        # First part is pieces
                        pieces_text = re.sub(r'<[^>]+>', '', parts[0]).strip()
                        pieces_match = re.search(r'(\d+)', pieces_text)
                        if pieces_match:
                            load_data['pieces'] = pieces_match.group(1)
                            print(f"✅ Pieces extracted: {load_data['pieces']}")
                        
                        # Second part is weight
                        weight_text = re.sub(r'<[^>]+>', '', parts[1]).strip()
                        weight_match = re.search(r'(\d+)', weight_text)
                        if weight_match:
                            load_data['weight'] = f"{weight_match.group(1)} lbs"
                            print(f"✅ Weight extracted: {load_data['weight']}")
                else:
                    # Single value - assume it's weight
                    text = re.sub(r'<[^>]+>', '', html).strip()
                    weight_match = re.search(r'(\d+)', text)
                    if weight_match:
                        load_data['weight'] = f"{weight_match.group(1)} lbs"
                        print(f"✅ Weight extracted: {load_data['weight']}")'''

# Find the old table parsing logic and replace it
old_pattern = r'# Cell 7 usually contains pieces and miles.*?print\(f"✅ Miles extracted: \{load_data\[\'miles\'\]\}"\)'

# Replace with new logic
fixed_content = re.sub(old_pattern, new_parsing_logic, content, flags=re.DOTALL)

# Write the fixed version
with open('/home/nichols-ai/sylectus-monitor/enhanced_parser.py', 'w') as f:
    f.write(fixed_content)

print("✅ Enhanced miles/weight parsing logic implemented")
print("- Column 6: Vehicle type and miles (max 4 digits)")  
print("- Column 7: Pieces and weight")
print("- Proper HTML <br> tag parsing")