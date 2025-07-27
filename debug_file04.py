#!/usr/bin/env python3
"""Debug file04 to see why PATHWAY OPTIONS is not detected."""

import fitz
import sys
sys.path.append('src')
from pdf_outline_extractor.extractor_new import PDFOutlineExtractor

def debug_file04():
    print("=== FILE04 DEBUG ===")
    
    doc = fitz.open("pdfs/file04.pdf")
    page = doc[0]  # Only 1 page
    
    print("Looking for text containing 'pathway' or 'options':")
    
    blocks = page.get_text("dict")
    
    for block_idx, block in enumerate(blocks["blocks"]):
        if "lines" in block:
            for line_idx, line in enumerate(block["lines"]):
                for span_idx, span in enumerate(line["spans"]):
                    text = span["text"].strip()
                    if text and ('pathway' in text.lower() or 'options' in text.lower()):
                        size = span.get("size", 12)
                        flags = span.get("flags", 0)
                        x = span["bbox"][0]
                        is_bold = bool(flags & 16)
                        print(f"  '{text}' | size={size:.1f} | bold={is_bold} | x={x:.1f}")
    
    doc.close()

    # Test with extractor
    extractor = PDFOutlineExtractor()
    result = extractor.extract_outline("pdfs/file04.pdf")
    print(f"\nExtractor result: {len(result.get('outline', []))} headings")
    for heading in result.get('outline', []):
        print(f"  {heading}")

if __name__ == "__main__":
    debug_file04()
