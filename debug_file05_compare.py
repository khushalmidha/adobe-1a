#!/usr/bin/env python3
"""Compare file05 output with expected."""

import json

def compare_file05():
    # Load actual output
    with open("test_outputs/file05.json", "r") as f:
        actual = json.load(f)
    
    # Load expected output  
    with open("outputs/file05.json", "r") as f:
        expected = json.load(f)
    
    print("=== FILE05 COMPARISON ===")
    print(f"Actual: {actual.get('outline', [])}")
    print(f"Expected: {expected.get('outline', [])}")
    
    # Check exact text match
    if actual.get('outline') and expected.get('outline'):
        actual_text = actual['outline'][0]['text']
        expected_text = expected['outline'][0]['text']
        print(f"\nActual text: '{actual_text}'")
        print(f"Expected text: '{expected_text}'")
        print(f"Match: {actual_text.strip() == expected_text.strip()}")

if __name__ == "__main__":
    compare_file05()
