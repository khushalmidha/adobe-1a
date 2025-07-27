#!/usr/bin/env python3
"""Debug file03.pdf to understand its content structure."""

import fitz
from pathlib import Path

def analyze_pdf_content(pdf_path):
    print(f"=== ANALYZING {pdf_path} ===")
    
    doc = fitz.open(pdf_path)
    
    for page_num in range(min(3, len(doc))):  # First 3 pages
        page = doc[page_num]
        print(f"\n--- PAGE {page_num + 1} ---")
        
        blocks = page.get_text("dict")["blocks"]
        
        for block_idx, block in enumerate(blocks):
            if "lines" in block:
                print(f"\nBlock {block_idx}:")
                bbox = block["bbox"]
                print(f"  bbox: {bbox}")
                print(f"  x0: {bbox[0]:.1f}, width: {bbox[2] - bbox[0]:.1f}")
                
                for line_idx, line in enumerate(block["lines"]):
                    line_text = ""
                    font_sizes = []
                    
                    for span in line["spans"]:
                        line_text += span["text"]
                        font_sizes.append(span["size"])
                    
                    if line_text.strip():
                        avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 0
                        print(f"    Line {line_idx}: '{line_text.strip()}'")
                        print(f"      Font size: {avg_font_size:.1f}")
                        print(f"      Line bbox: {line['bbox']}")
    
    doc.close()

if __name__ == "__main__":
    analyze_pdf_content("pdfs/file03.pdf")
