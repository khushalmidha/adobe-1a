#!/usr/bin/env python3

import json
import sys
sys.path.insert(0, 'src')

# Debug all test cases
files = ['file01', 'file02', 'file03', 'file04', 'file05']

for file_name in files:
    print(f"\n{'='*60}")
    print(f"DEBUGGING {file_name.upper()}")
    print(f"{'='*60}")
    
    # Load expected and actual results
    try:
        with open(f"outputs/{file_name}.json", 'r', encoding='utf-8') as f:
            expected = json.load(f)
        
        with open(f"test_outputs/{file_name}.json", 'r', encoding='utf-8') as f:
            actual = json.load(f)
        
        # Compare titles
        print(f"TITLE:")
        print(f"  Expected: '{expected['title']}'")
        print(f"  Actual:   '{actual['title']}'")
        print(f"  Match:    {expected['title'] == actual['title']}")
        
        # Compare outline counts
        exp_count = len(expected['outline'])
        act_count = len(actual['outline'])
        print(f"\nOUTLINE COUNT:")
        print(f"  Expected: {exp_count}")
        print(f"  Actual:   {act_count}")
        print(f"  Match:    {exp_count == act_count}")
        
        # Show expected headings
        print(f"\nEXPECTED HEADINGS:")
        if exp_count == 0:
            print("  (No headings expected)")
        else:
            for i, heading in enumerate(expected['outline']):
                print(f"  {i+1}. {heading['level']} | '{heading['text']}' | Page {heading['page']}")
        
        # Show actual headings (first 10)
        print(f"\nACTUAL HEADINGS (first 10):")
        if act_count == 0:
            print("  (No headings detected)")
        else:
            for i, heading in enumerate(actual['outline'][:10]):
                print(f"  {i+1}. {heading['level']} | '{heading['text']}' | Page {heading['page']}")
            if act_count > 10:
                print(f"  ... and {act_count - 10} more")
        
        # Check for exact matches
        if exp_count > 0 and act_count > 0:
            exp_tuples = set((h['level'], h['text'].strip(), h['page']) for h in expected['outline'])
            act_tuples = set((h['level'], h['text'].strip(), h['page']) for h in actual['outline'])
            matches = exp_tuples & act_tuples
            print(f"\nEXACT MATCHES: {len(matches)} out of {exp_count}")
            if matches:
                for match in sorted(matches):
                    print(f"  ✓ {match[0]} | '{match[1]}' | Page {match[2]}")
        
    except Exception as e:
        print(f"Error processing {file_name}: {e}")

print(f"\n{'='*60}")
print("SUMMARY: All test cases have 0 exact matches!")
print("The heading detection algorithm needs complete restructuring.")
print("Focus should be on:")
print("1. Detecting ONLY the headings that appear in expected output")
print("2. Using hierarchical structure, not just font sizes")
print("3. Exact text matching including case and spacing")
print("='*60")
