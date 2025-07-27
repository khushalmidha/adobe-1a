#!/usr/bin/env python3

import sys
sys.path.insert(0, 'src')

import fitz
doc = fitz.open("pdfs/file05.pdf")
page = doc[0]
blocks = page.get_text("dict")

print("=== FILE05 DEBUG ===")
print(f"Document has {len(doc)} pages")

print("\nAll text spans on page 0:")
for i, block in enumerate(blocks["blocks"]):
    if "lines" in block:
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()
                if text:
                    print(f"  '{text}' (size: {span['size']:.1f}, bbox: {span['bbox']})")

# Test our extractor
from src.pdf_outline_extractor.extractor_new import PDFOutlineExtractor
extractor = PDFOutlineExtractor()
result = extractor.extract_outline("pdfs/file05.pdf")

print(f"\nOur result:")
print(f"Title: '{result['title']}'")
print(f"Outline count: {len(result['outline'])}")
for heading in result['outline']:
    print(f"  {heading['level']} | '{heading['text']}' | Page {heading['page']}")

print(f"\nExpected result:")
print(f"Title: ''")
print(f"Outline: H1 | 'HOPE To SEE You THERE!' | Page 0")
