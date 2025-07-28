#!/usr/bin/env python3
"""
Main entry point for Adobe Hackathon Round 1A - PDF Outline Extractor
Processes all PDFs from /app/input and generates JSON outputs in /app/output
"""

import json
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any

# Import the PDF outline extractor
from src.pdf_outline_extractor.extractor_new import PDFOutlineExtractor
from src.pdf_outline_extractor.json_writer_new import JSONWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_pdf_file(pdf_path: Path, output_path: Path, extractor: PDFOutlineExtractor) -> bool:
    """
    Process a single PDF file and save the outline as JSON.
    
    Args:
        pdf_path: Path to the input PDF file
        output_path: Path to save the output JSON file
        extractor: PDFOutlineExtractor instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Processing: {pdf_path.name}")
        
        # Extract outline from PDF
        result = extractor.extract_outline(str(pdf_path))
        
        if not result:
            logger.warning(f"No outline extracted from {pdf_path.name}")
            # Create empty result structure
            result = {
                "title": "",
                "outline": []
            }
        
        # Save as JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully processed {pdf_path.name} -> {output_path.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {pdf_path.name}: {str(e)}")
        # Create error result
        error_result = {
            "title": "",
            "outline": [],
            "error": str(e)
        }
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2, ensure_ascii=False)
        except:
            pass
        return False


def main():
    """
    Main function that processes all PDFs from /app/input directory
    and generates corresponding JSON files in /app/output directory.
    """
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    logger.info("Starting PDF Outline Extractor for Adobe Hackathon Round 1A")
    logger.info(f"Input directory: {input_dir}")
    logger.info(f"Output directory: {output_dir}")
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if input directory exists
    if not input_dir.exists():
        logger.error(f"Input directory {input_dir} does not exist")
        sys.exit(1)
    
    # Find all PDF files in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        sys.exit(0)
    
    logger.info(f"Found {len(pdf_files)} PDF file(s) to process")
    
    # Initialize the extractor with optimized parameters
    extractor = PDFOutlineExtractor(
        min_h1_size_ratio=1.5,
        min_h2_size_ratio=1.3,
        min_h3_size_ratio=1.1
    )
    
    # Process each PDF file
    successful = 0
    failed = 0
    
    for pdf_path in pdf_files:
        # Generate corresponding JSON output filename
        json_filename = pdf_path.stem + ".json"
        output_path = output_dir / json_filename
        
        # Process the PDF
        if process_pdf_file(pdf_path, output_path, extractor):
            successful += 1
        else:
            failed += 1
    
    # Summary
    logger.info(f"Processing complete: {successful} successful, {failed} failed")
    
    if failed > 0:
        logger.warning(f"{failed} files failed to process")
        sys.exit(1)
    else:
        logger.info("All files processed successfully")
        sys.exit(0)


if __name__ == "__main__":
    main()
