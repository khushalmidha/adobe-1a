"""Layout analysis utilities for PDF text processing.

This module provides functions for analyzing text layout, font sizes,
indentation, and detecting structural elements like bullets and numbering.
"""

import re
import statistics
from typing import Dict, List, Tuple, Optional, Any
import numpy as np


class LayoutAnalyzer:
    """Analyzes PDF layout to identify heading hierarchy and structure."""
    
    def __init__(
        self,
        min_h1_size_ratio: float = 1.5,
        min_h2_size_ratio: float = 1.3,
        min_h3_size_ratio: float = 1.1,
        h2_indent_threshold: float = 50.0,
        title_width_threshold: float = 0.8
    ):
        """Initialize layout analyzer with configurable thresholds.
        
        Args:
            min_h1_size_ratio: Minimum font size ratio for H1 detection
            min_h2_size_ratio: Minimum font size ratio for H2 detection  
            min_h3_size_ratio: Minimum font size ratio for H3 detection
            h2_indent_threshold: X-coordinate threshold for H2/H3 distinction
            title_width_threshold: Minimum line width ratio for title detection
        """
        self.min_h1_size_ratio = min_h1_size_ratio
        self.min_h2_size_ratio = min_h2_size_ratio
        self.min_h3_size_ratio = min_h3_size_ratio
        self.h2_indent_threshold = h2_indent_threshold
        self.title_width_threshold = title_width_threshold
        
        # Regex patterns for detecting structural elements
        self.numbering_pattern = re.compile(
            r'^\s*(?:'
            r'\d+\.?\s+'  # 1. or 1 
            r'|\d+\.\d+\.?\s+'  # 1.1. or 1.1
            r'|\d+\.\d+\.\d+\.?\s+'  # 1.1.1. or 1.1.1
            r'|[a-zA-Z]\.?\s+'  # a. or A.
            r'|[ivxlcdm]+\.?\s+'  # roman numerals
            r'|[IVXLCDM]+\.?\s+'  # roman numerals uppercase
            r')',
            re.IGNORECASE
        )
        
        self.bullet_pattern = re.compile(
            r'^\s*(?:'
            r'[-•‣⁃▪▫◦‰‱]'  # various bullet characters
            r'|\*'  # asterisk
            r'|\+'  # plus
            r'|»'  # right-pointing double angle
            r')\s+',
            re.UNICODE
        )

    def calculate_font_size_ratios(self, spans: List[Dict[str, Any]], page_width: float) -> List[Dict[str, Any]]:
        """Calculate font size ratios for text spans on a page.
        
        Args:
            spans: List of text spans with font size information
            page_width: Width of the page for layout analysis
            
        Returns:
            List of spans enhanced with size ratios and layout metrics
        """
        if not spans:
            return []
        
        # Extract font sizes and calculate statistics
        font_sizes = [span.get('size', 12.0) for span in spans if span.get('size', 0) > 0]
        if not font_sizes:
            return spans
            
        avg_font_size = statistics.mean(font_sizes)
        median_font_size = statistics.median(font_sizes)
        
        # Use median for more robust baseline
        baseline_size = median_font_size if len(font_sizes) > 3 else avg_font_size
        
        enhanced_spans = []
        for span in spans:
            enhanced_span = span.copy()
            font_size = span.get('size', baseline_size)
            
            # Calculate size ratio
            size_ratio = font_size / baseline_size if baseline_size > 0 else 1.0
            enhanced_span['size_ratio'] = size_ratio
            
            # Calculate line width ratio
            text_width = span.get('width', 0)
            width_ratio = text_width / page_width if page_width > 0 else 0
            enhanced_span['width_ratio'] = width_ratio
            
            # Analyze indentation
            x_pos = span.get('x', 0)
            enhanced_span['indent_level'] = self._calculate_indent_level(x_pos)
            
            enhanced_spans.append(enhanced_span)
            
        return enhanced_spans

    def _calculate_indent_level(self, x_position: float) -> int:
        """Calculate indentation level based on x-position.
        
        Args:
            x_position: X-coordinate of text span
            
        Returns:
            Indentation level (0 = no indent, 1+ = indented)
        """
        # Define indentation thresholds
        if x_position < 50:
            return 0  # No indentation
        elif x_position < 100:
            return 1  # First level indent
        elif x_position < 150:
            return 2  # Second level indent
        else:
            return 3  # Deep indentation

    def classify_heading_level(self, span: Dict[str, Any], context_spans: List[Dict[str, Any]]) -> Optional[str]:
        """Classify a text span's heading level based on size ratio and layout.
        
        Args:
            span: Text span to classify
            context_spans: Other spans on the same page for context
            
        Returns:
            Heading level ('H1', 'H2', 'H3') or None if not a heading
        """
        size_ratio = span.get('size_ratio', 1.0)
        indent_level = span.get('indent_level', 0)
        text = span.get('text', '').strip()
        
        # Skip empty or very short text
        if len(text) < 2:
            return None
            
        # Check for structural markers
        has_numbering = bool(self.numbering_pattern.match(text))
        has_bullet = bool(self.bullet_pattern.match(text))
        
        # Primary classification by font size ratio
        if size_ratio >= self.min_h1_size_ratio:
            # H1 candidate - check for further refinement
            if indent_level == 0 or has_numbering:
                return 'H1'
            elif indent_level == 1:
                return 'H2'  # Indented large text might be H2
            else:
                return 'H3'  # Deeply indented large text
                
        elif size_ratio >= self.min_h2_size_ratio:
            # H2 candidate - refine by indentation and structure
            if indent_level <= 1 and (has_numbering or not has_bullet):
                return 'H2'
            else:
                return 'H3'  # Indented or bullet points are likely H3
                
        elif size_ratio >= self.min_h3_size_ratio:
            # H3 candidate - check structure
            if has_numbering or (indent_level <= 2 and len(text) > 10):
                return 'H3'
                
        return None

    def detect_title(self, spans: List[Dict[str, Any]], page_num: int = 0) -> Optional[str]:
        """Detect the document title from the first page.
        
        Args:
            spans: Text spans from the page
            page_num: Page number (0-indexed)
            
        Returns:
            Title text or None if no clear title found
        """
        # Only look for title on first page
        if page_num != 0:
            return None
            
        if not spans:
            return None
            
        # Find spans that could be titles
        title_candidates = []
        
        for span in spans:
            text = span.get('text', '').strip()
            size_ratio = span.get('size_ratio', 1.0)
            width_ratio = span.get('width_ratio', 0.0)
            y_pos = span.get('y', 0)
            
            # Title criteria:
            # 1. Large font size
            # 2. Wide text span
            # 3. Near top of page
            # 4. Reasonable length
            if (size_ratio >= self.min_h1_size_ratio and
                width_ratio >= self.title_width_threshold and
                y_pos < 200 and  # Upper portion of page
                len(text) > 5 and len(text) < 200):
                
                title_candidates.append((text, size_ratio, y_pos))
        
        if not title_candidates:
            # Fallback: look for the largest text on the page
            largest_spans = sorted(spans, key=lambda x: x.get('size_ratio', 0), reverse=True)
            for span in largest_spans[:3]:  # Check top 3 largest
                text = span.get('text', '').strip()
                if len(text) > 5 and len(text) < 200:
                    return text
            return None
        
        # Sort by size ratio and position, prefer larger and higher text
        title_candidates.sort(key=lambda x: (x[1], -x[2]), reverse=True)
        return title_candidates[0][0]

    def detect_structural_patterns(self, text: str) -> Dict[str, bool]:
        """Detect structural patterns in text (numbering, bullets, etc.).
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with pattern detection results
        """
        return {
            'has_numbering': bool(self.numbering_pattern.match(text)),
            'has_bullet': bool(self.bullet_pattern.match(text)),
            'is_all_caps': text.isupper() and len(text) > 3,
            'has_special_chars': bool(re.search(r'[^\w\s.-]', text, re.UNICODE)),
        }

    def analyze_text_flow(self, spans: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze text flow and layout patterns on a page.
        
        Args:
            spans: Text spans to analyze
            
        Returns:
            Dictionary with flow analysis results
        """
        if not spans:
            return {'reading_order': [], 'columns': 1, 'text_density': 0.0}
        
        # Sort spans by reading order (top to bottom, left to right)
        sorted_spans = sorted(spans, key=lambda x: (x.get('y', 0), x.get('x', 0)))
        
        # Analyze column layout
        x_positions = [span.get('x', 0) for span in spans]
        y_positions = [span.get('y', 0) for span in spans]
        
        # Simple column detection based on x-position clustering
        unique_x = sorted(set(x_positions))
        column_threshold = 100  # Minimum distance between columns
        
        columns = 1
        if len(unique_x) > 1:
            for i in range(1, len(unique_x)):
                if unique_x[i] - unique_x[i-1] > column_threshold:
                    columns += 1
        
        # Calculate text density
        page_area = 1.0  # Normalized
        text_area = sum(span.get('width', 0) * span.get('height', 12) for span in spans)
        text_density = min(text_area / (page_area * 1000), 1.0)  # Normalize
        
        return {
            'reading_order': [span.get('text', '') for span in sorted_spans],
            'columns': columns,
            'text_density': text_density,
            'x_range': (min(x_positions) if x_positions else 0, max(x_positions) if x_positions else 0),
            'y_range': (min(y_positions) if y_positions else 0, max(y_positions) if y_positions else 0),
        }
