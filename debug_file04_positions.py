#!/usr/bin/env python3
"""Debug X positions to understand layout structure."""

import fitz

def debug_positioning():
    doc = fitz.open("pdfs/file04.pdf")
    page = doc[0]
    text_dict = page.get_text("dict")
    
    print("15.3 font size elements with positions:")
    for block in text_dict["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    if abs(span["size"] - 15.3) < 0.1:  # Font size 15.3
                        x, y = span["bbox"][:2]
                        width = span["bbox"][2] - span["bbox"][0]
                        text = span["text"].strip()
                        print(f"Text: '{text}' | X: {x:.1f} | Y: {y:.1f} | Width: {width:.1f}")
    
    # Get page width for reference
    page_rect = page.rect
    print(f"\nPage width: {page_rect.width:.1f}")
    
    doc.close()

if __name__ == "__main__":
    debug_positioning()
