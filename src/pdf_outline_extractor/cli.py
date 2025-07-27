"""Command-line interface for PDF outline extraction.

This module provides CLI commands for extracting PDF outlines and comparing results.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from .extractor import PDFOutlineExtractor
from .json_writer import JSONWriter


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration.
    
    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(verbose: bool) -> None:
    """PDF Outline Extractor - Extract structured outlines from PDF documents."""
    setup_logging(verbose)


@main.command()
@click.option(
    '--input-dir', 
    required=True, 
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Directory containing input PDF files'
)
@click.option(
    '--output-dir', 
    required=True, 
    type=click.Path(file_okay=False, dir_okay=True),
    help='Directory for output JSON files'
)
@click.option(
    '--min-h1-size-ratio', 
    default=1.5, 
    type=float,
    help='Minimum font size ratio for H1 detection (default: 1.5)'
)
@click.option(
    '--min-h2-size-ratio',
    default=1.3,
    type=float, 
    help='Minimum font size ratio for H2 detection (default: 1.3)'
)
@click.option(
    '--min-h3-size-ratio',
    default=1.1,
    type=float,
    help='Minimum font size ratio for H3 detection (default: 1.1)'
)
@click.option(
    '--h2-indent-threshold',
    default=50.0,
    type=float,
    help='X-coordinate threshold for H2/H3 distinction (default: 50)'
)
@click.option(
    '--title-width-threshold',
    default=0.8,
    type=float,
    help='Minimum line width ratio for title detection (default: 0.8)'
)
@click.option(
    '--lang-model-path',
    type=click.Path(exists=True),
    help='Path to language detection model (optional)'
)
@click.option(
    '--file-pattern',
    default='*.pdf',
    help='Glob pattern for PDF files (default: *.pdf)'
)
@click.option(
    '--no-language-detection',
    is_flag=True,
    help='Disable language detection for faster processing'
)
def extract(
    input_dir: str,
    output_dir: str,
    min_h1_size_ratio: float,
    min_h2_size_ratio: float,
    min_h3_size_ratio: float,
    h2_indent_threshold: float,
    title_width_threshold: float,
    lang_model_path: Optional[str],
    file_pattern: str,
    no_language_detection: bool
) -> None:
    """Extract outlines from PDF files."""
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize extractor with custom parameters
        extractor = PDFOutlineExtractor(
            min_h1_size_ratio=min_h1_size_ratio,
            min_h2_size_ratio=min_h2_size_ratio,
            min_h3_size_ratio=min_h3_size_ratio,
            h2_indent_threshold=h2_indent_threshold,
            title_width_threshold=title_width_threshold,
            language_detection=not no_language_detection
        )
        
        logger.info(f"Extracting outlines from {input_dir}")
        logger.info(f"Output directory: {output_dir}")
        logger.info(f"File pattern: {file_pattern}")
        
        # Extract and save outlines
        written_files = extractor.batch_extract_and_save(
            input_dir=input_dir,
            output_dir=output_dir,
            file_pattern=file_pattern
        )
        
        if written_files:
            logger.info(f"Successfully processed {len(written_files)} files:")
            for file_path in written_files:
                logger.info(f"  - {file_path}")
        else:
            logger.warning("No files were processed successfully")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        sys.exit(1)


@main.command()
@click.option(
    '--pred',
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Directory with predicted JSON files'
)
@click.option(
    '--gold',
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help='Directory with ground truth JSON files'
)
@click.option(
    '--output-report',
    type=click.Path(file_okay=True, dir_okay=False),
    help='Path to save comparison report (optional)'
)
@click.option(
    '--detailed',
    is_flag=True,
    help='Show detailed per-file results'
)
def cmp(
    pred: str,
    gold: str,
    output_report: Optional[str],
    detailed: bool
) -> None:
    """Compare predicted outlines with ground truth."""
    logger = logging.getLogger(__name__)
    
    try:
        pred_path = Path(pred)
        gold_path = Path(gold)
        
        logger.info(f"Comparing predictions in {pred_path}")
        logger.info(f"Against ground truth in {gold_path}")
        
        # Initialize JSON writer for comparison
        json_writer = JSONWriter(pred_path)
        
        # Perform comparison
        results = json_writer.compare_outlines(pred_path, gold_path)
        
        if not results:
            logger.warning("No matching files found for comparison")
            sys.exit(1)
        
        # Generate report
        report = json_writer.generate_comparison_report(results)
        
        # Print report
        click.echo(report)
        
        # Save report if requested
        if output_report:
            with open(output_report, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to {output_report}")
        
        # Show detailed results if requested
        if detailed:
            click.echo("\nDetailed Results:")
            click.echo("=" * 50)
            for filename, metrics in results.items():
                click.echo(f"\n{filename}:")
                click.echo(f"  True Positives:  {metrics['true_positives']}")
                click.echo(f"  False Positives: {metrics['false_positives']}")
                click.echo(f"  False Negatives: {metrics['false_negatives']}")
                click.echo(f"  Precision:       {metrics['precision']:.4f}")
                click.echo(f"  Recall:          {metrics['recall']:.4f}")
                click.echo(f"  F1 Score:        {metrics['f1']:.4f}")
        
        # Calculate overall metrics for exit code
        all_f1_scores = [r['f1'] for r in results.values()]
        avg_f1 = sum(all_f1_scores) / len(all_f1_scores) if all_f1_scores else 0.0
        
        logger.info(f"Average F1 Score: {avg_f1:.4f}")
        
        # Exit with appropriate code
        if avg_f1 < 0.5:
            logger.warning("Low performance detected (F1 < 0.5)")
            sys.exit(2)
        elif avg_f1 < 0.8:
            logger.info("Moderate performance (F1 < 0.8)")
            sys.exit(0)
        else:
            logger.info("Good performance (F1 >= 0.8)")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        sys.exit(1)


@main.command()
@click.argument('pdf_file', type=click.Path(exists=True, dir_okay=False))
@click.option(
    '--output',
    type=click.Path(dir_okay=False),
    help='Output JSON file path (optional)'
)
@click.option(
    '--pretty',
    is_flag=True,
    help='Pretty print JSON output'
)
def single(pdf_file: str, output: Optional[str], pretty: bool) -> None:
    """Extract outline from a single PDF file."""
    logger = logging.getLogger(__name__)
    
    try:
        pdf_path = Path(pdf_file)
        logger.info(f"Processing single file: {pdf_path}")
        
        # Initialize extractor
        extractor = PDFOutlineExtractor()
        
        # Extract outline
        outline_data = extractor.extract_outline(pdf_path)
        
        if output:
            # Save to specified file
            output_path = Path(output)
            json_writer = JSONWriter(
                output_dir=output_path.parent,
                indent=4 if pretty else 2
            )
            
            written_file = json_writer.write_outline_json(
                filename=output_path.name,
                title=outline_data['title'],
                outline_entries=outline_data['outline'],
                metadata=outline_data.get('metadata')
            )
            
            logger.info(f"Outline saved to {written_file}")
        else:
            # Print to stdout
            import json
            json_str = json.dumps(
                {
                    'title': outline_data['title'],
                    'outline': outline_data['outline']
                },
                ensure_ascii=False,
                indent=4 if pretty else 2
            )
            click.echo(json_str)
            
    except Exception as e:
        logger.error(f"Failed to process {pdf_file}: {e}")
        sys.exit(1)


@main.command()
def version() -> None:
    """Show version information."""
    from . import __version__
    click.echo(f"PDF Outline Extractor v{__version__}")


# Legacy argparse-based interface for backward compatibility
def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for legacy CLI interface.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='Extract structured outlines from PDF documents'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract outlines from PDFs')
    extract_parser.add_argument(
        '--input-dir', 
        required=True,
        help='Directory containing input PDF files'
    )
    extract_parser.add_argument(
        '--output-dir',
        required=True,
        help='Directory for output JSON files'
    )
    extract_parser.add_argument(
        '--min-h1-size-ratio',
        type=float,
        default=1.5,
        help='Minimum font size ratio for H1 detection'
    )
    extract_parser.add_argument(
        '--h2-indent-threshold',
        type=float,
        default=50.0,
        help='X-coordinate threshold for H2/H3 distinction'
    )
    extract_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    # Compare command
    cmp_parser = subparsers.add_parser('cmp', help='Compare predicted vs ground truth')
    cmp_parser.add_argument(
        '--pred',
        required=True,
        help='Directory with predicted JSON files'
    )
    cmp_parser.add_argument(
        '--gold',
        required=True,
        help='Directory with ground truth JSON files'
    )
    cmp_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    return parser


def legacy_main() -> None:
    """Legacy main function for argparse interface."""
    parser = create_parser()
    args = parser.parse_args()
    
    setup_logging(getattr(args, 'verbose', False))
    
    if args.command == 'extract':
        # Convert to click context
        from click.testing import CliRunner
        runner = CliRunner()
        
        cmd_args = [
            'extract',
            '--input-dir', args.input_dir,
            '--output-dir', args.output_dir,
            '--min-h1-size-ratio', str(args.min_h1_size_ratio),
            '--h2-indent-threshold', str(args.h2_indent_threshold)
        ]
        
        if args.verbose:
            cmd_args.insert(1, '--verbose')
        
        result = runner.invoke(main, cmd_args)
        sys.exit(result.exit_code)
        
    elif args.command == 'cmp':
        from click.testing import CliRunner
        runner = CliRunner()
        
        cmd_args = [
            'cmp',
            '--pred', args.pred,
            '--gold', args.gold
        ]
        
        if args.verbose:
            cmd_args.insert(1, '--verbose')
        
        result = runner.invoke(main, cmd_args)
        sys.exit(result.exit_code)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
