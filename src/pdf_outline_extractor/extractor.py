"""PDF outline extraction engine.

This module contains the core logic for parsing PDF documents and extracting
structured outlines using PyMuPDF with advanced text analysis.
"""

import os
import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
import statistics

from .layout_utils import LayoutAnalyzer
from .i18n_utils import TextNormalizer
from .json_writer import JSONWriter


class PDFOutlineExtractor:
    """Main class for extracting structured outlines from PDF documents."""
    
    def __init__(
        self,
        min_h1_size_ratio: float = 1.5,
        min_h2_size_ratio: float = 1.3,
        min_h3_size_ratio: float = 1.1,
        h2_indent_threshold: float = 50.0,
        title_width_threshold: float = 0.8,
        min_heading_length: int = 2,
        max_heading_length: int = 200,
        language_detection: bool = True
    ):
        """Initialize PDF outline extractor.
        
        Args:
            min_h1_size_ratio: Minimum font size ratio for H1 detection
            min_h2_size_ratio: Minimum font size ratio for H2 detection
            min_h3_size_ratio: Minimum font size ratio for H3 detection
            h2_indent_threshold: X-coordinate threshold for H2/H3 distinction
            title_width_threshold: Minimum line width ratio for title detection
            min_heading_length: Minimum heading text length
            max_heading_length: Maximum heading text length
            language_detection: Whether to perform language detection
        """
        self.layout_analyzer = LayoutAnalyzer(
            min_h1_size_ratio=min_h1_size_ratio,
            min_h2_size_ratio=min_h2_size_ratio,
            min_h3_size_ratio=min_h3_size_ratio,
            h2_indent_threshold=h2_indent_threshold,
            title_width_threshold=title_width_threshold
        )
        
        self.text_normalizer = TextNormalizer()
        self.min_heading_length = min_heading_length
        self.max_heading_length = max_heading_length
        self.language_detection = language_detection
        self.logger = logging.getLogger(__name__)

    def extract_outline(self, pdf_path: Union[str, Path]) -> Dict[str, Any]:
        """Extract outline from a single PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with title and outline entries
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        self.logger.info(f"Extracting outline from {pdf_path}")
        
        try:
            # Open PDF document
            doc = fitz.open(str(pdf_path))
            
            # Extract text spans from all pages
            all_spans = []
            page_dimensions = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_width = page.rect.width
                page_height = page.rect.height
                page_dimensions.append((page_width, page_height))
                
                # Get text blocks with detailed information
                spans = self._extract_page_spans(page, page_num)
                
                # Enhance spans with layout analysis
                enhanced_spans = self.layout_analyzer.calculate_font_size_ratios(
                    spans, page_width
                )
                
                all_spans.extend(enhanced_spans)
            
            doc.close()
            
            # Detect title from first page
            first_page_spans = [s for s in all_spans if s.get('page', 0) == 0]
            title = self.layout_analyzer.detect_title(first_page_spans, page_num=0)
            
            # Extract heading entries
            outline_entries = self._extract_headings(all_spans)
            
            # Create metadata
            metadata = {
                'total_pages': len(doc) if 'doc' in locals() else 0,
                'extraction_method': 'PyMuPDF + Layout Analysis',
                'language_detection_enabled': self.language_detection,
                'page_dimensions': page_dimensions
            }
            
            return {
                'title': title,
                'outline': outline_entries,
                'metadata': metadata
            }
            
        except Exception as e:
            self.logger.error(f"Failed to extract outline from {pdf_path}: {e}")
            raise

    def _extract_page_spans(self, page: fitz.Page, page_num: int) -> List[Dict[str, Any]]:
        """Extract text spans from a single page.
        
        Args:
            page: PyMuPDF page object
            page_num: Page number (0-indexed)
            
        Returns:
            List of text spans with metadata
        """
        spans = []
        
        try:
            # Get text blocks with font information
            blocks = page.get_text("dict")
            
            for block in blocks["blocks"]:
                if "lines" not in block:
                    continue
                
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span.get("text", "").strip()
                        
                        if not text:
                            continue
                        
                        # Extract span information
                        span_info = {
                            'text': text,
                            'page': page_num,
                            'x': span.get("bbox", [0, 0, 0, 0])[0],
                            'y': span.get("bbox", [0, 0, 0, 0])[1],
                            'width': span.get("bbox", [0, 0, 0, 0])[2] - span.get("bbox", [0, 0, 0, 0])[0],
                            'height': span.get("bbox", [0, 0, 0, 0])[3] - span.get("bbox", [0, 0, 0, 0])[1],
                            'size': span.get("size", 12.0),
                            'font': span.get("font", ""),
                            'flags': span.get("flags", 0),
                            'color': span.get("color", 0),
                            'order': len(spans)  # Order of appearance
                        }
                        
                        # Process text with i18n utilities if enabled
                        if self.language_detection:
                            text_info = self.text_normalizer.process_multilingual_text(text)
                            span_info.update({
                                'normalized_text': text_info['normalized'],
                                'language': text_info['language'],
                                'language_confidence': text_info['confidence'],
                                'text_direction': text_info['direction'],
                                'script': text_info['script']
                            })
                        else:
                            span_info['normalized_text'] = self.text_normalizer.normalize_text(text)
                        
                        spans.append(span_info)
        
        except Exception as e:
            self.logger.warning(f"Error extracting spans from page {page_num}: {e}")
        
        return spans

    def _extract_headings(self, all_spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract heading entries from text spans.
        
        Args:
            all_spans: All text spans from the document
            
        Returns:
            List of heading entries with level, text, and page
        """
        headings = []
        
        for span in all_spans:
            text = span.get('normalized_text', span.get('text', ''))
            
            # Skip spans that are too short or too long
            if len(text) < self.min_heading_length or len(text) > self.max_heading_length:
                continue
            
            # Get context spans from the same page
            page_num = span.get('page', 0)
            context_spans = [s for s in all_spans if s.get('page') == page_num]
            
            # Classify heading level
            heading_level = self.layout_analyzer.classify_heading_level(span, context_spans)
            
            if heading_level:
                # Clean heading text
                clean_text = self.text_normalizer.extract_clean_heading_text(text)
                
                if clean_text:  # Only add if we have clean text
                    heading_entry = {
                        'level': heading_level,
                        'text': clean_text,
                        'page': page_num,
                        'order': span.get('order', 0),
                        'confidence': self._calculate_heading_confidence(span, context_spans)
                    }
                    
                    # Add language information if available
                    if self.language_detection and 'language' in span:
                        heading_entry['language'] = span['language']
                        heading_entry['language_confidence'] = span.get('language_confidence', 0.0)
                    
                    headings.append(heading_entry)
        
        # Filter and deduplicate headings
        filtered_headings = self._filter_headings(headings)
        
        return filtered_headings

    def _calculate_heading_confidence(
        self, 
        span: Dict[str, Any], 
        context_spans: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for heading classification.
        
        Args:
            span: Text span being evaluated
            context_spans: Other spans on the same page
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.0
        
        # Size ratio confidence
        size_ratio = span.get('size_ratio', 1.0)
        if size_ratio >= 1.5:
            confidence += 0.4
        elif size_ratio >= 1.3:
            confidence += 0.3
        elif size_ratio >= 1.1:
            confidence += 0.2
        
        # Structural patterns confidence
        text = span.get('text', '')
        patterns = self.layout_analyzer.detect_structural_patterns(text)
        
        if patterns['has_numbering']:
            confidence += 0.2
        if patterns['is_all_caps'] and len(text) > 5:
            confidence += 0.1
        
        # Position confidence
        x_pos = span.get('x', 0)
        if x_pos < 100:  # Left-aligned
            confidence += 0.1
        
        # Length confidence
        text_length = len(text.strip())
        if 10 <= text_length <= 80:  # Reasonable heading length
            confidence += 0.1
        
        # Language detection confidence
        if self.language_detection:
            lang_confidence = span.get('language_confidence', 0.0)
            confidence += lang_confidence * 0.1
        
        return min(confidence, 1.0)

    def _filter_headings(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and deduplicate heading entries.
        
        Args:
            headings: Raw heading entries
            
        Returns:
            Filtered heading entries
        """
        if not headings:
            return []
        
        # Sort by page and order
        sorted_headings = sorted(headings, key=lambda x: (x['page'], x['order']))
        
        # Remove duplicates and low-confidence headings
        filtered = []
        seen_texts = set()
        
        for heading in sorted_headings:
            text = heading['text'].lower().strip()
            confidence = heading.get('confidence', 0.0)
            
            # Skip very low confidence headings
            if confidence < 0.3:
                continue
            
            # Skip duplicates (case-insensitive)
            if text in seen_texts:
                continue
            
            # Skip headings that are too similar to previous ones
            if not self._is_distinct_heading(text, seen_texts):
                continue
            
            seen_texts.add(text)
            
            # Remove confidence and order from final output
            final_heading = {
                'level': heading['level'],
                'text': heading['text'],
                'page': heading['page']
            }
            
            filtered.append(final_heading)
        
        return filtered

    def _is_distinct_heading(self, text: str, seen_texts: set) -> bool:
        """Check if heading text is distinct from previously seen headings.
        
        Args:
            text: Heading text to check
            seen_texts: Set of previously seen heading texts
            
        Returns:
            True if text is distinct enough
        """
        # Simple similarity check - could be enhanced with fuzzy matching
        for seen in seen_texts:
            # Check for substring containment
            if (text in seen and len(text) > len(seen) * 0.8) or \
               (seen in text and len(seen) > len(text) * 0.8):
                return False
        
        return True

    def extract_multiple_outlines(
        self, 
        input_dir: Union[str, Path], 
        file_pattern: str = "*.pdf"
    ) -> Dict[str, Dict[str, Any]]:
        """Extract outlines from multiple PDF files.
        
        Args:
            input_dir: Directory containing PDF files
            file_pattern: Glob pattern for PDF files
            
        Returns:
            Dictionary mapping filenames to outline data
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input directory not found: {input_path}")
        
        pdf_files = list(input_path.glob(file_pattern))
        
        if not pdf_files:
            self.logger.warning(f"No PDF files found in {input_path} with pattern {file_pattern}")
            return {}
        
        results = {}
        
        for pdf_file in pdf_files:
            try:
                self.logger.info(f"Processing {pdf_file.name}")
                outline_data = self.extract_outline(pdf_file)
                results[pdf_file.name] = outline_data
                
            except Exception as e:
                self.logger.error(f"Failed to process {pdf_file.name}: {e}")
                # Continue with other files
                continue
        
        return results

    def batch_extract_and_save(
        self,
        input_dir: Union[str, Path],
        output_dir: Union[str, Path],
        file_pattern: str = "*.pdf"
    ) -> List[Path]:
        """Extract outlines from multiple PDFs and save JSON files.
        
        Args:
            input_dir: Directory containing PDF files
            output_dir: Directory for output JSON files
            file_pattern: Glob pattern for PDF files
            
        Returns:
            List of paths to created JSON files
        """
        # Extract outlines
        outlines = self.extract_multiple_outlines(input_dir, file_pattern)
        
        if not outlines:
            self.logger.warning("No outlines extracted")
            return []
        
        # Save JSON files
        json_writer = JSONWriter(output_dir)
        written_files = json_writer.write_multiple_outlines(outlines)
        
        self.logger.info(f"Successfully processed {len(written_files)} PDF files")
        return written_files
