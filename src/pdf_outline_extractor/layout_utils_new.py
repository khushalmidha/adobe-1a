"""
Layout analysis utilities for PDF text processing.
Pure Python implementation without ML dependencies.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
import statistics


class LayoutAnalyzer:
    """
    Analyzes PDF layout to identify headings using font size ratios,
    positioning, and structural patterns.
    """
    
    def __init__(self):
        """Initialize the layout analyzer."""
        # Patterns for detecting numbered/bulleted content
        self.numbering_patterns = [
            r'^\s*\d+\.?\s*',                    # 1. or 1 
            r'^\s*[a-zA-Z]\.?\s*',              # a. or A.
            r'^\s*[ivxlcdm]+\.?\s*',            # Roman numerals
            r'^\s*[IVXLCDM]+\.?\s*',            # Capital Roman numerals
            r'^\s*[-•·]\s*',                     # Bullets
            r'^\s*\(\d+\)\s*',                  # (1)
            r'^\s*\([a-zA-Z]\)\s*',             # (a)
        ]
        
        # Compiled regex patterns for better performance
        self.compiled_patterns = [re.compile(pattern) for pattern in self.numbering_patterns]
    
    def has_numbering_or_bullets(self, text: str) -> bool:
        """
        Check if text starts with numbering or bullet patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            True if text has numbering/bullet patterns
        """
        if not text:
            return False
            
        # Check against all patterns
        for pattern in self.compiled_patterns:
            if pattern.match(text):
                return True
        
        return False
    
    def calculate_font_size_stats(self, spans: List[Dict]) -> Dict[str, float]:
        """
        Calculate font size statistics for a collection of spans.
        
        Args:
            spans: List of text spans with font size information
            
        Returns:
            Dictionary with font size statistics
        """
        if not spans:
            return {"mean": 12.0, "median": 12.0, "std": 0.0, "min": 12.0, "max": 12.0}
        
        font_sizes = [span["font_size"] for span in spans if span.get("font_size", 0) > 0]
        
        if not font_sizes:
            return {"mean": 12.0, "median": 12.0, "std": 0.0, "min": 12.0, "max": 12.0}
        
        mean_size = statistics.mean(font_sizes)
        median_size = statistics.median(font_sizes)
        min_size = min(font_sizes)
        max_size = max(font_sizes)
        
        # Calculate standard deviation
        if len(font_sizes) > 1:
            std_size = statistics.stdev(font_sizes)
        else:
            std_size = 0.0
        
        return {
            "mean": mean_size,
            "median": median_size,
            "std": std_size,
            "min": min_size,
            "max": max_size
        }
    
    def analyze_text_positioning(self, spans: List[Dict]) -> Dict[str, Any]:
        """
        Analyze text positioning patterns to identify structure.
        
        Args:
            spans: List of text spans with position information
            
        Returns:
            Dictionary with positioning analysis
        """
        if not spans:
            return {"left_margins": [], "common_indents": [], "line_heights": []}
        
        # Extract positioning data
        left_margins = [span["x"] for span in spans if "x" in span]
        line_heights = [span["height"] for span in spans if "height" in span]
        
        # Find common indentation levels
        common_indents = self._find_common_indents(left_margins)
        
        return {
            "left_margins": left_margins,
            "common_indents": common_indents,
            "line_heights": line_heights,
            "avg_line_height": statistics.median(line_heights) if line_heights else 0
        }
    
    def _find_common_indents(self, margins: List[float], tolerance: float = 5.0) -> List[float]:
        """
        Find common indentation levels in the document.
        
        Args:
            margins: List of left margin positions
            tolerance: Tolerance for grouping similar margins
            
        Returns:
            List of common indentation levels
        """
        if not margins:
            return []
        
        # Group similar margins
        indent_groups = []
        sorted_margins = sorted(set(margins))
        
        for margin in sorted_margins:
            # Check if this margin fits into an existing group
            placed = False
            for group in indent_groups:
                if abs(group[0] - margin) <= tolerance:
                    group.append(margin)
                    placed = True
                    break
            
            if not placed:
                indent_groups.append([margin])
        
        # Return representative values for each group
        common_indents = []
        for group in indent_groups:
            if len(group) >= 2:  # Only include if used multiple times
                common_indents.append(statistics.median(group))
        
        return sorted(common_indents)
    
    def is_likely_heading(self, span: Dict, page_avg_size: float, 
                         position_analysis: Dict) -> Tuple[bool, Optional[str]]:
        """
        Determine if a text span is likely to be a heading.
        
        Args:
            span: Text span to analyze
            page_avg_size: Average font size for the page
            position_analysis: Positioning analysis results
            
        Returns:
            Tuple of (is_heading, heading_level)
        """
        text = span.get("text", "").strip()
        font_size = span.get("font_size", 0)
        x_pos = span.get("x", 0)
        
        if not text or font_size <= 0:
            return False, None
        
        # Calculate size ratio
        size_ratio = font_size / page_avg_size if page_avg_size > 0 else 1.0
        
        # Check for heading patterns
        has_numbers = self.has_numbering_or_bullets(text)
        is_caps = text.isupper() and len(text) > 3
        is_title_case = text.istitle()
        
        # Font size based classification
        if size_ratio >= 1.5:
            return True, "H1"
        elif size_ratio >= 1.3:
            # Use positioning to distinguish H2 vs H3
            common_indents = position_analysis.get("common_indents", [])
            if common_indents and x_pos > min(common_indents) + 10:
                return True, "H3"
            else:
                return True, "H2"
        elif size_ratio >= 1.1:
            return True, "H3"
        
        # Pattern-based detection for smaller fonts
        if (has_numbers or is_caps or is_title_case) and size_ratio >= 1.05:
            if x_pos < 30:  # Left-aligned
                return True, "H2"
            else:
                return True, "H3"
        
        return False, None
    
    def detect_title_candidates(self, spans: List[Dict], page_width: float) -> List[Dict]:
        """
        Detect potential title candidates on the first page.
        
        Args:
            spans: Text spans from the first page
            page_width: Width of the page
            
        Returns:
            List of title candidates with scores
        """
        candidates = []
        
        for span in spans:
            text = span.get("text", "").strip()
            if len(text) < 5:  # Too short for a title
                continue
            
            # Calculate metrics
            font_size = span.get("font_size", 0)
            width = span.get("width", 0)
            x_pos = span.get("x", 0)
            y_pos = span.get("y", 0)
            
            # Width coverage
            width_coverage = width / page_width if page_width > 0 else 0
            
            # Position score (higher for top of page, centered)
            position_score = max(0, 1 - (y_pos / 200))  # Prefer top 200 pixels
            center_score = max(0, 1 - abs((x_pos + width/2) - page_width/2) / (page_width/2))
            
            # Calculate total score
            size_score = min(font_size / 20, 2.0)  # Normalize font size
            width_score = min(width_coverage * 2, 1.0)  # Prefer wider text
            
            total_score = size_score + width_score + position_score + center_score
            
            candidate = {
                "text": text,
                "score": total_score,
                "font_size": font_size,
                "width_coverage": width_coverage,
                "span": span
            }
            candidates.append(candidate)
        
        # Sort by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        return candidates[:5]  # Return top 5 candidates
    
    def clean_heading_text(self, text: str, preserve_structure: bool = True) -> str:
        """
        Clean heading text while optionally preserving structural elements.
        
        Args:
            text: Raw heading text
            preserve_structure: Whether to preserve numbering/bullets
            
        Returns:
            Cleaned heading text
        """
        if not text:
            return ""
        
        # Normalize whitespace but preserve intentional formatting
        cleaned = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
        cleaned = cleaned.strip()
        
        if not preserve_structure:
            # Remove numbering/bullets if requested
            for pattern in self.numbering_patterns:
                cleaned = re.sub(pattern, '', cleaned)
            cleaned = cleaned.strip()
        
        return cleaned
    
    def validate_heading_sequence(self, headings: List[Dict]) -> List[Dict]:
        """
        Validate and potentially correct heading level sequence.
        
        Args:
            headings: List of heading dictionaries
            
        Returns:
            Validated heading list
        """
        if not headings:
            return []
        
        validated = []
        last_level = None
        
        for heading in headings:
            level = heading["level"]
            text = heading["text"]
            
            # Skip if text is too short or repetitive
            if len(text.strip()) < 3:
                continue
            
            # Check for logical level progression
            if last_level is None:
                # First heading can be any level
                validated.append(heading)
                last_level = level
            else:
                # Ensure reasonable progression
                level_map = {"H1": 1, "H2": 2, "H3": 3}
                current_num = level_map.get(level, 3)
                last_num = level_map.get(last_level, 1)
                
                # Allow same level or reasonable jump
                if current_num <= last_num + 1:
                    validated.append(heading)
                    last_level = level
                else:
                    # Demote to reasonable level
                    corrected_level = f"H{min(last_num + 1, 3)}"
                    heading_copy = heading.copy()
                    heading_copy["level"] = corrected_level
                    validated.append(heading_copy)
                    last_level = corrected_level
        
        return validated
