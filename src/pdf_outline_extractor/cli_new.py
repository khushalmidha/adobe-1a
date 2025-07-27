#!/usr/bin/env python3
"""
Command Line Interface for PDF Outline Extractor.
Adobe Hackathon Round 1A submission - Pure Python implementation.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any
import time

from .extractor_new import PDFOutlineExtractor


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def extract_outlines(input_dir: str, output_dir: str, **kwargs):
    """
    Extract outlines from all PDF files in input directory.
    
    Args:
        input_dir: Directory containing PDF files
        output_dir: Directory to save JSON output files
        **kwargs: Additional parameters for PDFOutlineExtractor
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Initialize extractor with custom parameters
    extractor_params = {
        'min_h1_size_ratio': kwargs.get('min_h1_size_ratio', 1.5),
        'min_h2_size_ratio': kwargs.get('min_h2_size_ratio', 1.3),
        'min_h3_size_ratio': kwargs.get('min_h3_size_ratio', 1.1),
        'h2_indent_threshold': kwargs.get('h2_indent_threshold', 20.0),
        'h3_indent_threshold': kwargs.get('h3_indent_threshold', 40.0),
    }
    
    extractor = PDFOutlineExtractor(**extractor_params)
    
    # Find all PDF files
    pdf_files = list(input_path.glob("*.pdf"))
    
    if not pdf_files:
        logging.warning(f"No PDF files found in {input_dir}")
        return
    
    logging.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process each PDF file
    for pdf_file in pdf_files:
        try:
            start_time = time.time()
            logging.info(f"Processing: {pdf_file.name}")
            
            # Extract outline
            result = extractor.extract_outline(str(pdf_file))
            
            # Save JSON output with same filename but .json extension
            output_file = output_path / f"{pdf_file.stem}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4, ensure_ascii=False)
            
            processing_time = time.time() - start_time
            logging.info(f"Completed: {pdf_file.name} -> {output_file.name} ({processing_time:.2f}s)")
            
        except Exception as e:
            logging.error(f"Error processing {pdf_file.name}: {str(e)}")


def compare_results(pred_dir: str, gold_dir: str):
    """
    Compare predicted JSON files with ground truth.
    Computes precision, recall, and F1 score for heading detection.
    
    Args:
        pred_dir: Directory containing predicted JSON files
        gold_dir: Directory containing ground truth JSON files
    """
    pred_path = Path(pred_dir)
    gold_path = Path(gold_dir)
    
    pred_files = {f.stem: f for f in pred_path.glob("*.json")}
    gold_files = {f.stem: f for f in gold_path.glob("*.json")}
    
    common_files = set(pred_files.keys()) & set(gold_files.keys())
    
    if not common_files:
        logging.error("No matching files found between prediction and ground truth directories")
        return
    
    total_metrics = {'precision': 0, 'recall': 0, 'f1': 0}
    file_count = 0
    
    for filename in common_files:
        try:
            # Load predicted and ground truth data
            with open(pred_files[filename], 'r', encoding='utf-8') as f:
                pred_data = json.load(f)
            
            with open(gold_files[filename], 'r', encoding='utf-8') as f:
                gold_data = json.load(f)
            
            # Calculate metrics for this file
            metrics = calculate_metrics(pred_data, gold_data)
            
            logging.info(f"{filename}: P={metrics['precision']:.3f}, R={metrics['recall']:.3f}, F1={metrics['f1']:.3f}")
            
            total_metrics['precision'] += metrics['precision']
            total_metrics['recall'] += metrics['recall']
            total_metrics['f1'] += metrics['f1']
            file_count += 1
            
        except Exception as e:
            logging.error(f"Error comparing {filename}: {str(e)}")
    
    if file_count > 0:
        # Calculate average metrics
        avg_precision = total_metrics['precision'] / file_count
        avg_recall = total_metrics['recall'] / file_count
        avg_f1 = total_metrics['f1'] / file_count
        
        print(f"\n=== OVERALL RESULTS ===")
        print(f"Files compared: {file_count}")
        print(f"Average Precision: {avg_precision:.3f}")
        print(f"Average Recall: {avg_recall:.3f}")
        print(f"Average F1 Score: {avg_f1:.3f}")


