#!/usr/bin/env python3
"""
Simple CLI for testing PDF outline extraction.
"""

import argparse
import json
import sys
from pathlib import Path

from .extractor_new import PDFOutlineExtractor


def main():
    parser = argparse.ArgumentParser(description='Extract outline from PDF')
    parser.add_argument('pdf_file', help='Path to PDF file')
    parser.add_argument('--output', '-o', help='Output JSON file path')
    
    args = parser.parse_args()
    
    try:
        extractor = PDFOutlineExtractor()
        result = extractor.extract_outline(args.pdf_file)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            print(f"Output saved to {args.output}")
        else:
            print(json.dumps(result, indent=4, ensure_ascii=False))
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
