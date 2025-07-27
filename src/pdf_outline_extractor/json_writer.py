"""JSON writer module for outputting structured PDF outlines.

This module handles the creation and writing of JSON files containing
extracted PDF outline data in the specified format.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging


class JSONWriter:
    """Handles JSON output formatting and file operations."""
    
    def __init__(self, output_dir: str, ensure_ascii: bool = False, indent: int = 2):
        """Initialize JSON writer.
        
        Args:
            output_dir: Directory for output JSON files
            ensure_ascii: Whether to escape non-ASCII characters
            indent: JSON indentation level
        """
        self.output_dir = Path(output_dir)
        self.ensure_ascii = ensure_ascii
        self.indent = indent
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_outline_json(
        self, 
        title: Optional[str], 
        outline_entries: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create JSON structure for PDF outline.
        
        Args:
            title: Document title
            outline_entries: List of heading entries
            metadata: Optional metadata to include
            
        Returns:
            JSON-serializable dictionary
        """
        # Ensure title is a string
        if title is None:
            title = ""
        
        # Sort outline entries by page number, then by order of appearance
        sorted_entries = sorted(
            outline_entries, 
            key=lambda x: (x.get('page', 0), x.get('order', 0))
        )
        
        # Clean and validate entries
        cleaned_entries = []
        for entry in sorted_entries:
            cleaned_entry = {
                'level': entry.get('level', 'H1'),
                'text': str(entry.get('text', '')).strip(),
                'page': int(entry.get('page', 0))  # Ensure 0-based indexing
            }
            
            # Only include non-empty text entries
            if cleaned_entry['text']:
                cleaned_entries.append(cleaned_entry)
        
        json_data = {
            'title': title,
            'outline': cleaned_entries
        }
        
        # Add metadata if provided
        if metadata:
            json_data['metadata'] = metadata
            
        return json_data

    def write_outline_json(
        self, 
        filename: str, 
        title: Optional[str],
        outline_entries: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Write outline JSON to file.
        
        Args:
            filename: Output filename (without extension)
            title: Document title
            outline_entries: List of heading entries
            metadata: Optional metadata
            
        Returns:
            Path to written file
        """
        # Ensure filename has .json extension
        if not filename.endswith('.json'):
            filename = f"{filename}.json"
        
        output_path = self.output_dir / filename
        
        # Create JSON data
        json_data = self.create_outline_json(title, outline_entries, metadata)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(
                    json_data, 
                    f, 
                    ensure_ascii=self.ensure_ascii,
                    indent=self.indent,
                    sort_keys=False  # Preserve order
                )
            
            self.logger.info(f"Successfully wrote outline to {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to write JSON file {output_path}: {e}")
            raise

    def write_multiple_outlines(
        self, 
        outlines: Dict[str, Dict[str, Any]]
    ) -> List[Path]:
        """Write multiple outline JSON files.
        
        Args:
            outlines: Dictionary mapping filenames to outline data
            
        Returns:
            List of paths to written files
        """
        written_files = []
        
        for pdf_filename, outline_data in outlines.items():
            # Extract base filename without extension
            base_name = Path(pdf_filename).stem
            
            try:
                output_path = self.write_outline_json(
                    filename=base_name,
                    title=outline_data.get('title'),
                    outline_entries=outline_data.get('outline', []),
                    metadata=outline_data.get('metadata')
                )
                written_files.append(output_path)
                
            except Exception as e:
                self.logger.error(f"Failed to write outline for {pdf_filename}: {e}")
                continue
        
        return written_files

    def validate_json_format(self, json_data: Dict[str, Any]) -> bool:
        """Validate JSON data against expected outline format.
        
        Args:
            json_data: JSON data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required top-level keys
            if 'title' not in json_data or 'outline' not in json_data:
                return False
            
            # Check title is string
            if not isinstance(json_data['title'], str):
                return False
            
            # Check outline is list
            if not isinstance(json_data['outline'], list):
                return False
            
            # Validate each outline entry
            for entry in json_data['outline']:
                if not isinstance(entry, dict):
                    return False
                
                # Check required fields
                required_fields = ['level', 'text', 'page']
                for field in required_fields:
                    if field not in entry:
                        return False
                
                # Check field types
                if not isinstance(entry['level'], str):
                    return False
                if not isinstance(entry['text'], str):
                    return False
                if not isinstance(entry['page'], int):
                    return False
                
                # Check valid level values
                if entry['level'] not in ['H1', 'H2', 'H3']:
                    return False
                
                # Check page number is non-negative
                if entry['page'] < 0:
                    return False
            
            return True
            
        except Exception:
            return False

    def read_json_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """Read and validate JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            JSON data or None if invalid
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if self.validate_json_format(data):
                return data
            else:
                self.logger.warning(f"Invalid JSON format in {filepath}")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to read JSON file {filepath}: {e}")
            return None

    def compare_outlines(
        self, 
        predicted_dir: Path, 
        gold_dir: Path
    ) -> Dict[str, Dict[str, float]]:
        """Compare predicted outlines with ground truth.
        
        Args:
            predicted_dir: Directory with predicted JSON files
            gold_dir: Directory with ground truth JSON files
            
        Returns:
            Dictionary with comparison metrics per file
        """
        results = {}
        
        # Find matching files
        predicted_files = {f.stem: f for f in predicted_dir.glob('*.json')}
        gold_files = {f.stem: f for f in gold_dir.glob('*.json')}
        
        common_files = set(predicted_files.keys()) & set(gold_files.keys())
        
        for filename in common_files:
            pred_data = self.read_json_file(predicted_files[filename])
            gold_data = self.read_json_file(gold_files[filename])
            
            if pred_data is None or gold_data is None:
                self.logger.warning(f"Skipping {filename} due to invalid JSON")
                continue
            
            metrics = self._calculate_metrics(
                pred_data['outline'], 
                gold_data['outline']
            )
            results[filename] = metrics
        
        return results

    def _calculate_metrics(
        self, 
        predicted: List[Dict[str, Any]], 
        gold: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate precision, recall, and F1 for outline comparison.
        
        Args:
            predicted: Predicted outline entries
            gold: Ground truth outline entries
            
        Returns:
            Dictionary with precision, recall, and F1 scores
        """
        # Create sets of tuples for exact matching
        pred_set = set()
        for entry in predicted:
            pred_set.add((
                entry['level'], 
                entry['text'].strip(), 
                entry['page']
            ))
        
        gold_set = set()
        for entry in gold:
            gold_set.add((
                entry['level'], 
                entry['text'].strip(), 
                entry['page']
            ))
        
        # Calculate metrics
        true_positives = len(pred_set & gold_set)
        false_positives = len(pred_set - gold_set)
        false_negatives = len(gold_set - pred_set)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'true_positives': true_positives,
            'false_positives': false_positives,
            'false_negatives': false_negatives
        }

    def generate_comparison_report(
        self, 
        comparison_results: Dict[str, Dict[str, float]]
    ) -> str:
        """Generate a human-readable comparison report.
        
        Args:
            comparison_results: Results from compare_outlines
            
        Returns:
            Formatted report string
        """
        if not comparison_results:
            return "No comparison results available.\n"
        
        # Calculate overall metrics
        total_tp = sum(r['true_positives'] for r in comparison_results.values())
        total_fp = sum(r['false_positives'] for r in comparison_results.values())
        total_fn = sum(r['false_negatives'] for r in comparison_results.values())
        
        overall_precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
        overall_recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
        overall_f1 = 2 * overall_precision * overall_recall / (overall_precision + overall_recall) if (overall_precision + overall_recall) > 0 else 0.0
        
        # Generate report
        report = ["PDF Outline Extraction Comparison Report"]
        report.append("=" * 50)
        report.append("")
        
        # Overall metrics
        report.append("Overall Metrics:")
        report.append(f"  Precision: {overall_precision:.3f}")
        report.append(f"  Recall:    {overall_recall:.3f}")
        report.append(f"  F1 Score:  {overall_f1:.3f}")
        report.append("")
        
        # Per-file metrics
        report.append("Per-File Results:")
        report.append("-" * 30)
        
        for filename, metrics in sorted(comparison_results.items()):
            report.append(f"{filename}:")
            report.append(f"  Precision: {metrics['precision']:.3f}")
            report.append(f"  Recall:    {metrics['recall']:.3f}")
            report.append(f"  F1 Score:  {metrics['f1']:.3f}")
            report.append(f"  TP/FP/FN:  {metrics['true_positives']}/{metrics['false_positives']}/{metrics['false_negatives']}")
            report.append("")
        
        return "\n".join(report)
