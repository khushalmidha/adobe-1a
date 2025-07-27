#!/usr/bin/env python3

import sys
sys.path.insert(0, 'src')

from src.pdf_outline_extractor.extractor_new import PDFOutlineExtractor

# Create an extractor and manually debug the grouping process
extractor = PDFOutlineExtractor()

# Process the PDF manually to see grouping
import fitz
doc = fitz.open("pdfs/file05.pdf")
page = doc[0]
blocks = page.get_text("dict")

# Build spans as extractor does
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

print("=== BEFORE GROUPING ===")
hope_spans = [s for s in spans if any(word in s["text"] for word in ["HOPE", "To", "SEE", "You", "HERE", "!"])]
for span in hope_spans:
    print(f"'{span['text']}' (size: {span['font_size']}, y: {span['y']}, x: {span['x']})")

# Test grouping
grouped_spans = extractor._group_spans_by_line(spans)

print(f"\n=== AFTER GROUPING ===")
print(f"Original spans: {len(spans)}, Grouped spans: {len(grouped_spans)}")

# Find the grouped span containing HOPE
hope_grouped = [s for s in grouped_spans if "HOPE" in s["text"]]
if hope_grouped:
    for span in hope_grouped:
        print(f"Grouped: '{span['text']}' (size: {span['font_size']}, y: {span['y']})")
else:
    print("No grouped span found containing HOPE")
    
# Check if it's being filtered out
print(f"\n=== FILTERING CHECKS ===")
if hope_grouped:
    span = hope_grouped[0]
    text = span["text"].strip()
    
    print(f"Text: '{text}'")
    print(f"Length: {len(text)}")
    print(f"Is form field: {extractor._is_form_field(text)}")
    print(f"Is body text: {extractor._is_body_text(text)}")
    print(f"Is page element: {extractor._is_page_element(text)}")
    
    # Check document type detection
    doc_type = extractor._detect_document_type(grouped_spans)
    print(f"Document type: {doc_type}")
    
    # Check heading score
    page_avg_sizes = [12.0]  # dummy
    page_avg = page_avg_sizes[0]
    size_ratio = span["font_size"] / page_avg
    print(f"Size ratio: {size_ratio}")
    
    all_font_sizes = [s["font_size"] for s in grouped_spans]
    font_size_75th = sorted(all_font_sizes)[int(len(all_font_sizes) * 0.75)]
    font_size_90th = sorted(all_font_sizes)[int(len(all_font_sizes) * 0.90)]
    
    heading_score = extractor._calculate_heading_score(span, size_ratio, font_size_75th, font_size_90th)
    print(f"Heading score: {heading_score}")
    print(f"Score > 0.3: {heading_score > 0.3}")
