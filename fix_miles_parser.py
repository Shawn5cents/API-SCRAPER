#!/usr/bin/env python3
"""
Fix for miles parsing in enhanced_parser.py
"""

import re

# Read the current parser
with open('/home/nichols-ai/sylectus-monitor/enhanced_parser.py', 'r') as f:
    content = f.read()

# Fix the miles parsing logic
old_pattern = '''                else:
                    # Fallback: try to split by position if it's concatenated
                    if text.isdigit() and len(text) >= 2:
                        # Assume first 1-2 digits are pieces, rest are miles
                        if len(text) == 2:
                            load_data['pieces'] = text[0]
                            load_data['miles'] = text[1:]
                        elif len(text) == 3:
                            load_data['pieces'] = text[0]
                            load_data['miles'] = text[1:]
                        elif len(text) >= 4:
                            load_data['pieces'] = text[0]
                            load_data['miles'] = text[1:]'''

new_pattern = '''                else:
                    # Fallback: try to split by position if it's concatenated
                    if text.isdigit() and len(text) >= 2:
                        # Assume first 1-2 digits are pieces, rest are miles (max 4 digits for miles)
                        if len(text) == 2:
                            load_data['pieces'] = text[0]
                            load_data['miles'] = text[1:]
                        elif len(text) == 3:
                            load_data['pieces'] = text[0]
                            load_data['miles'] = text[1:]
                        elif len(text) >= 4:
                            load_data['pieces'] = text[0]
                            # Limit miles to max 4 digits (9999 miles max)
                            miles_part = text[1:]
                            if len(miles_part) > 4:
                                miles_part = miles_part[:4]
                            load_data['miles'] = miles_part'''

# Replace the pattern
fixed_content = content.replace(old_pattern, new_pattern)

# Write the fixed version
with open('/home/nichols-ai/sylectus-monitor/enhanced_parser.py', 'w') as f:
    f.write(fixed_content)

print("✅ Miles parsing fixed - limited to max 4 digits (9999 miles)")