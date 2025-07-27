#!/usr/bin/env python3
"""Quick comparison script to check accuracy after Syllabus fix."""

import json

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalize_text(text):
    """Normalize text for comparison."""
    return text.strip().rstrip()

def compare_outlines(predicted_file, expected_file):
    pred_data = load_json(predicted_file)
    exp_data = load_json(expected_file)
    
    pred_outline = pred_data.get('outline', [])
    exp_outline = exp_data.get('outline', [])
    
    print(f"Predicted: {len(pred_outline)} headings")
    print(f"Expected: {len(exp_outline)} headings")
    
    matches = 0
    total = len(exp_outline)
    
    # Create lookup for predicted headings
    pred_lookup = {}
    for heading in pred_outline:
        key = (heading['level'], normalize_text(heading['text']), heading['page'])
        pred_lookup[key] = heading
    
    print("\nComparison details:")
    for i, exp_heading in enumerate(exp_outline):
        exp_key = (exp_heading['level'], normalize_text(exp_heading['text']), exp_heading['page'])
        
        if exp_key in pred_lookup:
            matches += 1
            print(f"✅ Match {i+1}: {exp_heading['level']} '{exp_heading['text']}' (page {exp_heading['page']})")
        else:
            print(f"❌ Missing {i+1}: {exp_heading['level']} '{exp_heading['text']}' (page {exp_heading['page']})")
    
    accuracy = (matches / total) * 100 if total > 0 else 0
    print(f"\nAccuracy: {matches}/{total} = {accuracy:.1f}%")
    
    return accuracy

if __name__ == "__main__":
    compare_outlines(
        "test_fixed_syllabus.json",
        "outputs/file02.json"
    )
