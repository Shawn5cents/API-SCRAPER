#!/usr/bin/env python3
"""
Test improved parser with real data to verify dims, weight, pieces extraction
"""

import json
from bs4 import BeautifulSoup
from enhanced_parser import SylectusLoadParser

def test_improved_parser():
    print("🧪 Testing improved parser with real data...")
    
    # Load real data
    with open('load_details_20250706_210059_567093.json', 'r') as f:
        load_data = json.load(f)
    
    print(f"🔍 Original parsing results:")
    print(f"   Miles: {load_data.get('miles', 'Unknown')}")
    print(f"   Pieces: {load_data.get('pieces', 'Unknown')}")
    print(f"   Weight: {load_data.get('weight', 'Unknown')}")
    print(f"   Vehicle: {load_data.get('vehicle_type', 'Unknown')}")
    print(f"   Dimensions: {load_data.get('dimensions', 'Unknown')}")
    
    # Test with improved parser
    soup = BeautifulSoup(load_data['raw_html'], 'html.parser')
    row = soup.find('tr')
    
    if row:
        parser = SylectusLoadParser()
        result = parser.parse_load_row_comprehensive(row)
        
        print(f"\n✨ Improved parsing results:")
        print(f"   Miles: {result.get('miles', 'Unknown')}")
        print(f"   Pieces: {result.get('pieces', 'Unknown')}")
        print(f"   Weight: {result.get('weight', 'Unknown')}")
        print(f"   Vehicle: {result.get('vehicle_type', 'Unknown')}")
        print(f"   Dimensions: {result.get('dimensions', 'Unknown')}")
        
        # Check specific cell data
        print(f"\n🔍 Cell analysis:")
        for cell in result['all_cells']:
            if cell['index'] in [6, 7]:
                print(f"   Cell {cell['index']}: '{cell['text']}' (HTML: {cell['html'][:100]}...)")
        
        return result
    
    return None

def test_with_sample_data():
    print(f"\n🧪 Testing with sample data containing dimensions...")
    
    sample_html = '''
    <tr>
        <td>TEST COMPANY LLC Days to Pay: 30Credit Score: 95%</td>
        <td>Straight Truck123456</td>
        <td>789012</td>
        <td>DALLAS, TX 75201ASAP</td>
        <td>HOUSTON, TX 77001ASAP</td>
        <td>07/07/2025 08:0007/07/2025 14:00</td>
        <td>STRAIGHT TRUCK2500</td>
        <td>2<br/>250</td>
        <td>48x96x108</td>
    </tr>
    '''
    
    soup = BeautifulSoup(sample_html, 'html.parser')
    row = soup.find('tr')
    
    parser = SylectusLoadParser()
    result = parser.parse_load_row_comprehensive(row)
    
    print(f"   Company: {result.get('company', 'Unknown')}")
    print(f"   Load ID: {result.get('load_id', 'Unknown')}")
    print(f"   Miles: {result.get('miles', 'Unknown')}")
    print(f"   Pieces: {result.get('pieces', 'Unknown')}")
    print(f"   Weight: {result.get('weight', 'Unknown')}")
    print(f"   Vehicle: {result.get('vehicle_type', 'Unknown')}")
    print(f"   Dimensions: {result.get('dimensions', 'Unknown')}")
    print(f"   Length: {result.get('length', 'Unknown')}")
    print(f"   Width: {result.get('width', 'Unknown')}")
    print(f"   Height: {result.get('height', 'Unknown')}")

if __name__ == "__main__":
    test_improved_parser()
    test_with_sample_data()