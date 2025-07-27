#!/usr/bin/env python3
"""Debug the span grouping for file04."""

from src.pdf_outline_extractor.extractor_new import PDFOutlineExtractor

def debug_span_grouping():
    extractor = PDFOutlineExtractor()
    
    import fitz
    doc = fitz.open("pdfs/file04.pdf")
    
    # Extract spans from first page
    page_spans, avg_size = extractor._extract_page_spans(doc[0], 0)
    
    # Group spans by line
    grouped_spans = extractor._group_spans_by_line(page_spans)
    
    print("Grouped spans from file04:")
    for span in grouped_spans:
        if span['font_size'] > 14:  # Only show larger text
            print(f"Text: '{span['text']}' | Font: {span['font_size']:.1f} | Y: {span['y']:.1f}")
    
    doc.close()

if __name__ == "__main__":
    debug_span_grouping()
