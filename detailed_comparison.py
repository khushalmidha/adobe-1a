#!/usr/bin/env python3
"""Detailed comparison to see what we're missing vs what we're detecting."""

import json
import os

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def compare_detailed(pred_file, exp_file, filename):
    print(f"\n=== {filename.upper()} DETAILED COMPARISON ===")
    
    try:
        pred_data = load_json(pred_file)
        exp_data = load_json(exp_file)
        
        pred_outline = pred_data.get('outline', [])
        exp_outline = exp_data.get('outline', [])
        
        print(f"Predicted: {len(pred_outline)} headings")
        print(f"Expected: {len(exp_outline)} headings")
        
        # Show what we predicted
        print(f"\n--- WHAT WE DETECTED ---")
        for i, heading in enumerate(pred_outline):
            print(f"{i+1}. {heading['level']} '{heading['text']}' (page {heading['page']})")
        
        # Show what we missed  
        print(f"\n--- WHAT WE SHOULD DETECT ---")
        pred_lookup = {(h['level'], h['text'].strip(), h['page']) for h in pred_outline}
        
        matches = 0
        for i, heading in enumerate(exp_outline):
            key = (heading['level'], heading['text'].strip(), heading['page'])
            if key in pred_lookup:
                print(f"✅ {i+1}. {heading['level']} '{heading['text']}' (page {heading['page']})")
                matches += 1
            else:
                print(f"❌ {i+1}. {heading['level']} '{heading['text']}' (page {heading['page']})")
        
        accuracy = (matches / len(exp_outline)) * 100 if exp_outline else 0
        print(f"\nAccuracy: {matches}/{len(exp_outline)} = {accuracy:.1f}%")
        
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    # Compare file02 (our best performing one)
    compare_detailed("test_outputs/file02.json", "outputs/file02.json", "file02")
    
    # Compare file04 (100% accurate)
    compare_detailed("test_outputs/file04.json", "outputs/file04.json", "file04")

if __name__ == "__main__":
    main()
