"""
Tests for PDF outline extractor.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Import the new modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pdf_outline_extractor.extractor_new import PDFOutlineExtractor
from pdf_outline_extractor.layout_utils_new import LayoutAnalyzer
from pdf_outline_extractor.i18n_utils_new import normalize_text, detect_language
from pdf_outline_extractor.json_writer_new import OutlineWriter


class TestPDFOutlineExtractor:
    """Test the main extractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PDFOutlineExtractor()
    
    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        extractor = PDFOutlineExtractor()
        assert extractor.min_h1_size_ratio == 1.5
        assert extractor.min_h2_size_ratio == 1.3
        assert extractor.min_h3_size_ratio == 1.1
        assert extractor.h2_indent_threshold == 20.0
    
    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        extractor = PDFOutlineExtractor(
            min_h1_size_ratio=1.6,
            min_h2_size_ratio=1.4,
            min_h3_size_ratio=1.2,
            h2_indent_threshold=30.0
        )
        assert extractor.min_h1_size_ratio == 1.6
        assert extractor.min_h2_size_ratio == 1.4
        assert extractor.min_h3_size_ratio == 1.2
        assert extractor.h2_indent_threshold == 30.0
    
    def test_extract_outline_missing_file(self):
        """Test handling of missing PDF file."""
        result = self.extractor.extract_outline("nonexistent.pdf")
        assert result["title"] == ""
        assert result["outline"] == []
    
    def test_clean_heading_text(self):
        """Test heading text cleaning."""
        # Test basic cleaning
        result = self.extractor._clean_heading_text("  Chapter 1: Introduction  ")
        assert result == "Chapter 1: Introduction"
        
        # Test multiple spaces
        result = self.extractor._clean_heading_text("Chapter    1:    Introduction")
        assert result == "Chapter 1: Introduction"
        
        # Test empty string
        result = self.extractor._clean_heading_text("")
        assert result == ""
        
        # Test with tabs and newlines (should be preserved)
        result = self.extractor._clean_heading_text("Chapter\t1:\nIntroduction")
        assert result == "Chapter\t1:\nIntroduction"
    
    def test_determine_heading_level(self):
        """Test heading level determination."""
        span = {
            "text": "Test Heading",
            "x": 10.0,
            "font_size": 18.0
        }
        
        # Test H1 level (size ratio >= 1.5)
        level = self.extractor._determine_heading_level(span, 1.6, False)
        assert level == "H1"
        
        # Test H2 level (size ratio >= 1.3, left-aligned)
        level = self.extractor._determine_heading_level(span, 1.4, False)
        assert level == "H2"
        
        # Test H3 level (size ratio >= 1.3, indented)
        span["x"] = 40.0
        level = self.extractor._determine_heading_level(span, 1.4, False)
        assert level == "H3"
        
        # Test H3 level (size ratio >= 1.1)
        level = self.extractor._determine_heading_level(span, 1.2, False)
        assert level == "H3"
        
        # Test no heading
        level = self.extractor._determine_heading_level(span, 1.0, False)
        assert level is None
    
    def test_looks_like_heading(self):
        """Test heading pattern recognition."""
        # Test ALL CAPS
        assert self.extractor._looks_like_heading("CHAPTER ONE", 1.1) == True
        
        # Test numbered section
        assert self.extractor._looks_like_heading("1. Introduction", 1.1) == True
        
        # Test chapter pattern
        assert self.extractor._looks_like_heading("Chapter 1", 1.1) == True
        
        # Test section pattern
        assert self.extractor._looks_like_heading("Section 2.1", 1.1) == True
        
        # Test part pattern
        assert self.extractor._looks_like_heading("Part I", 1.1) == True
        
        # Test small font size
        assert self.extractor._looks_like_heading("CHAPTER ONE", 0.9) == False
        
        # Test normal text
        assert self.extractor._looks_like_heading("this is normal text", 1.1) == False
    
    def test_filter_and_sort_headings(self):
        """Test heading filtering and sorting."""
        headings = [
            {"level": "H1", "text": "Chapter 1", "page": 2},
            {"level": "H2", "text": "Section 1.1", "page": 0},
            {"level": "H1", "text": "Chapter 1", "page": 2},  # Duplicate
            {"level": "H3", "text": "AB", "page": 1},  # Too short
            {"level": "H2", "text": "Section 1.2", "page": 1},
        ]
        
        filtered = self.extractor._filter_and_sort_headings(headings)
        
        # Should remove duplicates and too-short headings
        assert len(filtered) == 3
        
        # Should be sorted by page
        assert filtered[0]["page"] == 0
        assert filtered[1]["page"] == 1
        assert filtered[2]["page"] == 2
        
        # Should not contain duplicates or short headings
        texts = [h["text"] for h in filtered]
        assert "AB" not in texts
        assert texts.count("Chapter 1") == 1