def calculate_metrics(pred_data: Dict, gold_data: Dict) -> Dict[str, float]:
    """
    Calculate precision, recall, and F1 score for outline comparison.
    Compares exact matches of (level, text, page) tuples.
    """
    # Extract heading tuples (level, text, page)
    pred_headings = set()
    gold_headings = set()
    
    for heading in pred_data.get('outline', []):
        tuple_key = (heading['level'], heading['text'].strip(), heading['page'])
        pred_headings.add(tuple_key)
    
    for heading in gold_data.get('outline', []):
        tuple_key = (heading['level'], heading['text'].strip(), heading['page'])
        gold_headings.add(tuple_key)
    
    # Calculate metrics
    true_positives = len(pred_headings & gold_headings)
    false_positives = len(pred_headings - gold_headings)
    false_negatives = len(gold_headings - pred_headings)
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'true_positives': true_positives,
        'false_positives': false_positives,
        'false_negatives': false_negatives
    }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='PDF Outline Extractor - Adobe Hackathon Round 1A',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract outlines from PDFs
  python -m pdf_outline_extractor.cli_new extract --input-dir /app/input --output-dir /app/output
  
  # Compare results with ground truth
  python -m pdf_outline_extractor.cli_new compare --pred-dir /app/output --gold-dir /app/expected
  
  # Extract with custom parameters
  python -m pdf_outline_extractor.cli_new extract --input-dir /app/input --output-dir /app/output --min-h1-size-ratio 1.6 --verbose
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract outlines from PDF files')
    extract_parser.add_argument('--input-dir', required=True, help='Input directory containing PDF files')
    extract_parser.add_argument('--output-dir', required=True, help='Output directory for JSON files')
    extract_parser.add_argument('--min-h1-size-ratio', type=float, default=1.5, help='Minimum font size ratio for H1 headings')
    extract_parser.add_argument('--min-h2-size-ratio', type=float, default=1.3, help='Minimum font size ratio for H2 headings')
    extract_parser.add_argument('--min-h3-size-ratio', type=float, default=1.1, help='Minimum font size ratio for H3 headings')
    extract_parser.add_argument('--h2-indent-threshold', type=float, default=20.0, help='X-coordinate threshold for H2 detection')
    extract_parser.add_argument('--h3-indent-threshold', type=float, default=40.0, help='X-coordinate threshold for H3 detection')
    extract_parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare predicted results with ground truth')
    compare_parser.add_argument('--pred-dir', required=True, help='Directory containing predicted JSON files')
    compare_parser.add_argument('--gold-dir', required=True, help='Directory containing ground truth JSON files')
    compare_parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    # Legacy support for direct execution (Docker compatibility)
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] not in ['extract', 'compare']):
        # Default behavior for Docker: extract from /app/input to /app/output
        setup_logging(False)
        extract_outlines('/app/input', '/app/output')
        return
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    setup_logging(args.verbose)
    
    if args.command == 'extract':
        extract_outlines(
            args.input_dir,
            args.output_dir,
            min_h1_size_ratio=args.min_h1_size_ratio,
            min_h2_size_ratio=args.min_h2_size_ratio,
            min_h3_size_ratio=args.min_h3_size_ratio,
            h2_indent_threshold=args.h2_indent_threshold,
            h3_indent_threshold=args.h3_indent_threshold
        )
    
    elif args.command == 'compare':
        compare_results(args.pred_dir, args.gold_dir)


if __name__ == '__main__':
    main()
        if not input_dir.exists():
            logger.error(f"Input directory does not exist: {input_dir}")
            return 1
        
        pdf_files = list(input_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {input_dir}")
            return 0
        
        # Ensure output directory exists
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process each PDF file
        results = {}
        total_time = 0
        
        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}...")
            
            start_time = time.time()
            try:
                # Extract outline
                outline_data = extractor.extract_outline(str(pdf_file))
                
                # Write JSON output
                output_file = output_dir / f"{pdf_file.stem}.json"
                writer = OutlineWriter()
                success = writer.write_outline(outline_data, str(output_file))
                
                end_time = time.time()
                processing_time = end_time - start_time
                total_time += processing_time
                
                if success:
                    logger.info(f"Successfully processed {pdf_file.name} in {processing_time:.2f}s")
                    results[pdf_file.name] = {
                        "status": "success",
                        "output_file": str(output_file),
                        "processing_time": processing_time,
                        "headings_found": len(outline_data.get("outline", []))
                    }
                else:
                    logger.error(f"Failed to write output for {pdf_file.name}")
                    results[pdf_file.name] = {
                        "status": "write_error",
                        "processing_time": processing_time
                    }
                    
            except Exception as e:
                end_time = time.time()
                processing_time = end_time - start_time
                total_time += processing_time
                
                logger.error(f"Error processing {pdf_file.name}: {str(e)}")
                results[pdf_file.name] = {
                    "status": "error",
                    "error": str(e),
                    "processing_time": processing_time
                }
        
        # Summary
        successful = sum(1 for r in results.values() if r["status"] == "success")
        logger.info(f"Processing complete: {successful}/{len(pdf_files)} files successful")
        logger.info(f"Total processing time: {total_time:.2f}s")
        
        # Write processing summary
        summary_file = output_dir / "processing_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                "total_files": len(pdf_files),
                "successful": successful,
                "total_time": total_time,
                "results": results
            }, f, indent=2)
        
        return 0 if successful == len(pdf_files) else 1
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1


