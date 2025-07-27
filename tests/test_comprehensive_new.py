"""
Comprehensive test suite for PDF Outline Extractor.
Adobe Hackathon Round 1A submission.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pdf_outline_extractor.extractor_new import PDFOutlineExtractor
from pdf_outline_extractor.cli_clean import calculate_metrics, extract_outlines, compare_results


class TestPDFOutlineExtractor:
    """Test cases for PDFOutlineExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PDFOutlineExtractor()
    
    def test_initialization(self):
        """Test extractor initialization with default parameters."""
        assert self.extractor.min_h1_size_ratio == 1.5
        assert self.extractor.min_h2_size_ratio == 1.3
        assert self.extractor.min_h3_size_ratio == 1.1
        assert self.extractor.h2_indent_threshold == 20.0
        assert self.extractor.h3_indent_threshold == 40.0
    
    def test_initialization_custom_params(self):
        """Test extractor initialization with custom parameters."""
        custom_extractor = PDFOutlineExtractor(
            min_h1_size_ratio=1.6,
            min_h2_size_ratio=1.4,
            min_h3_size_ratio=1.2,
            h2_indent_threshold=25.0,
            h3_indent_threshold=45.0
        )
        assert custom_extractor.min_h1_size_ratio == 1.6
        assert custom_extractor.min_h2_size_ratio == 1.4
        assert custom_extractor.min_h3_size_ratio == 1.2
        assert custom_extractor.h2_indent_threshold == 25.0
        assert custom_extractor.h3_indent_threshold == 45.0
    
    def test_normalize_text_basic(self):
        """Test basic text normalization."""
        text = "Hello   World"
        normalized = self.extractor.normalize_text(text)
        assert normalized == "Hello World"
    
    def test_normalize_text_multilingual(self):
        """Test text normalization with multilingual content."""
        # Test with Unicode characters
        text = "Résumé\u00A0café"  # Non-breaking space
        normalized = self.extractor.normalize_text(text)
        assert "Résumé" in normalized
        assert "café" in normalized
    
    def test_normalize_text_preserve_newlines(self):
        """Test that newlines and tabs are preserved as literal characters."""
        text = "Line 1\nLine 2\tTabbed"
        normalized = self.extractor.normalize_text(text)
        assert "\n" in normalized
        assert "\t" in normalized
        assert normalized == "Line 1\nLine 2\tTabbed"
    
    def test_has_numbering_or_bullets(self):
        """Test numbering and bullet detection."""
        # Test numbered headings
        assert self.extractor._has_numbering_or_bullets("1. Introduction")
        assert self.extractor._has_numbering_or_bullets("1.1 Overview")
        assert self.extractor._has_numbering_or_bullets("1.1.1 Details")
        
        # Test lettered headings
        assert self.extractor._has_numbering_or_bullets("a. First point")
        assert self.extractor._has_numbering_or_bullets("A. First point")
        
        # Test bullets
        assert self.extractor._has_numbering_or_bullets("• Bullet point")
        assert self.extractor._has_numbering_or_bullets("- Dash point")
        assert self.extractor._has_numbering_or_bullets("* Star point")
        
        # Test Roman numerals
        assert self.extractor._has_numbering_or_bullets("i. Introduction")
        assert self.extractor._has_numbering_or_bullets("IV. Chapter Four")
        
        # Test plain text (should return False)
        assert not self.extractor._has_numbering_or_bullets("Plain heading")
        assert not self.extractor._has_numbering_or_bullets("Introduction")
    
    def test_looks_like_heading_patterns(self):
        """Test heading pattern detection."""
        # Test ALL CAPS
        assert self.extractor._looks_like_heading("CHAPTER ONE", 1.2)
        assert self.extractor._looks_like_heading("INTRODUCTION", 1.1)
        
        # Test numbered sections
        assert self.extractor._looks_like_heading("1. Introduction", 1.1)
        assert self.extractor._looks_like_heading("Chapter 1", 1.1)
        assert self.extractor._looks_like_heading("Section 2", 1.1)
        assert self.extractor._looks_like_heading("Part I", 1.1)
        assert self.extractor._looks_like_heading("Appendix A", 1.1)
        
        # Test title case
        assert self.extractor._looks_like_heading("Introduction to Machine Learning", 1.1)
        assert self.extractor._looks_like_heading("Data Processing Methods", 1.1)
        
        # Test short standalone text
        assert self.extractor._looks_like_heading("Background", 1.1)
        assert self.extractor._looks_like_heading("Methodology", 1.1)
        
        # Test cases that shouldn't be headings
        assert not self.extractor._looks_like_heading("This is a very long sentence that looks like regular paragraph text.", 1.1)
        assert not self.extractor._looks_like_heading("small text", 0.9)
        assert not self.extractor._looks_like_heading("Text ending with period.", 1.1)
    
    def test_determine_heading_level(self):
        """Test heading level determination logic."""
        # Create mock span with different properties
        span_h1 = {"x": 10, "text": "Chapter 1: Introduction"}
        span_h2 = {"x": 15, "text": "1.1 Overview"}
        span_h3 = {"x": 25, "text": "1.1.1 Details"}
        span_h4 = {"x": 45, "text": "1.1.1.1 Specifics"}
        
        # Test H1 classification (high font size ratio)
        assert self.extractor._determine_heading_level(span_h1, 1.6, False) == "H1"
        assert self.extractor._determine_heading_level(span_h1, 1.5, False) == "H1"
        
        # Test H2 classification (medium font size ratio, low indentation)
        assert self.extractor._determine_heading_level(span_h2, 1.4, False) == "H2"
        assert self.extractor._determine_heading_level(span_h2, 1.3, False) == "H2"
        
        # Test H3 classification (medium font size ratio, medium indentation)
        assert self.extractor._determine_heading_level(span_h3, 1.4, False) == "H3"
        assert self.extractor._determine_heading_level(span_h3, 1.2, False) == "H3"
        
        # Test H4 classification (low font size ratio, high indentation)
        assert self.extractor._determine_heading_level(span_h4, 1.2, False) == "H4"
        
        # Test with numbering
        assert self.extractor._determine_heading_level(span_h2, 1.1, True) == "H2"
        assert self.extractor._determine_heading_level(span_h3, 1.1, True) == "H3"
        
        # Test cases that shouldn't be headings
        assert self.extractor._determine_heading_level(span_h1, 0.9, False) is None
    
    @patch('fitz.open')
    def test_extract_outline_mock_pdf(self, mock_fitz_open):
        """Test outline extraction with mocked PDF."""
        # Create mock PDF document
        mock_doc = MagicMock()
        mock_doc.page_count = 2
        mock_fitz_open.return_value = mock_doc
        
        # Create mock pages with text spans
        mock_page1 = MagicMock()
        mock_page2 = MagicMock()
        mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
        
        # Mock text extraction for page 1 (title page)
        mock_page1.get_text.return_value = {
            "blocks": [{
                "lines": [{
                    "spans": [{
                        "text": "Sample Document Title",
                        "size": 18,
                        "font": "Arial-Bold",
                        "flags": 16,
                        "bbox": [50, 50, 250, 70]
                    }]
                }]
            }]
        }
        
        # Mock text extraction for page 2 (content page)
        mock_page2.get_text.return_value = {
            "blocks": [{
                "lines": [{
                    "spans": [{
                        "text": "1. Introduction",
                        "size": 14,
                        "font": "Arial-Bold",
                        "flags": 16,
                        "bbox": [20, 100, 120, 115]
                    }, {
                        "text": "1.1 Overview",
                        "size": 12,
                        "font": "Arial",
                        "flags": 0,
                        "bbox": [30, 120, 120, 135]
                    }]
                }]
            }]
        }
        
        # Extract outline
        result = self.extractor.extract_outline("mock_file.pdf")
        
        # Verify results
        assert "title" in result
        assert "outline" in result
        assert isinstance(result["outline"], list)
        
        # Verify that the document was opened and closed
        mock_fitz_open.assert_called_once_with("mock_file.pdf")
        mock_doc.close.assert_called_once()
    
    def test_extract_outline_file_not_found(self):
        """Test graceful handling of non-existent PDF files."""
        result = self.extractor.extract_outline("nonexistent.pdf")
        assert result == {"title": "", "outline": []}
    
    def test_filter_and_sort_headings(self):
        """Test heading filtering and sorting."""
        headings = [
            {"level": "H2", "text": "Background", "page": 1},
            {"level": "H1", "text": "Introduction", "page": 0},
            {"level": "H3", "text": "Details", "page": 1},
            {"level": "H2", "text": "Background", "page": 1},  # Duplicate
            {"level": "H2", "text": "AA", "page": 2},  # Too short
        ]
        
        filtered = self.extractor._filter_and_sort_headings(headings)
        
        # Should remove duplicates and short headings
        assert len(filtered) == 3
        
        # Should be sorted by page
        assert filtered[0]["page"] == 0
        assert filtered[1]["page"] == 1
        assert filtered[2]["page"] == 1
        
        # Should not contain duplicates or short headings
        texts = [h["text"] for h in filtered]
        assert texts.count("Background") == 1
        assert "AA" not in texts


