#!/usr/bin/env python3
"""Test form field detection."""

import re

def test_form_field_detection():
    text = "Application form for grant of LTC advance"
    print(f"Testing: '{text}'")
    print(f"Length: {len(text)}")
    
    text_lower = text.strip().lower()
    print(f"Lowercase: '{text_lower}'")
    
    form_indicators = [
        'name', 'designation', 'date', 'service', 'pay', 'whether',
        'home town', 'employed', 'signature', 'place', 'stamp',
        'office', 'department', 'employee', 'id', 'number', 's.no',
        'serial', 'amount', 'rupees', 'advance', 'purpose', 'from',
        'to', 'duration', 'period', 'remarks', 'recommendation',
        'approved', 'sanctioned', 'certified', 'checked'
    ]
    
    # Check exact matches
    if text_lower in form_indicators:
        print("✓ Exact match found")
    else:
        print("✗ No exact match")
    
    # Check contains
    for indicator in form_indicators:
        if indicator in text_lower:
            print(f"✓ Contains '{indicator}'")
            
            # Check conditions
            if len(text_lower) <= 30:
                print(f"  ✓ Length <= 30")
            else:
                print(f"  ✗ Length > 30 ({len(text_lower)})")
                
            if not any(deco in text_lower for deco in ['hope', 'see', 'you', 'there', 'welcome', 'party', 'event']):
                print(f"  ✓ No decorative words")
            else:
                print(f"  ✗ Has decorative words")
                
            if not any(title_pattern in text_lower for title_pattern in ['application form', 'request form', 'form for']):
                print(f"  ✗ No title pattern exclusion")
            else:
                print(f"  ✓ Has title pattern exclusion")

if __name__ == "__main__":
    test_form_field_detection()
