#!/usr/bin/env python3

import json
import fitz  # PyMuPDF
from src.pdf_outline_extractor.extractor_new import PDFOutlineExtractor

def debug_file02():
    """Debug file02 specifically to understand what headings to match."""
    
    # Load expected output
    with open('outputs/file02.json', 'r', encoding='utf-8') as f:
        expected = json.load(f)
    
    print("EXPECTED HEADINGS FOR FILE02:")
    for i, heading in enumerate(expected['outline'], 1):
        print(f"{i:2d}. {heading['level']} | '{heading['text']}' | Page {heading['page']}")
    
    print("\n" + "="*60)
    print("ANALYZING PDF FILE02 SPANS...")
    
    # Extract all spans from file02
    extractor = PDFOutlineExtractor()
    doc = fitz.open('pdfs/file02.pdf')
    
    all_spans = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        spans, _ = extractor._extract_page_spans(page, page_num)
        all_spans.extend(spans)
    
    doc.close()
    
    # Group spans by line
    grouped_spans = extractor._group_spans_by_line(all_spans)
    
    # Look for the expected heading texts
    expected_texts = [h['text'].strip() for h in expected['outline']]
    
    print(f"\nLOOKING FOR THESE {len(expected_texts)} EXPECTED HEADINGS:")
    for i, text in enumerate(expected_texts, 1):
        print(f"{i:2d}. '{text}'")
    
    print(f"\nSCANNING {len(grouped_spans)} GROUPED SPANS...")
    
    found_matches = []
    
    for span in grouped_spans:
        text = span['text']
        text_stripped = text.strip()
        
        # Check if this span text matches any expected heading
        for expected_text in expected_texts:
            if text_stripped == expected_text or text == expected_text:
                found_matches.append({
                    'expected': expected_text,
                    'actual': text,
                    'page': span['page'],
                    'font_size': span['font_size'],
                    'x': span['x'],
                    'y': span['y']
                })
                print(f"MATCH: '{text}' (Page {span['page']}, Font: {span['font_size']}, Pos: {span['x']},{span['y']})")
    
    print(f"\nFOUND {len(found_matches)} EXACT MATCHES out of {len(expected_texts)} expected")
    
    if len(found_matches) < len(expected_texts):
        print("\nMISSING HEADINGS - checking for partial matches...")
        for expected_text in expected_texts:
            found = False
            for match in found_matches:
                if match['expected'] == expected_text:
                    found = True
                    break
            
            if not found:
                print(f"MISSING: '{expected_text}'")
                # Look for partial matches
                best_matches = []
                for span in grouped_spans:
                    span_text = span['text'].strip()
                    # Check for various partial match conditions
                    if (expected_text.lower() in span_text.lower() or
                        span_text.lower() in expected_text.lower() or
                        any(word in span_text.lower() for word in expected_text.lower().split()[:3])):
                        best_matches.append({
                            'text': span['text'],
                            'page': span['page'],
                            'font_size': span['font_size'],
                            'similarity': len(set(expected_text.lower().split()) & set(span_text.lower().split()))
                        })
                
                # Sort by similarity and show top 3
                best_matches.sort(key=lambda x: x['similarity'], reverse=True)
                for match in best_matches[:3]:
                    print(f"  PARTIAL: '{match['text']}' (Page {match['page']}, Similarity: {match['similarity']})")

if __name__ == "__main__":
    debug_file02()
