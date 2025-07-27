#!/usr/bin/env python3
"""Compare file04 output with expected to see exact issue."""

import json

def compare_file04():
    # Load actual output
    with open("test_outputs/file04.json", "r") as f:
        actual = json.load(f)
    
    # Load expected output  
    with open("outputs/file04.json", "r") as f:
        expected = json.load(f)
    
    print("=== FILE04 COMPARISON ===")
    print(f"Actual outline: {len(actual.get('outline', []))} headings")
    for i, h in enumerate(actual.get('outline', [])):
        print(f"  {i+1}: {h}")
    
    print(f"\nExpected outline: {len(expected.get('outline', []))} headings")
    for i, h in enumerate(expected.get('outline', [])):
        print(f"  {i+1}: {h}")
    
    # Check exact match
    exp_heading = expected['outline'][0]
    exp_key = (exp_heading['level'], exp_heading['text'].strip(), exp_heading['page'])
    print(f"\nExpected key: {exp_key}")
    
    found_match = False
    for act_heading in actual.get('outline', []):
        act_key = (act_heading['level'], act_heading['text'].strip(), act_heading['page'])
        print(f"Actual key: {act_key}")
        if act_key == exp_key:
            found_match = True
            print("✅ MATCH FOUND!")
        else:
            print("❌ No match")
    
    if not found_match:
        print("❌ NO MATCH FOUND")

if __name__ == "__main__":
    compare_file04()
