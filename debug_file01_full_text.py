#!/usr/bin/env python3
"""Check what actual text is on file01 first page."""

import fitz  # PyMuPDF

def extract_first_page_text():
    doc = fitz.open("pdfs/file01.pdf")
    page = doc[0]
    
    # Get all text blocks
    text_blocks = page.get_text("dict")["blocks"]
    
    all_text = ""
    for block in text_blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    all_text += span["text"] + " "
    
    print(f"All text from first page:\n{all_text[:500]}...")
    print(f"\nLowercase: {all_text.lower()[:500]}...")
    
    # Check invitation filter
    filter_phrases = [
        'hope to see', 'pigeon forge', 'rsvp', 'party', 'event', 
        'invitation', 'please visit', 'waiver', 'topjump'
    ]
    
    print("\nInvitation filter check:")
    for phrase in filter_phrases:
        if phrase in all_text.lower():
            print(f"MATCH FOUND: '{phrase}' is in the full text!")
            
    doc.close()

if __name__ == "__main__":
    extract_first_page_text()
