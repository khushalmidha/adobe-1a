#!/usr/bin/env python3
"""Compare file03 predicted vs expected headings."""

import json

def compare_file03():
    # Load both files
    with open('test_outputs/file03.json', 'r') as f:
        pred = json.load(f)
    
    with open('outputs/file03.json', 'r') as f:
        exp = json.load(f)
    
    pred_headings = pred['outline']
    exp_headings = exp['outline']
    
    print(f"PREDICTED: {len(pred_headings)} headings")
    print(f"EXPECTED: {len(exp_headings)} headings")
    print()
    
    # Create lookup for matches
    pred_lookup = set()
    for h in pred_headings:
        key = (h['level'], h['text'].strip(), h['page'])
        pred_lookup.add(key)
    
    print("=== EXPECTED HEADINGS (✓ = found, ✗ = missing) ===")
    for i, h in enumerate(exp_headings):
        key = (h['level'], h['text'].strip(), h['page'])
        status = "✓" if key in pred_lookup else "✗"
        print(f"{status} {h['level']}: '{h['text']}' (page {h['page']})")
    
    print("\n=== PREDICTED HEADINGS NOT IN EXPECTED ===")
    exp_lookup = set()
    for h in exp_headings:
        key = (h['level'], h['text'].strip(), h['page'])
        exp_lookup.add(key)
    
    for h in pred_headings:
        key = (h['level'], h['text'].strip(), h['page'])
        if key not in exp_lookup:
            print(f"EXTRA: {h['level']}: '{h['text']}' (page {h['page']})")

if __name__ == "__main__":
    compare_file03()
