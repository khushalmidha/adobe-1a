#!/usr/bin/env python3
"""Debug file01.pdf title extraction."""

import fitz
from pathlib import Path

def debug_title_extraction(pdf_path):
    print(f"=== DEBUGGING TITLE EXTRACTION FOR {pdf_path} ===")
    
    doc = fitz.open(pdf_path)
    page = doc[0]  # First page
    
    blocks = page.get_text("dict")["blocks"]
    
    print("\n--- ALL TEXT SPANS ON PAGE 0 ---")
    all_spans = []
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if text:
                        span_info = {
                            "text": text,
                            "font_size": span["size"],
                            "x": span["bbox"][0],
                            "y": span["bbox"][1],
                            "width": span["bbox"][2] - span["bbox"][0],
                            "height": span["bbox"][3] - span["bbox"][1]
                        }
                        all_spans.append(span_info)
                        print(f"  '{text}' - Size: {span['size']:.1f}, Y: {span['bbox'][1]:.1f}")
    
    # Calculate page dimensions
    if all_spans:
        page_width = max((s["x"] + s["width"]) for s in all_spans)
        page_height = max(s["y"] + s["height"] for s in all_spans)
        print(f"\nPage dimensions: {page_width:.1f} x {page_height:.1f}")
        
        # Check upper spans (top 50%)
        upper_spans = [s for s in all_spans if s["y"] < page_height * 0.5]
        print(f"Upper spans (top 50%): {len(upper_spans)}")
        
        if upper_spans:
            # Find largest font sizes
            all_font_sizes = [s["font_size"] for s in all_spans]
            max_font_size = max(all_font_sizes) if all_font_sizes else 12.0
            print(f"Max font size: {max_font_size}")
            
            largest_spans = [s for s in upper_spans if s["font_size"] >= max_font_size * 0.95]
            print(f"Largest spans in upper area:")
            for span in largest_spans:
                print(f"  '{span['text']}' - Size: {span['font_size']:.1f}")
    
    doc.close()

if __name__ == "__main__":
    debug_title_extraction("pdfs/file01.pdf")