def compare_command(args) -> int:
    """
    Compare predicted outlines with ground truth.
    
    Args:
        args: Command line arguments
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        pred_dir = Path(args.pred_dir)
        gold_dir = Path(args.gold_dir)
        
        if not pred_dir.exists():
            logger.error(f"Prediction directory does not exist: {pred_dir}")
            return 1
        
        if not gold_dir.exists():
            logger.error(f"Gold directory does not exist: {gold_dir}")
            return 1
        
        # Find JSON files
        pred_files = {f.stem: f for f in pred_dir.glob("*.json")}
        gold_files = {f.stem: f for f in gold_dir.glob("*.json")}
        
        # Find common files
        common_files = set(pred_files.keys()) & set(gold_files.keys())
        
        if not common_files:
            logger.warning("No common files found for comparison")
            return 0
        
        # Compare files
        writer = OutlineWriter()
        total_metrics = {"precision": 0, "recall": 0, "f1": 0}
        comparison_results = {}
        
        for file_stem in sorted(common_files):
            pred_file = pred_files[file_stem]
            gold_file = gold_files[file_stem]
            
            logger.info(f"Comparing {file_stem}...")
            
            # Load data
            pred_data = writer.read_outline(str(pred_file))
            gold_data = writer.read_outline(str(gold_file))
            
            # Compare
            metrics = writer.compare_outlines(pred_data, gold_data)
            
            # Store results
            comparison_results[file_stem] = metrics
            
            # Update totals
            total_metrics["precision"] += metrics["precision"]
            total_metrics["recall"] += metrics["recall"]
            total_metrics["f1"] += metrics["f1"]
            
            # Log individual results
            logger.info(f"  {file_stem}: P={metrics['precision']:.3f} R={metrics['recall']:.3f} F1={metrics['f1']:.3f}")
        
        # Calculate averages
        num_files = len(common_files)
        avg_metrics = {
            "precision": total_metrics["precision"] / num_files,
            "recall": total_metrics["recall"] / num_files,
            "f1": total_metrics["f1"] / num_files
        }
        
        # Output summary
        logger.info("\n=== COMPARISON SUMMARY ===")
        logger.info(f"Files compared: {num_files}")
        logger.info(f"Average Precision: {avg_metrics['precision']:.3f}")
        logger.info(f"Average Recall: {avg_metrics['recall']:.3f}")
        logger.info(f"Average F1: {avg_metrics['f1']:.3f}")
        
        # Save detailed results
        if hasattr(args, 'output_file') and args.output_file:
            results_data = {
                "summary": avg_metrics,
                "files_compared": num_files,
                "detailed_results": comparison_results
            }
            
            with open(args.output_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2)
            
            logger.info(f"Detailed results saved to {args.output_file}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error during comparison: {str(e)}")
        return 1


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="PDF Outline Extractor - Extract structured outlines from PDF documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract outlines from PDFs
  pdf_outline_extractor --input-dir /app/input --output-dir /app/output
  
  # Compare predictions with ground truth
  pdf_outline_extractor cmp --pred /app/output --gold /app/expected
  
  # Extract with custom parameters
  pdf_outline_extractor --input-dir ./pdfs --output-dir ./output \\
    --min-h1-size-ratio 1.6 --h2-indent-threshold 30 --verbose
        """
    )
    
    # Global arguments
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command (default)
    extract_parser = subparsers.add_parser('extract', help='Extract outlines from PDFs (default)')
    extract_parser.add_argument('--input-dir', '-i', required=True,
                               help='Directory containing input PDF files')
    extract_parser.add_argument('--output-dir', '-o', required=True,
                               help='Directory for output JSON files')
    extract_parser.add_argument('--min-h1-size-ratio', type=float, default=1.5,
                               help='Minimum font size ratio for H1 detection (default: 1.5)')
    extract_parser.add_argument('--min-h2-size-ratio', type=float, default=1.3,
                               help='Minimum font size ratio for H2 detection (default: 1.3)')
    extract_parser.add_argument('--min-h3-size-ratio', type=float, default=1.1,
                               help='Minimum font size ratio for H3 detection (default: 1.1)')
    extract_parser.add_argument('--h2-indent-threshold', type=float, default=20.0,
                               help='X-coordinate threshold for H2 vs H3 distinction (default: 20.0)')
    
    # Compare command
    compare_parser = subparsers.add_parser('cmp', help='Compare predictions with ground truth')
    compare_parser.add_argument('--pred', '--pred-dir', dest='pred_dir', required=True,
                               help='Directory containing predicted JSON files')
    compare_parser.add_argument('--gold', '--gold-dir', dest='gold_dir', required=True,
                               help='Directory containing ground truth JSON files')
    compare_parser.add_argument('--output-file', '-o',
                               help='File to save detailed comparison results')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle default command (extract)
    if args.command is None:
        # Check if we have extract arguments
        if hasattr(args, 'input_dir') and hasattr(args, 'output_dir'):
            return extract_command(args)
        else:
            # Add extract arguments for backwards compatibility
            extract_parser.add_argument('--input-dir', '-i', required=True,
                                       help='Directory containing input PDF files')
            extract_parser.add_argument('--output-dir', '-o', required=True,
                                       help='Directory for output JSON files')
            # Re-parse for extract
            args = extract_parser.parse_args()
            return extract_command(args)
    
    # Handle subcommands
    if args.command == 'extract':
        return extract_command(args)
    elif args.command == 'cmp':
        return compare_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
