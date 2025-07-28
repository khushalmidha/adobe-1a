#!/usr/bin/env python3
"""
Script to process all PDFs from the pdfs folder and save JSON outputs to test_output folder.
"""

import json
import sys
from pathlib import Path

# Add src to path so we can import the modules
sys.path.append('src')

from pdf_outline_extractor.extractor_new import PDFOutlineExtractor


def main():
    """Process all PDF files from pdfs directory and save results to test_output directory."""
    input_dir = Path("../pdfs")
    output_dir = Path("../test_output")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        print(f"Error: Input directory {input_dir} does not exist")
        sys.exit(1)
    
    # Find all PDF files in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    extractor = PDFOutlineExtractor()
    
    for pdf_file in pdf_files:
        try:
            print(f"Processing {pdf_file.name}...")
            
            # Extract outline
            result = extractor.extract_outline(str(pdf_file))
            
            # Save result with same filename but .json extension
            output_file = output_dir / f"{pdf_file.stem}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=True)
            
            print(f"  -> Saved to {output_file}")
            
        except Exception as e:
            print(f"Error processing {pdf_file.name}: {e}")
            continue
    
    print("Processing complete!")


if __name__ == "__main__":
    main()
