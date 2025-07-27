#!/usr/bin/env python3
"""Debug file03 to understand why no headings are detected."""

import fitz
import sys

def debug_file03():
    doc = fitz.open("pdfs/file03.pdf")
    
    print("=== FILE03 DEBUG: First few pages ===")
    
    for page_num in range(min(3, len(doc))):  # Check first 3 pages
        page = doc[page_num]
        print(f"\n--- PAGE {page_num + 1} ---")
        
        blocks = page.get_text("dict")
        
        for block_idx, block in enumerate(blocks["blocks"]):
            if "lines" in block:
                for line_idx, line in enumerate(block["lines"]):
                    for span_idx, span in enumerate(line["spans"]):
                        text = span["text"].strip()
                        if text and len(text) > 3:
                            size = span.get("size", 12)
                            flags = span.get("flags", 0)
                            x = span["bbox"][0]
                            is_bold = bool(flags & 16)
                            
                            # Show text that might be headings (large, bold, or specific content)
                            if (size >= 14 or is_bold or 
                                any(word in text.lower() for word in [
                                    'ontario', 'digital', 'library', 'summary', 'background', 
                                    'timeline', 'access', 'governance', 'funding'
                                ])):
                                print(f"  {text[:60]:<60} | size={size:.1f} | bold={is_bold} | x={x:.1f}")
    
    doc.close()

if __name__ == "__main__":
    debug_file03()