class TestCLIFunctions:
    """Test cases for CLI functions."""
    
    def test_calculate_metrics_perfect_match(self):
        """Test metrics calculation with perfect match."""
        pred_data = {
            "title": "Test Document",
            "outline": [
                {"level": "H1", "text": "Introduction", "page": 0},
                {"level": "H2", "text": "Background", "page": 1}
            ]
        }
        gold_data = pred_data.copy()
        
        metrics = calculate_metrics(pred_data, gold_data)
        
        assert metrics["precision"] == 1.0
        assert metrics["recall"] == 1.0
        assert metrics["f1"] == 1.0
        assert metrics["true_positives"] == 2
        assert metrics["false_positives"] == 0
        assert metrics["false_negatives"] == 0
    
    def test_calculate_metrics_no_match(self):
        """Test metrics calculation with no matches."""
        pred_data = {
            "title": "Test Document",
            "outline": [
                {"level": "H1", "text": "Introduction", "page": 0},
                {"level": "H2", "text": "Background", "page": 1}
            ]
        }
        gold_data = {
            "title": "Test Document",
            "outline": [
                {"level": "H1", "text": "Conclusion", "page": 2},
                {"level": "H2", "text": "Summary", "page": 3}
            ]
        }
        
        metrics = calculate_metrics(pred_data, gold_data)
        
        assert metrics["precision"] == 0.0
        assert metrics["recall"] == 0.0
        assert metrics["f1"] == 0.0
        assert metrics["true_positives"] == 0
        assert metrics["false_positives"] == 2
        assert metrics["false_negatives"] == 2
    
    def test_calculate_metrics_partial_match(self):
        """Test metrics calculation with partial matches."""
        pred_data = {
            "title": "Test Document",
            "outline": [
                {"level": "H1", "text": "Introduction", "page": 0},
                {"level": "H2", "text": "Background", "page": 1},
                {"level": "H2", "text": "Extra Section", "page": 2}
            ]
        }
        gold_data = {
            "title": "Test Document",
            "outline": [
                {"level": "H1", "text": "Introduction", "page": 0},
                {"level": "H2", "text": "Methods", "page": 1}
            ]
        }
        
        metrics = calculate_metrics(pred_data, gold_data)
        
        # 1 true positive, 2 false positives, 1 false negative
        assert metrics["precision"] == 1/3  # 1/(1+2)
        assert metrics["recall"] == 1/2      # 1/(1+1)
        assert abs(metrics["f1"] - 2/5) < 0.001  # 2*(1/3)*(1/2)/((1/3)+(1/2))
    
    def test_calculate_metrics_empty_data(self):
        """Test metrics calculation with empty data."""
        pred_data = {"title": "", "outline": []}
        gold_data = {"title": "", "outline": []}
        
        metrics = calculate_metrics(pred_data, gold_data)
        
        assert metrics["precision"] == 0.0
        assert metrics["recall"] == 0.0
        assert metrics["f1"] == 0.0


