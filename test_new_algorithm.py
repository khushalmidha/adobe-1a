#!/usr/bin/env python3

import json
from src.pdf_outline_extractor.extractor_new import PDFOutlineExtractor

def test_new_algorithm():
    """Test the new exact matching algorithm on file02."""
    
    # Load expected output
    with open('outputs/file02.json', 'r', encoding='utf-8') as f:
        expected = json.load(f)
    
    # Extract using new algorithm
    extractor = PDFOutlineExtractor()
    result = extractor.extract_outline('pdfs/file02.pdf')
    
    print("=== NEW ALGORITHM RESULTS FOR FILE02 ===")
    print(f"Title: '{result['title']}'")
    print(f"Headings count: {len(result['outline'])}")
    print()
    
    print("DETECTED HEADINGS:")
    for i, heading in enumerate(result['outline'], 1):
        print(f"{i:2d}. {heading['level']} | '{heading['text']}' | Page {heading['page']}")
    
    print()
    print("EXPECTED HEADINGS:")
    for i, heading in enumerate(expected['outline'], 1):
        print(f"{i:2d}. {heading['level']} | '{heading['text']}' | Page {heading['page']}")
    
    # Check matches
    print()
    print("MATCHES:")
    matches = 0
    for expected_heading in expected['outline']:
        for actual_heading in result['outline']:
            if (expected_heading['text'].strip() == actual_heading['text'].strip() and
                expected_heading['page'] == actual_heading['page']):
                matches += 1
                print(f"✓ MATCH: '{expected_heading['text']}' | Page {expected_heading['page']}")
                break
    
    print(f"\nTOTAL MATCHES: {matches} out of {len(expected['outline'])}")

if __name__ == "__main__":
    test_new_algorithm()
