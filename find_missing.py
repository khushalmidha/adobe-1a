#!/usr/bin/env python3

import fitz  # PyMuPDF
from src.pdf_outline_extractor.extractor_new import PDFOutlineExtractor

def find_missing_headings():
    """Find the missing headings by searching all spans."""
    
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
    
    # Look for the missing headings
    missing_searches = [
        'revision history',
        '4. references',
        'references'
    ]
    
    print("SEARCHING FOR MISSING HEADINGS:")
    for search_term in missing_searches:
        print(f"\nSearching for: '{search_term}'")
        found = []
        for span in grouped_spans:
            if search_term.lower() in span['text'].lower():
                found.append({
                    'text': span['text'],
                    'page': span['page'],
                    'font_size': span['font_size'],
                    'position': f"({span['x']}, {span['y']})"
                })
        
        for match in found:
            print(f"  FOUND: '{match['text']}' | Page {match['page']} | Font: {match['font_size']} | Pos: {match['position']}")
    
    # Also look for any span that starts with "4."
    print(f"\nALL SPANS STARTING WITH '4.':")
    for span in grouped_spans:
        if span['text'].strip().startswith('4.'):
            print(f"  '{span['text']}' | Page {span['page']} | Font: {span['font_size']}")

if __name__ == "__main__":
    find_missing_headings()
