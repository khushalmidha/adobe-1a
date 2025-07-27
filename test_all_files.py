#!/usr/bin/env python3
"""Test all files and compare with expected outputs."""

import json
import os
from pathlib import Path

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_text(text):
    return text.strip().rstrip()

def compare_single_file(pred_file, exp_file, filename):
    try:
        pred_data = load_json(pred_file)
        exp_data = load_json(exp_file)
        
        pred_outline = pred_data.get('outline', [])
        exp_outline = exp_data.get('outline', [])
        
        matches = 0
        total = len(exp_outline)
        
        # Create lookup for predicted headings
        pred_lookup = {}
        for heading in pred_outline:
            key = (heading['level'], normalize_text(heading['text']), heading['page'])
            pred_lookup[key] = heading
        
        # Count matches
        for exp_heading in exp_outline:
            exp_key = (exp_heading['level'], normalize_text(exp_heading['text']), exp_heading['page'])
            if exp_key in pred_lookup:
                matches += 1
        
        accuracy = (matches / total) * 100 if total > 0 else 100  # 100% if no headings expected
        
        print(f"{filename}: {matches}/{total} = {accuracy:.1f}%")
        return accuracy
        
    except Exception as e:
        print(f"{filename}: ERROR - {e}")
        return 0

def main():
    test_outputs_dir = "test_outputs"
    expected_dir = "outputs"
    
    print("=== CURRENT ACCURACY ACROSS ALL FILES ===")
    
    total_accuracy = 0
    file_count = 0
    
    for i in range(1, 6):  # file01 to file05
        filename = f"file{i:02d}"
        pred_file = f"{test_outputs_dir}/{filename}.json"
        exp_file = f"{expected_dir}/{filename}.json"
        
        if os.path.exists(pred_file) and os.path.exists(exp_file):
            accuracy = compare_single_file(pred_file, exp_file, filename)
            total_accuracy += accuracy
            file_count += 1
    
    if file_count > 0:
        avg_accuracy = total_accuracy / file_count
        print(f"\nOverall Average: {avg_accuracy:.1f}%")
    
    return total_accuracy, file_count

if __name__ == "__main__":
    main()
