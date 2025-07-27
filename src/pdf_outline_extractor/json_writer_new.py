"""
JSON output writer for PDF outline extraction.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List
import logging


class OutlineWriter:
    """
    Handles writing PDF outline data to JSON files.
    """
    
    def __init__(self):
        """Initialize the JSON writer."""
        self.logger = logging.getLogger(__name__)
    
    def write_outline(self, outline_data: Dict[str, Any], output_path: str) -> bool:
        """
        Write outline data to a JSON file.
        
        Args:
            outline_data: Dictionary containing title and outline
            output_path: Path to output JSON file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Format the data according to spec
            formatted_data = self._format_outline_data(outline_data)
            
            # Write to file with proper formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Successfully wrote outline to {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write outline to {output_path}: {str(e)}")
            return False
    
    def _format_outline_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format outline data according to hackathon specification.
        
        Args:
            data: Raw outline data
            
        Returns:
            Formatted data dictionary
        """
        # Ensure we have the required structure
        formatted = {
            "title": data.get("title", ""),
            "outline": []
        }
        
        # Process outline entries
        outline_entries = data.get("outline", [])
        for entry in outline_entries:
            formatted_entry = {
                "level": entry.get("level", "H1"),
                "text": entry.get("text", ""),
                "page": entry.get("page", 0)  # 0-based indexing as per spec
            }
            formatted["outline"].append(formatted_entry)
        
        return formatted
    
    def write_multiple_outlines(self, outlines: Dict[str, Dict[str, Any]], 
                              output_dir: str) -> Dict[str, bool]:
        """
        Write multiple outline files to a directory.
        
        Args:
            outlines: Dictionary mapping PDF names to outline data
            output_dir: Output directory path
            
        Returns:
            Dictionary mapping filenames to success status
        """
        results = {}
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        for pdf_name, outline_data in outlines.items():
            # Generate output filename
            base_name = Path(pdf_name).stem
            output_filename = f"{base_name}.json"
            output_path = os.path.join(output_dir, output_filename)
            
            # Write the outline
            success = self.write_outline(outline_data, output_path)
            results[output_filename] = success
        
        return results
    
    def validate_outline_format(self, data: Dict[str, Any]) -> List[str]:
        """
        Validate outline data format against specification.
        
        Args:
            data: Outline data to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check required fields
        if "title" not in data:
            errors.append("Missing 'title' field")
        elif not isinstance(data["title"], str):
            errors.append("'title' field must be a string")
        
        if "outline" not in data:
            errors.append("Missing 'outline' field")
        elif not isinstance(data["outline"], list):
            errors.append("'outline' field must be a list")
        else:
            # Validate outline entries
            for i, entry in enumerate(data["outline"]):
                if not isinstance(entry, dict):
                    errors.append(f"Outline entry {i} must be a dictionary")
                    continue
                
                # Check required entry fields
                if "level" not in entry:
                    errors.append(f"Outline entry {i} missing 'level' field")
                elif entry["level"] not in ["H1", "H2", "H3"]:
                    errors.append(f"Outline entry {i} has invalid level: {entry['level']}")
                
                if "text" not in entry:
                    errors.append(f"Outline entry {i} missing 'text' field")
                elif not isinstance(entry["text"], str):
                    errors.append(f"Outline entry {i} 'text' field must be a string")
                
                if "page" not in entry:
                    errors.append(f"Outline entry {i} missing 'page' field")
                elif not isinstance(entry["page"], int) or entry["page"] < 0:
                    errors.append(f"Outline entry {i} 'page' field must be a non-negative integer")
        
        return errors
    
    def read_outline(self, json_path: str) -> Dict[str, Any]:
        """
        Read outline data from a JSON file.
        
        Args:
            json_path: Path to JSON file
            
        Returns:
            Outline data dictionary
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate format
            errors = self.validate_outline_format(data)
            if errors:
                self.logger.warning(f"Format validation errors in {json_path}: {errors}")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to read outline from {json_path}: {str(e)}")
            return {"title": "", "outline": []}
    
    def compare_outlines(self, pred_data: Dict[str, Any], 
                        gold_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Compare predicted outline with ground truth.
        
        Args:
            pred_data: Predicted outline data
            gold_data: Ground truth outline data
            
        Returns:
            Dictionary with precision, recall, F1 scores
        """
        pred_entries = pred_data.get("outline", [])
        gold_entries = gold_data.get("outline", [])
        
        # Convert to tuples for comparison (level, text, page)
        pred_tuples = {
            (entry["level"], entry["text"].strip().lower(), entry["page"])
            for entry in pred_entries
        }
        
        gold_tuples = {
            (entry["level"], entry["text"].strip().lower(), entry["page"])
            for entry in gold_entries
        }
        
        # Calculate metrics
        if len(pred_tuples) == 0 and len(gold_tuples) == 0:
            precision = recall = f1 = 1.0
        elif len(pred_tuples) == 0:
            precision = recall = f1 = 0.0
        elif len(gold_tuples) == 0:
            precision = recall = f1 = 0.0
        else:
            true_positives = len(pred_tuples & gold_tuples)
            precision = true_positives / len(pred_tuples)
            recall = true_positives / len(gold_tuples)
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "true_positives": len(pred_tuples & gold_tuples) if pred_tuples and gold_tuples else 0,
            "predicted_count": len(pred_tuples),
            "gold_count": len(gold_tuples)
        }
