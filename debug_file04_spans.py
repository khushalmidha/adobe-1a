#!/usr/bin/env python3
"""Debug file04 text to understand what should be headings."""

import fitz  # PyMuPDF

def debug_file04_spans():
    doc = fitz.open("pdfs/file04.pdf")
    page = doc[0]
    
    # Get text with detailed positioning
    text_dict = page.get_text("dict")
    
    print("File04 text elements:")
    for block_idx, block in enumerate(text_dict["blocks"]):
        if "lines" in block:
            for line_idx, line in enumerate(block["lines"]):
                for span_idx, span in enumerate(line["spans"]):
                    x, y = span["bbox"][:2]
                    text = span["text"].strip()
                    font_size = span["size"]
                    if text:
                        print(f"Text: '{text}' | Font: {font_size:.1f} | Position: ({x:.1f}, {y:.1f})")
    
    doc.close()

if __name__ == "__main__":
    debug_file04_spans()