class TestLayoutAnalyzer:
    """Test the layout analyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = LayoutAnalyzer()
    
    def test_has_numbering_or_bullets(self):
        """Test numbering and bullet detection."""
        # Test numbered lists
        assert self.analyzer.has_numbering_or_bullets("1. First item") == True
        assert self.analyzer.has_numbering_or_bullets("2 Second item") == True
        assert self.analyzer.has_numbering_or_bullets("a. Letter item") == True
        assert self.analyzer.has_numbering_or_bullets("A. Capital letter") == True
        
        # Test Roman numerals
        assert self.analyzer.has_numbering_or_bullets("i. Roman lower") == True
        assert self.analyzer.has_numbering_or_bullets("II. Roman upper") == True
        
        # Test bullets
        assert self.analyzer.has_numbering_or_bullets("• Bullet point") == True
        assert self.analyzer.has_numbering_or_bullets("- Dash point") == True
        
        # Test parentheses
        assert self.analyzer.has_numbering_or_bullets("(1) Parentheses") == True
        assert self.analyzer.has_numbering_or_bullets("(a) Letter paren") == True
        
        # Test normal text
        assert self.analyzer.has_numbering_or_bullets("Normal text") == False
        assert self.analyzer.has_numbering_or_bullets("Text with 1 number") == False
    
    def test_calculate_font_size_stats(self):
        """Test font size statistics calculation."""
        spans = [
            {"font_size": 12.0},
            {"font_size": 14.0},
            {"font_size": 16.0},
            {"font_size": 18.0},
        ]
        
        stats = self.analyzer.calculate_font_size_stats(spans)
        
        assert stats["min"] == 12.0
        assert stats["max"] == 18.0
        assert stats["mean"] == 15.0
        assert stats["median"] == 15.0
        assert stats["std"] > 0
    
    def test_calculate_font_size_stats_empty(self):
        """Test font size statistics with empty input."""
        stats = self.analyzer.calculate_font_size_stats([])
        
        assert stats["min"] == 12.0
        assert stats["max"] == 12.0
        assert stats["mean"] == 12.0
        assert stats["median"] == 12.0
        assert stats["std"] == 0.0
    
    def test_find_common_indents(self):
        """Test finding common indentation levels."""
        margins = [0.0, 5.0, 20.0, 22.0, 40.0, 42.0, 100.0]
        
        indents = self.analyzer._find_common_indents(margins, tolerance=5.0)
        
        # Should group similar margins
        assert len(indents) == 3  # 0-5, 20-22, 40-42 groups, 100 is single
        assert 0.0 in indents or 5.0 in indents  # Representative of first group
        assert 20.0 in indents or 22.0 in indents  # Representative of second group
        assert 40.0 in indents or 42.0 in indents  # Representative of third group
    
    def test_detect_title_candidates(self):
        """Test title detection."""
        spans = [
            {
                "text": "Document Title",
                "font_size": 24.0,
                "width": 200.0,
                "x": 100.0,
                "y": 50.0
            },
            {
                "text": "Small text",
                "font_size": 12.0,
                "width": 100.0,
                "x": 0.0,
                "y": 200.0
            }
        ]
        
        candidates = self.analyzer.detect_title_candidates(spans, page_width=400.0)
        
        assert len(candidates) >= 1
        assert candidates[0]["text"] == "Document Title"
        assert candidates[0]["score"] > candidates[1]["score"] if len(candidates) > 1 else True
    
    def test_clean_heading_text(self):
        """Test heading text cleaning."""
        # Test basic cleaning
        result = self.analyzer.clean_heading_text("  Chapter 1  ")
        assert result == "Chapter 1"
        
        # Test preserve structure
        result = self.analyzer.clean_heading_text("1. Chapter Title", preserve_structure=True)
        assert result == "1. Chapter Title"
        
        # Test remove structure
        result = self.analyzer.clean_heading_text("1. Chapter Title", preserve_structure=False)
        assert result == "Chapter Title"
    
    def test_validate_heading_sequence(self):
        """Test heading sequence validation."""
        headings = [
            {"level": "H1", "text": "Chapter 1", "page": 0},
            {"level": "H3", "text": "Subsection", "page": 1},  # Skip H2
            {"level": "H2", "text": "Section 1.1", "page": 2},
        ]
        
        validated = self.analyzer.validate_heading_sequence(headings)
        
        # Should correct the sequence
        assert len(validated) == 3
        assert validated[1]["level"] == "H2"  # H3 should be corrected to H2


class TestI18nUtils:
    """Test internationalization utilities."""
    
    def test_normalize_text(self):
        """Test text normalization."""
        # Test Unicode normalization
        text = "café"  # é can be composed or decomposed
        normalized = normalize_text(text)
        assert len(normalized) <= len(text)  # NFC normalization should reduce length
        
        # Test empty string
        assert normalize_text("") == ""
        
        # Test with tabs and newlines (should be preserved)
        text_with_whitespace = "text\twith\ntabs"
        normalized = normalize_text(text_with_whitespace)
        assert "\t" in normalized
        assert "\n" in normalized
    
    def test_detect_language(self):
        """Test language detection."""
        # Test English
        assert detect_language("Hello world") == "en"
        
        # Test Arabic (if Arabic text provided)
        assert detect_language("مرحبا بالعالم") == "ar"
        
        # Test Hebrew
        assert detect_language("שלום עולם") == "he"
        
        # Test empty string
        assert detect_language("") == "en"
        
        # Test short string
        assert detect_language("Hi") == "en"
    
    def test_is_rtl_language(self):
        """Test RTL language detection."""
        from pdf_outline_extractor.i18n_utils_new import is_rtl_language
        
        assert is_rtl_language("ar") == True
        assert is_rtl_language("he") == True
        assert is_rtl_language("en") == False
        assert is_rtl_language("zh") == False
    
    def test_clean_text_for_analysis(self):
        """Test text cleaning for analysis."""
        from pdf_outline_extractor.i18n_utils_new import clean_text_for_analysis
        
        # Test multiple spaces
        result = clean_text_for_analysis("text  with   spaces")
        assert result == "text with spaces"
        
        # Test zero-width characters
        text_with_zwc = "text\u200Bwith\u200Czwc"
        result = clean_text_for_analysis(text_with_zwc)
        assert "\u200B" not in result
        assert "\u200C" not in result
    
    def test_extract_text_features(self):
        """Test text feature extraction."""
        from pdf_outline_extractor.i18n_utils_new import extract_text_features
        
        features = extract_text_features("Chapter 1: Introduction")
        
        assert features["length"] > 0
        assert features["word_count"] == 2
        assert features["has_digits"] == True
        assert features["has_punctuation"] == True
        assert features["language"] == "en"
        assert features["is_rtl"] == False
    
    def test_validate_heading_text(self):
        """Test heading text validation."""
        from pdf_outline_extractor.i18n_utils_new import validate_heading_text
        
        # Valid headings
        assert validate_heading_text("Chapter 1") == True
        assert validate_heading_text("Introduction") == True
        
        # Invalid headings
        assert validate_heading_text("") == False
        assert validate_heading_text("A") == False  # Too short
        assert validate_heading_text("...") == False  # Mostly punctuation
        assert validate_heading_text("A" * 300) == False  # Too long


class TestOutlineWriter:
    """Test the JSON writer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.writer = OutlineWriter()
    
    def test_format_outline_data(self):
        """Test outline data formatting."""
        data = {
            "title": "Test Document",
            "outline": [
                {"level": "H1", "text": "Chapter 1", "page": 0},
                {"level": "H2", "text": "Section 1.1", "page": 1},
            ]
        }
        
        formatted = self.writer._format_outline_data(data)
        
        assert formatted["title"] == "Test Document"
        assert len(formatted["outline"]) == 2
        assert formatted["outline"][0]["level"] == "H1"
        assert formatted["outline"][0]["page"] == 0
    
    def test_validate_outline_format(self):
        """Test outline format validation."""
        # Valid data
        valid_data = {
            "title": "Test",
            "outline": [
                {"level": "H1", "text": "Chapter", "page": 0}
            ]
        }
        errors = self.writer.validate_outline_format(valid_data)
        assert len(errors) == 0
        
        # Invalid data - missing title
        invalid_data = {
            "outline": [
                {"level": "H1", "text": "Chapter", "page": 0}
            ]
        }
        errors = self.writer.validate_outline_format(invalid_data)
        assert len(errors) > 0
        assert any("title" in error for error in errors)
    
    def test_compare_outlines(self):
        """Test outline comparison."""
        pred_data = {
            "title": "Test",
            "outline": [
                {"level": "H1", "text": "Chapter 1", "page": 0},
                {"level": "H2", "text": "Section 1.1", "page": 1},
            ]
        }
        
        gold_data = {
            "title": "Test",
            "outline": [
                {"level": "H1", "text": "Chapter 1", "page": 0},
                {"level": "H2", "text": "Different Section", "page": 1},
            ]
        }
        
        metrics = self.writer.compare_outlines(pred_data, gold_data)
        
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics
        assert metrics["precision"] == 0.5  # 1 out of 2 predictions correct
        assert metrics["recall"] == 0.5     # 1 out of 2 gold correct
    
    def test_write_and_read_outline(self):
        """Test writing and reading outline files."""
        outline_data = {
            "title": "Test Document",
            "outline": [
                {"level": "H1", "text": "Chapter 1", "page": 0}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            # Write outline
            success = self.writer.write_outline(outline_data, temp_path)
            assert success == True
            
            # Read it back
            read_data = self.writer.read_outline(temp_path)
            assert read_data["title"] == "Test Document"
            assert len(read_data["outline"]) == 1
            assert read_data["outline"][0]["level"] == "H1"
            
        finally:
            os.unlink(temp_path)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_pdf_handling(self):
        """Test handling of PDFs with no text."""
        extractor = PDFOutlineExtractor()
        
        # Mock empty PDF
        with patch('fitz.open') as mock_open:
            mock_doc = Mock()
            mock_doc.page_count = 1
            mock_page = Mock()
            mock_page.get_text.return_value = {"blocks": []}
            mock_doc.__getitem__.return_value = mock_page
            mock_open.return_value = mock_doc
            
            result = extractor.extract_outline("empty.pdf")
            assert result["title"] == ""
            assert result["outline"] == []
    
    def test_mixed_language_headings(self):
        """Test handling of mixed-language headings."""
        extractor = PDFOutlineExtractor()
        
        # Test with mixed scripts
        mixed_texts = [
            "Chapter 1: مقدمة",  # English + Arabic
            "第一章：Introduction",  # Chinese + English
            "Κεφάλαιο 1",  # Greek
        ]
        
        for text in mixed_texts:
            # Should not crash on mixed languages
            cleaned = extractor._clean_heading_text(text)
            assert len(cleaned) > 0
    
    def test_tabs_newlines_in_headings(self):
        """Test handling of tabs and newlines in headings."""
        extractor = PDFOutlineExtractor()
        
        # Test with tabs and newlines
        text_with_whitespace = "Chapter\t1:\nIntroduction"
        cleaned = extractor._clean_heading_text(text_with_whitespace)
        
        # Should preserve tabs and newlines as per spec
        assert "\t" in cleaned
        assert "\n" in cleaned
    
    def test_unicode_edge_cases(self):
        """Test Unicode edge cases."""
        from pdf_outline_extractor.i18n_utils_new import normalize_text, handle_special_characters
        
        # Test with emoji
        text_with_emoji = "📖 Chapter 1: Introduction 🎉"
        normalized = normalize_text(text_with_emoji)
        assert "📖" in normalized
        assert "🎉" in normalized
        
        # Test with combining characters
        text_with_combining = "café"  # e + combining acute
        processed = handle_special_characters(text_with_combining)
        assert len(processed) > 0
        
        # Test with unusual punctuation
        text_with_punct = "Chapter‽ 1… Introduction⁇"
        processed = handle_special_characters(text_with_punct)
        assert "‽" in processed  # Interrobang
        assert "…" in processed  # Ellipsis
        assert "⁇" in processed  # Double question mark


if __name__ == "__main__":
    pytest.main([__file__])