class TestMultilingualSupport:
    """Test cases for multilingual content handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PDFOutlineExtractor()
    
    def test_normalize_text_unicode(self):
        """Test Unicode text normalization."""
        # Test various Unicode scripts
        texts = [
            "Résumé",  # French
            "naïve",   # Diacritics
            "日本語",   # Japanese
            "العربية",  # Arabic
            "עברית",   # Hebrew
            "Ελληνικά", # Greek
            "Русский", # Russian
            "中文",     # Chinese
        ]
        
        for text in texts:
            normalized = self.extractor.normalize_text(text)
            assert normalized == text  # Should preserve original characters
    
    def test_heading_patterns_multilingual(self):
        """Test heading pattern detection with multilingual content."""
        # Test with various scripts
        multilingual_headings = [
            ("第一章 导言", 1.2),  # Chinese
            ("序論", 1.2),        # Japanese
            ("مقدمة", 1.2),       # Arabic
            ("Введение", 1.2),    # Russian
            ("Εισαγωγή", 1.2),    # Greek
        ]
        
        for text, ratio in multilingual_headings:
            # Should detect as heading based on standalone text heuristic
            result = self.extractor._looks_like_heading(text, ratio)
            assert result, f"Failed to detect '{text}' as heading"
    
    def test_special_characters_preservation(self):
        """Test that special characters are preserved in headings."""
        special_texts = [
            "1.\tIntroduction",     # Tab character
            "Section\nA",          # Newline character
            "Price: $100",         # Dollar sign
            "Temperature: 20°C",   # Degree symbol
            "Test → Result",       # Arrow
            "α-β Testing",         # Greek letters
            "™ Trademark",         # Trademark symbol
        ]
        
        for text in special_texts:
            normalized = self.extractor.normalize_text(text)
            # Should preserve special characters as literal text
            assert normalized == text.replace("  ", " ")  # Only normalize multiple spaces


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
