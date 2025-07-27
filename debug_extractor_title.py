#!/usr/bin/env python3
"""Debug file01.pdf title extraction with the actual extractor."""

from src.pdf_outline_extractor.extractor_new import PDFOutlineExtractor

def debug_title_extraction():
    extractor = PDFOutlineExtractor()
    
    # Test the _is_form_field method directly
    text = "Application form for grant of LTC advance"
    is_form_field = extractor._is_form_field(text)
    print(f"_is_form_field('{text}') = {is_form_field}")
    
    # Test the _looks_like_title method if it exists
    try:
        looks_like_title = extractor._looks_like_title(text)
        print(f"_looks_like_title('{text}') = {looks_like_title}")
    except AttributeError:
        print("_looks_like_title method not found")
    
    # Extract and show the actual result
    result = extractor.extract_outline("pdfs/file01.pdf")
    print(f"Actual title extracted: '{result['title']}'")

if __name__ == "__main__":
    debug_title_extraction()
