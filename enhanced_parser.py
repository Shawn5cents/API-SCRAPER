#!/usr/bin/env python3
"""
Enhanced HTML Parser for Sylectus Load Data
Extracts ALL possible information including hidden emails in HTML attributes
"""

import re
import json
from bs4 import BeautifulSoup
from datetime import datetime

class SylectusLoadParser:
    def __init__(self):
        self.debug_mode = True
        
    def parse_load_row_comprehensive(self, row_element):
        """Extract absolutely everything from a load row"""
        
        load_data = {
            'timestamp': datetime.now().isoformat(),
            'company': 'Unknown',
            'load_id': 'Unknown',
            'pickup_city': 'Unknown',
            'pickup_state': 'Unknown',
            'pickup_date': 'Unknown',
            'pickup_time': 'Unknown',
            'delivery_city': 'Unknown', 
            'delivery_state': 'Unknown',
            'delivery_date': 'Unknown',
            'delivery_time': 'Unknown',
            'miles': 'Unknown',
            'pieces': 'Unknown',
            'weight': 'Unknown',
            'dimensions': 'Unknown',
            'length': 'Unknown',
            'width': 'Unknown',
            'height': 'Unknown',
            'vehicle_type': 'Unknown',
            'credit_score': 'Unknown',
            'days_to_pay': 'Unknown',
            'contact_email': 'Unknown',
            'contact_phone': 'Unknown',
            'broker_email': 'Unknown',
            'contact_name': 'Unknown',
            'special_instructions': 'Unknown',
            'raw_html': str(row_element),
            'all_cells': [],
            'all_links': [],
            'debug_info': {}
        }
        
        # Get all table cells
        cells = row_element.find_all(['td', 'th'])
        
        for i, cell in enumerate(cells):
            cell_data = {
                'index': i,
                'text': cell.get_text().strip(),
                'html': str(cell),
                'attributes': dict(cell.attrs),
                'links': []
            }
            
            # Extract all links in this cell
            links = cell.find_all('a')
            for link in links:
                link_data = {
                    'text': link.get_text().strip(),
                    'href': link.get('href', ''),
                    'onclick': link.get('onclick', ''),
                    'title': link.get('title', ''),
                    'id': link.get('id', ''),
                    'class': link.get('class', [])
                }
                cell_data['links'].append(link_data)
                load_data['all_links'].append(link_data)
                
                # Extract emails from href
                if 'mailto:' in link_data['href']:
                    email = link_data['href'].replace('mailto:', '')
                    if '@' in email:
                        load_data['contact_email'] = email
                        print(f"✅ Email found in href: {email}")
                
                # Extract emails from onclick events
                onclick = link_data['onclick']
                if onclick:
                    # Look for email patterns in onclick
                    email_patterns = [
                        r"email['\"]?\s*:\s*['\"]([^'\"]+@[^'\"]+)['\"]",
                        r"mailto['\"]?\s*:\s*['\"]([^'\"]+@[^'\"]+)['\"]", 
                        r"contact['\"]?\s*:\s*['\"]([^'\"]+@[^'\"]+)['\"]",
                        r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
                    ]
                    
                    for pattern in email_patterns:
                        match = re.search(pattern, onclick, re.IGNORECASE)
                        if match:
                            email = match.group(1)
                            load_data['contact_email'] = email
                            print(f"✅ Email found in onclick: {email}")
                            break
                
                # Extract phone numbers from onclick
                phone_patterns = [
                    r"phone['\"]?\s*:\s*['\"]([0-9\-\(\)\.\s]{10,})['\"]",
                    r"tel['\"]?\s*:\s*['\"]([0-9\-\(\)\.\s]{10,})['\"]",
                    r"(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})"
                ]
                
                for pattern in phone_patterns:
                    match = re.search(pattern, onclick)
                    if match:
                        phone = match.group(1)
                        load_data['contact_phone'] = phone
                        print(f"✅ Phone found in onclick: {phone}")
                        break
            
            load_data['all_cells'].append(cell_data)
        
        # Parse specific fields from cell content
        self._parse_company_info(load_data)
        self._parse_load_details(load_data)
        self._parse_location_dates(load_data)
        self._parse_payment_info(load_data)
        self._extract_hidden_contact_info(load_data)
        self._extract_profile_url(load_data)
        
        return load_data
    
    def _extract_profile_url(self, load_data):
        """Extract company profile URL for email retrieval"""
        for link in load_data['all_links']:
            onclick = link.get('onclick', '')
            if 'II14_promabprofile.asp' in onclick:
                # Extract the profile URL from onclick - handle different quote styles
                url_patterns = [
                    r"'([^']+II14_promabprofile\.asp[^']+)'",
                    r'"([^"]+II14_promabprofile\.asp[^"]+)"',
                    r"openawindow\('([^']+)', \d+, \d+\)",
                    r"openawindow\(\"([^\"]+)\", \d+, \d+\)"
                ]
                
                for pattern in url_patterns:
                    url_match = re.search(pattern, onclick)
                    if url_match:
                        profile_url = url_match.group(1)
                        # Clean up URL encoding
                        profile_url = profile_url.replace('&amp;', '&')
                        load_data['profile_url'] = profile_url
                        print(f"✅ Profile URL found: {profile_url}")
                        return
                
                # If no pattern matched, try to extract anything that looks like a profile URL
                if 'II14_promabprofile.asp' in onclick:
                    # Extract everything that looks like a URL
                    url_match = re.search(r'(II14_promabprofile\.asp[^\'"\s\)]+)', onclick)
                    if url_match:
                        profile_url = url_match.group(1)
                        profile_url = profile_url.replace('&amp;', '&')
                        load_data['profile_url'] = profile_url
                        print(f"✅ Profile URL found (fallback): {profile_url}")
                        return
    
    def _parse_company_info(self, load_data):
        """Extract company information"""
        if load_data['all_cells']:
            first_cell = load_data['all_cells'][0]['text']
            
            # Company name is usually before "Days to Pay"
            if 'Days to Pay' in first_cell:
                company = first_cell.split('Days to Pay')[0].strip()
                company = company.replace('\xa0', ' ').strip()
                if company:
                    load_data['company'] = company
                    print(f"✅ Company extracted: {company}")
    
    def _parse_load_details(self, load_data):
        """Extract load ID, miles, weight, etc."""
        for cell in load_data['all_cells']:
            text = cell['text']
            html = cell['html']
            
            # Extract load ID from second cell typically
            if cell['index'] == 1:
                load_id_match = re.search(r'(\d{6,})', text)
                if load_id_match:
                    load_data['load_id'] = load_id_match.group(1)
                    print(f"✅ Load ID extracted: {load_data['load_id']}")
                
                # Vehicle type
                vehicle_patterns = ['Small Straight', 'Large Straight', 'Straight', 'Van', 'Flatbed', 'Cargo Van']
                for vehicle in vehicle_patterns:
                    if vehicle.lower() in text.lower():
                        load_data['vehicle_type'] = vehicle
                        break
            
            # Cell 6 usually contains vehicle type + weight
            if cell['index'] == 6:
                # Extract vehicle type
                vehicle_patterns = ['CARGO VAN', 'STRAIGHT', 'VAN', 'FLATBED', 'REEFER', 'DRY VAN']
                for vehicle in vehicle_patterns:
                    if vehicle in text.upper():
                        load_data['vehicle_type'] = vehicle
                        break
                
                # Extract weight (numbers after vehicle type)
                weight_match = re.search(r'([A-Z\s]+)(\d+)', text)
                if weight_match:
                    weight = weight_match.group(2)
                    if int(weight) > 50:  # Weight should be > 50 lbs
                        load_data['weight'] = f"{weight} lbs"
                        print(f"✅ Weight extracted: {weight} lbs")
            
            # Cell 7 usually contains pieces and miles (separated by <br/>)
            if cell['index'] == 7:
                # Parse HTML to get separate values
                if '<br/>' in html:
                    parts = html.split('<br/>')
                    if len(parts) >= 2:
                        # First part: pieces
                        pieces_match = re.search(r'(\d+)', parts[0])
                        if pieces_match:
                            load_data['pieces'] = pieces_match.group(1)
                            print(f"✅ Pieces extracted: {load_data['pieces']}")
                        
                        # Second part: miles  
                        miles_match = re.search(r'(\d+)', parts[1])
                        if miles_match:
                            load_data['miles'] = miles_match.group(1)
                            print(f"✅ Miles extracted: {load_data['miles']}")
                else:
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
                            load_data['miles'] = text[1:]
            
            # Look for dimensions in any cell
            dim_patterns = [
                r'(\d+)["\']?\s*[xX×]\s*(\d+)["\']?\s*[xX×]\s*(\d+)["\']?',  # LxWxH with quotes
                r'(\d+)\s*[xX×]\s*(\d+)\s*[xX×]\s*(\d+)',  # LxWxH
                r'(\d+)L\s*[xX×]\s*(\d+)W\s*[xX×]\s*(\d+)H',  # LWH format
                r'(\d+)\s*x\s*(\d+)\s*x\s*(\d+)',  # Standard format
            ]
            
            for pattern in dim_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    length, width, height = match.groups()
                    load_data['dimensions'] = f"{length}x{width}x{height}"
                    load_data['length'] = length
                    load_data['width'] = width
                    load_data['height'] = height
                    print(f"✅ Dimensions extracted: {load_data['dimensions']}")
                    break
            
            # Extract numeric data (fallback for other cells)
            if text.isdigit() and load_data['miles'] == 'Unknown' and load_data['pieces'] == 'Unknown':
                num = int(text)
                if 100 <= num <= 3000:
                    load_data['miles'] = text
                elif 1 <= num <= 50:
                    load_data['pieces'] = text
    
    def _parse_location_dates(self, load_data):
        """Extract pickup/delivery locations and dates"""
        full_text = ' '.join([cell['text'] for cell in load_data['all_cells']])
        
        # Extract cities and states
        city_pattern = r'([A-Z][A-Z\s&]+),\s*([A-Z]{2})'
        cities = re.findall(city_pattern, full_text)
        
        if len(cities) >= 2:
            load_data['pickup_city'] = cities[0][0].strip()
            load_data['pickup_state'] = cities[0][1]
            load_data['delivery_city'] = cities[1][0].strip() 
            load_data['delivery_state'] = cities[1][1]
        
        # Extract dates and times
        date_pattern = r'(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})'
        dates = re.findall(date_pattern, full_text)
        
        if len(dates) >= 2:
            load_data['pickup_date'] = dates[0][0]
            load_data['pickup_time'] = dates[0][1]
            load_data['delivery_date'] = dates[1][0]
            load_data['delivery_time'] = dates[1][1]
    
    def _parse_payment_info(self, load_data):
        """Extract credit score, payment terms"""
        full_text = ' '.join([cell['text'] for cell in load_data['all_cells']])
        
        # Credit score
        credit_match = re.search(r'Credit\s*Score[:\s]*(\d+)%?', full_text, re.IGNORECASE)
        if credit_match:
            load_data['credit_score'] = f"{credit_match.group(1)}%"
        
        # Days to pay
        days_match = re.search(r'Days\s*to\s*Pay[:\s]*(\d+)', full_text, re.IGNORECASE)
        if days_match:
            load_data['days_to_pay'] = f"{days_match.group(1)} days"
    
    def _extract_hidden_contact_info(self, load_data):
        """Look for hidden contact info in HTML attributes and JavaScript"""
        
        # Check all onclick events for contact info
        for link in load_data['all_links']:
            onclick = link.get('onclick', '')
            if onclick:
                # Look for any contact patterns
                patterns = [
                    r"contact['\"]?\s*:\s*['\"]([^'\"]+)['\"]",
                    r"email['\"]?\s*:\s*['\"]([^'\"]+)['\"]",
                    r"phone['\"]?\s*:\s*['\"]([^'\"]+)['\"]",
                    r"showContact\s*\(\s*['\"]([^'\"]+)['\"]",
                    r"mailto\s*:\s*['\"]([^'\"]+@[^'\"]+)['\"]"
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, onclick, re.IGNORECASE)
                    if match:
                        contact_info = match.group(1)
                        if '@' in contact_info:
                            load_data['contact_email'] = contact_info
                            print(f"✅ Hidden email found: {contact_info}")
                        elif re.match(r'[\d\-\(\)\.\s]{10,}', contact_info):
                            load_data['contact_phone'] = contact_info
                            print(f"✅ Hidden phone found: {contact_info}")
        
        # Check for data attributes
        for cell in load_data['all_cells']:
            for attr_name, attr_value in cell['attributes'].items():
                if 'email' in attr_name.lower() or 'contact' in attr_name.lower():
                    if '@' in str(attr_value):
                        load_data['contact_email'] = str(attr_value)
                        print(f"✅ Email in attribute {attr_name}: {attr_value}")
        
        # Look for JavaScript variables or hidden form fields
        html = load_data['raw_html']
        js_patterns = [
            r"var\s+email\s*=\s*['\"]([^'\"]+@[^'\"]+)['\"]",
            r"email\s*:\s*['\"]([^'\"]+@[^'\"]+)['\"]",
            r"contact\s*:\s*['\"]([^'\"]+@[^'\"]+)['\"]"
        ]
        
        for pattern in js_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                email = match.group(1)
                load_data['contact_email'] = email
                print(f"✅ Email in JavaScript: {email}")
                break

# Test the enhanced parser
def test_enhanced_parser():
    """Test the enhanced parser with sample data"""
    
    sample_html = '''
    <tr>
        <td>YELLOW DIAMOND CONSULTANTS LLC Days to Pay: 32Credit Score: 91%S.A.F.E.R.</td>
        <td>Small Straight131912</td>
        <td>88141</td>
        <td><a href="mailto:contact@yellowdiamond.com" onclick="showContact('contact@yellowdiamond.com', '555-123-4567')">Contact</a></td>
    </tr>
    '''
    
    soup = BeautifulSoup(sample_html, 'html.parser')
    row = soup.find('tr')
    
    parser = SylectusLoadParser()
    result = parser.parse_load_row_comprehensive(row)
    
    print("📊 Enhanced Parser Test Results:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_enhanced_parser()