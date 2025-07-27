#!/usr/bin/env python3
"""Debug file03.pdf heading detection."""

import fitz
from pathlib import Path

def debug_heading_detection(pdf_path):
    print(f"=== DEBUGGING HEADING DETECTION FOR {pdf_path} ===")
    
    doc = fitz.open(pdf_path)
    
    # Check pages 1-3 where most headings should be
    for page_num in range(min(3, len(doc))):
        page = doc[page_num]
        print(f"\n--- PAGE {page_num + 1} ---")
        
        blocks = page.get_text("dict")["blocks"]
        
        heading_candidates = []
        
        for block_idx, block in enumerate(blocks):
            if "lines" in block:
                bbox = block["bbox"]
                x0 = bbox[0]
                
                for line_idx, line in enumerate(block["lines"]):
                    line_text = ""
                    avg_size = 0
                    flags = 0
                    
                    for span in line["spans"]:
                        line_text += span["text"]
                        avg_size = span["size"]  # Take last span size
                        flags = span.get("flags", 0)
                    
                    text = line_text.strip()
                    if not text:
                        continue
                    
                    is_bold = bool(flags & 16)
                    
                    # Check if this looks like a heading
                    is_heading_candidate = False
                    reasoning = []
                    
                    # Check length (short is good)
                    if len(text.split()) <= 3:
                        reasoning.append("short_text")
                    
                    # Check font size
                    if avg_size >= 12:
                        reasoning.append(f"size_{avg_size:.1f}")
                    
                    # Check if bold
                    if is_bold:
                        reasoning.append("bold")
                    
                    # Check specific keywords for file03
                    text_lower = text.lower()
                    file03_keywords = [
                        'summary', 'background', 'timeline', 'methodology', 
                        'deliverables', 'budget', 'evaluation', 'conclusion',
                        'appendix', 'phase', 'preamble', 'terms', 'membership',
                        'appointment', 'chair', 'meetings', 'accountability',
                        'financial', 'policies', 'resources'
                    ]
                    
                    for keyword in file03_keywords:
                        if keyword in text_lower:
                            reasoning.append(f"keyword_{keyword}")
                    
                    # Check for colon endings (H3 pattern)
                    if text.endswith(':'):
                        reasoning.append("colon_ending")
                    
                    # Determine if it's a candidate
                    if (len(text.split()) <= 4 and avg_size >= 11) or reasoning:
                        is_heading_candidate = True
                    
                    if is_heading_candidate:
                        print(f"  CANDIDATE: '{text}'")
                        print(f"    Size: {avg_size:.1f}, Bold: {is_bold}, X0: {x0:.1f}")
                        print(f"    Reasoning: {', '.join(reasoning)}")
                        
                        # Suggest level
                        suggested_level = "UNKNOWN"
                        if avg_size >= 16:
                            suggested_level = "H1"
                        elif avg_size >= 12 and avg_size < 16:
                            if any(kw in text_lower for kw in ['summary', 'background', 'appendix']):
                                suggested_level = "H2"
                        elif text.endswith(':') and avg_size >= 11:
                            suggested_level = "H3"
                        
                        print(f"    Suggested Level: {suggested_level}")
                        print()
    
    doc.close()

if __name__ == "__main__":
    debug_heading_detection("pdfs/file03.pdf")
