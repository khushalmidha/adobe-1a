#!/usr/bin/env python3
"""Debug the margin grouping and hierarchy detection for file03."""

import sys
sys.path.append('src')
from pdf_outline_extractor.extractor_new import PDFOutlineExtractor

def debug_file03_hierarchy():
    print("=== FILE03 HIERARCHY DEBUG ===")
    
    extractor = PDFOutlineExtractor()
    
    # Extract spans like the main algorithm does
    import fitz
    doc = fitz.open("pdfs/file03.pdf")
    
    all_spans = []
    for page_num in range(min(3, len(doc))):  # First 3 pages
        page = doc[page_num]
        page_spans, _ = extractor._extract_page_spans(page, page_num)
        all_spans.extend(page_spans)
    
    doc.close()
    
    # Group spans by line
    grouped_spans = extractor._group_spans_by_line(all_spans)
    
    # Filter potential headings
    potential_headings = []
    for span in grouped_spans:
        text = span["text"].strip()
        if not text or extractor._should_skip_span(text):
            continue
        
        if text.count('.') > 20:
            continue
        
        if len(text) > 150:
            continue
        
        potential_headings.append(span)
    
    print(f"Found {len(potential_headings)} potential headings after filtering")
    
    # Show potential headings by margin position
    for span in potential_headings[:20]:  # First 20
        text = span["text"].strip()
        x = span.get("x0", span.get("x", 0))
        size = span.get("size", span.get("font_size", 12))
        page = span.get("page", 0)
        
        # Check if it would be classified as heading
        is_heading = extractor._is_likely_heading(span, text)
        suggested_level = span.get('suggested_level', 'None')
        
        print(f"Page {page} | x={x:5.1f} | size={size:4.1f} | {is_heading} | {suggested_level} | {text[:50]}")

if __name__ == "__main__":
    debug_file03_hierarchy()
