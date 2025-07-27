#!/usr/bin/env python3
"""Debug script to check what text is on page 9 of file02.pdf."""

import fitz  # PyMuPDF
import sys

def debug_page_text(pdf_path, page_num):
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    
    print(f"=== PAGE {page_num} TEXT ANALYSIS ===")
    
    # Get all text spans with details
    blocks = page.get_text("dict")
    
    for block_idx, block in enumerate(blocks["blocks"]):
        if "lines" in block:
            print(f"\nBlock {block_idx}:")
            for line_idx, line in enumerate(block["lines"]):
                print(f"  Line {line_idx}:")
                for span_idx, span in enumerate(line["spans"]):
                    text = span["text"].strip()
                    if text and ("3." in text or "overview" in text.lower() or "syllabus" in text.lower()):
                        print(f"    Span {span_idx}: '{text}' (size: {span['size']:.1f}, flags: {span['flags']})")
    
    doc.close()

if __name__ == "__main__":
    debug_page_text("pdfs/file02.pdf", 9)  # Page 9 (0-indexed)
