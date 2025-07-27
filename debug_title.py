#!/usr/bin/env python3

import sys
sys.path.insert(0, 'src')

from src.pdf_outline_extractor.extractor_new import PDFOutlineExtractor

# Debug title extraction for file05
extractor = PDFOutlineExtractor()

# Let's debug the actual span processing
import fitz
doc = fitz.open("pdfs/file05.pdf")
page = doc[0]
blocks = page.get_text("dict")

# Process exactly as the extractor does
spans = []
for block in blocks["blocks"]:
    if "lines" in block:
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if text:
                    spans.append({
                        "text": text,
                        "font_size": span["size"],
                        "x": span["bbox"][0],
                        "y": span["bbox"][1],
                        "width": span["bbox"][2] - span["bbox"][0],
                        "height": span["bbox"][3] - span["bbox"][1],
                        "page": 0
                    })

# Calculate page dimensions
page_width = max((s["x"] + s["width"]) for s in spans) if spans else 1
page_height = max(s["y"] + s["height"] for s in spans) if spans else 1

print(f"Page dimensions: {page_width} x {page_height}")

# Filter upper spans (top 30%)
upper_spans = [s for s in spans if s["y"] < page_height * 0.3]
print(f"\nUpper spans (top 30%, y < {page_height * 0.3}):")
for span in upper_spans:
    print(f"  '{span['text']}' (size: {span['font_size']}, y: {span['y']})")

# Find max font size among all spans
if spans:
    max_font_size = max(s["font_size"] for s in spans)
    print(f"\nMax font size on page: {max_font_size}")
    
    largest_spans = [s for s in spans if s["font_size"] >= max_font_size * 0.95]
    print(f"All largest spans (>= {max_font_size * 0.95}):")
    for span in sorted(largest_spans, key=lambda x: (x["y"], x["x"])):
        print(f"  '{span['text']}' (size: {span['font_size']}, y: {span['y']}, x: {span['x']})")
    
    # Check if Foundation Level Extensions is close to Overview
    overview_span = None
    foundation_span = None
    for span in largest_spans:
        if "Overview" in span["text"]:
            overview_span = span
        elif "Foundation Level Extensions" in span["text"]:
            foundation_span = span
    
    if overview_span and foundation_span:
        y_diff = abs(overview_span["y"] - foundation_span["y"])
        print(f"\nY difference between Overview and Foundation: {y_diff}")
        print(f"Should be considered as title parts: {y_diff < 30}")  # Reasonable threshold

# Now test our extractor
result = extractor.extract_outline("pdfs/file02.pdf")
print(f"\nDetected title: '{result['title']}'")
print(f"Expected title: 'Overview  Foundation Level Extensions  '")
