#!/usr/bin/env python3
"""Debug file03.pdf extraction step by step."""

import sys
sys.path.append('src')

from pdf_outline_extractor.extractor_new import PDFOutlineExtractor

def debug_file03_extraction():
    print("=== DEBUGGING FILE03 EXTRACTION STEP BY STEP ===")
    
    extractor = PDFOutlineExtractor()
    
    # Let's manually go through the extraction process
    import fitz
    doc = fitz.open("pdfs/file03.pdf")
    
    # Extract text spans
    all_spans = []
    page_avg_sizes = []
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        page_spans, avg_size = extractor._extract_page_spans(page, page_num)
        all_spans.extend(page_spans)
        page_avg_sizes.append(avg_size)
    
    doc.close()
    
    print(f"Total spans extracted: {len(all_spans)}")
    print(f"Page average sizes: {page_avg_sizes}")
    
    # Group spans by line
    grouped_spans = extractor._group_spans_by_line(all_spans)
    print(f"Grouped spans: {len(grouped_spans)}")
    
    # Detect document type
    doc_type = extractor._detect_document_type(grouped_spans)
    print(f"Document type detected: {doc_type}")
    
    if doc_type in ['form', 'invitation']:
        print("Document type excludes heading extraction")
        return
    
    # Extract hierarchical headings
    print("\n=== EXTRACTING HIERARCHICAL HEADINGS ===")
    hierarchical_headings = extractor._extract_hierarchical_headings(grouped_spans, doc_type)
    
    print(f"Hierarchical headings found: {len(hierarchical_headings)}")
    for i, heading in enumerate(hierarchical_headings):
        print(f"  {i+1}. {heading.get('level', 'UNK')}: '{heading.get('text', '')}' (page {heading.get('page', 0)})")
    
    # Finalize headings
    print("\n=== FINALIZING HEADINGS ===")
    final_headings = extractor._finalize_headings(hierarchical_headings)
    
    print(f"Final headings: {len(final_headings)}")
    for i, heading in enumerate(final_headings):
        print(f"  {i+1}. {heading.get('level', 'UNK')}: '{heading.get('text', '')}' (page {heading.get('page', 0)})")

if __name__ == "__main__":
    debug_file03_extraction()
