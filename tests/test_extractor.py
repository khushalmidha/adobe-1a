"""Tests for PDF outline extraction functionality."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from pdf_outline_extractor.extractor import PDFOutlineExtractor
from pdf_outline_extractor.layout_utils import LayoutAnalyzer
from pdf_outline_extractor.json_writer import JSONWriter
from tests.fixtures import SAMPLE_OUTLINE, MULTILINGUAL_OUTLINE, EDGE_CASE_OUTLINE


class TestPDFOutlineExtractor:
    """Test cases for PDFOutlineExtractor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = PDFOutlineExtractor()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_extractor_initialization(self):
        """Test extractor initialization with custom parameters."""
        extractor = PDFOutlineExtractor(
            min_h1_size_ratio=2.0,
            min_h2_size_ratio=1.5,
            h2_indent_threshold=75.0
        )
        
        assert extractor.layout_analyzer.min_h1_size_ratio == 2.0
        assert extractor.layout_analyzer.min_h2_size_ratio == 1.5
        assert extractor.layout_analyzer.h2_indent_threshold == 75.0
    
    @patch('fitz.open')
    def test_extract_outline_file_not_found(self, mock_fitz_open):
        """Test handling of non-existent PDF files."""
        mock_fitz_open.side_effect = FileNotFoundError()
        
        with pytest.raises(FileNotFoundError):
            self.extractor.extract_outline("nonexistent.pdf")
    
    @patch('fitz.open')
    def test_extract_outline_success(self, mock_fitz_open):
        """Test successful outline extraction."""
        # Mock PyMuPDF document and page
        mock_doc = MagicMock()
        mock_page = MagicMock()
        
        # Configure mock document
        mock_doc.__len__ = Mock(return_value=3)
        mock_doc.__iter__ = Mock(return_value=iter([mock_page, mock_page, mock_page]))
        mock_page.rect.width = 612
        mock_page.rect.height = 792
        
        # Mock text extraction
        mock_page.get_text.return_value = {
            "blocks": [
                {
                    "lines": [
                        {
                            "spans": [
                                {
                                    "text": "Chapter 1: Introduction",
                                    "bbox": [50, 100, 300, 120],
                                    "size": 18.0,
                                    "font": "Arial-Bold",
                                    "flags": 0,
                                    "color": 0
                                },
                                {
                                    "text": "1.1 Background",
                                    "bbox": [70, 150, 250, 168],
                                    "size": 14.0,
                                    "font": "Arial",
                                    "flags": 0,
                                    "color": 0
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        mock_fitz_open.return_value = mock_doc
        
        # Create a temporary PDF file
        test_pdf = self.temp_dir / "test.pdf"
        test_pdf.write_bytes(b"fake pdf content")
        
        # Extract outline
        result = self.extractor.extract_outline(test_pdf)
        
        # Verify results
        assert isinstance(result, dict)
        assert 'title' in result
        assert 'outline' in result
        assert 'metadata' in result
        assert isinstance(result['outline'], list)
    
    def test_extract_multiple_outlines(self):
        """Test extracting outlines from multiple files."""
        # Create test directory with no PDF files
        empty_dir = self.temp_dir / "empty"
        empty_dir.mkdir()
        
        results = self.extractor.extract_multiple_outlines(empty_dir)
        assert results == {}
        
        # Test with non-existent directory
        with pytest.raises(FileNotFoundError):
            self.extractor.extract_multiple_outlines("nonexistent_dir")
    
    def test_calculate_heading_confidence(self):
        """Test heading confidence calculation."""
        span = {
            'text': 'Chapter 1: Introduction',
            'size_ratio': 1.6,
            'x': 50,
            'language_confidence': 0.9
        }
        
        context_spans = [span]
        confidence = self.extractor._calculate_heading_confidence(span, context_spans)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should have decent confidence for this example
    
    def test_filter_headings(self):
        """Test heading filtering and deduplication."""
        headings = [
            {'level': 'H1', 'text': 'Chapter 1', 'page': 0, 'confidence': 0.8, 'order': 1},
            {'level': 'H1', 'text': 'Chapter 1', 'page': 0, 'confidence': 0.7, 'order': 2},  # Duplicate
            {'level': 'H2', 'text': 'Section 1.1', 'page': 1, 'confidence': 0.6, 'order': 3},
            {'level': 'H3', 'text': 'Low confidence', 'page': 2, 'confidence': 0.2, 'order': 4},  # Low confidence
        ]
        
        filtered = self.extractor._filter_headings(headings)
        
        assert len(filtered) == 2  # Should remove duplicate and low confidence
        assert all('confidence' not in h for h in filtered)  # Should remove confidence field
        assert all('order' not in h for h in filtered)  # Should remove order field
    
    def test_is_distinct_heading(self):
        """Test heading distinctness check."""
        seen_texts = {'chapter 1: introduction', 'section 1.1 background'}
        
        # Should be distinct
        assert self.extractor._is_distinct_heading('chapter 2: methodology', seen_texts)
        
        # Should not be distinct (substring)
        assert not self.extractor._is_distinct_heading('chapter 1', seen_texts)
        assert not self.extractor._is_distinct_heading('introduction', seen_texts)


class TestLayoutAnalyzer:
    """Test cases for LayoutAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = LayoutAnalyzer()
    
    def test_initialization(self):
        """Test layout analyzer initialization."""
        analyzer = LayoutAnalyzer(
            min_h1_size_ratio=2.0,
            h2_indent_threshold=100.0
        )
        
        assert analyzer.min_h1_size_ratio == 2.0
        assert analyzer.h2_indent_threshold == 100.0
    
    def test_calculate_font_size_ratios(self):
        """Test font size ratio calculation."""
        spans = [
            {'size': 12.0, 'width': 100, 'x': 50, 'text': 'Normal text'},
            {'size': 18.0, 'width': 200, 'x': 50, 'text': 'Large text'},
            {'size': 10.0, 'width': 80, 'x': 100, 'text': 'Small text'}
        ]
        
        enhanced_spans = self.analyzer.calculate_font_size_ratios(spans, 400)
        
        assert len(enhanced_spans) == 3
        for span in enhanced_spans:
            assert 'size_ratio' in span
            assert 'width_ratio' in span
            assert 'indent_level' in span
            assert span['size_ratio'] > 0
    
    def test_calculate_indent_level(self):
        """Test indentation level calculation."""
        assert self.analyzer._calculate_indent_level(20) == 0
        assert self.analyzer._calculate_indent_level(75) == 1
        assert self.analyzer._calculate_indent_level(125) == 2
        assert self.analyzer._calculate_indent_level(200) == 3
    
    def test_classify_heading_level(self):
        """Test heading level classification."""
        span_h1 = {
            'text': 'Chapter 1: Introduction',
            'size_ratio': 1.6,
            'indent_level': 0
        }
        
        span_h2 = {
            'text': '1.1 Background',
            'size_ratio': 1.4,
            'indent_level': 1
        }
        
        span_h3 = {
            'text': '1.1.1 Details',
            'size_ratio': 1.2,
            'indent_level': 2
        }
        
        span_normal = {
            'text': 'Regular paragraph text',
            'size_ratio': 1.0,
            'indent_level': 0
        }
        
        context_spans = [span_h1, span_h2, span_h3, span_normal]
        
        assert self.analyzer.classify_heading_level(span_h1, context_spans) == 'H1'
        assert self.analyzer.classify_heading_level(span_h2, context_spans) == 'H2'
        assert self.analyzer.classify_heading_level(span_h3, context_spans) == 'H3'
        assert self.analyzer.classify_heading_level(span_normal, context_spans) is None
    
    def test_detect_title(self):
        """Test title detection."""
        spans = [
            {
                'text': 'Document Title',
                'size_ratio': 2.0,
                'width_ratio': 0.9,
                'y': 50
            },
            {
                'text': 'Chapter 1',
                'size_ratio': 1.5,
                'width_ratio': 0.5,
                'y': 100
            }
        ]
        
        title = self.analyzer.detect_title(spans, page_num=0)
        assert title == 'Document Title'
        
        # Should not detect title on non-first page
        title_none = self.analyzer.detect_title(spans, page_num=1)
        assert title_none is None
    
    def test_detect_structural_patterns(self):
        """Test structural pattern detection."""
        patterns1 = self.analyzer.detect_structural_patterns('1. Introduction')
        assert patterns1['has_numbering'] is True
        assert patterns1['has_bullet'] is False
        
        patterns2 = self.analyzer.detect_structural_patterns('• Bullet point')
        assert patterns2['has_numbering'] is False
        assert patterns2['has_bullet'] is True
        
        patterns3 = self.analyzer.detect_structural_patterns('CHAPTER TITLE')
        assert patterns3['is_all_caps'] is True
    
    def test_analyze_text_flow(self):
        """Test text flow analysis."""
        spans = [
            {'x': 50, 'y': 100, 'width': 100, 'height': 12, 'text': 'First line'},
            {'x': 50, 'y': 120, 'width': 120, 'height': 12, 'text': 'Second line'},
            {'x': 300, 'y': 100, 'width': 90, 'height': 12, 'text': 'Right column'},
        ]
        
        flow_analysis = self.analyzer.analyze_text_flow(spans)
        
        assert 'reading_order' in flow_analysis
        assert 'columns' in flow_analysis
        assert 'text_density' in flow_analysis
        assert len(flow_analysis['reading_order']) == 3


class TestJSONWriter:
    """Test cases for JSONWriter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.writer = JSONWriter(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_create_outline_json(self):
        """Test JSON outline creation."""
        title = "Test Document"
        outline_entries = [
            {'level': 'H1', 'text': 'Chapter 1', 'page': 0, 'order': 1},
            {'level': 'H2', 'text': 'Section 1.1', 'page': 1, 'order': 2}
        ]
        
        json_data = self.writer.create_outline_json(title, outline_entries)
        
        assert json_data['title'] == title
        assert len(json_data['outline']) == 2
        assert json_data['outline'][0]['level'] == 'H1'
        assert 'order' not in json_data['outline'][0]  # Should be removed
    
    def test_write_outline_json(self):
        """Test writing JSON outline to file."""
        title = "Test Document"
        outline_entries = [
            {'level': 'H1', 'text': 'Chapter 1', 'page': 0}
        ]
        
        output_path = self.writer.write_outline_json(
            'test_output', title, outline_entries
        )
        
        assert output_path.exists()
        assert output_path.suffix == '.json'
        
        # Read and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data['title'] == title
        assert len(data['outline']) == 1
    
    def test_validate_json_format(self):
        """Test JSON format validation."""
        valid_json = {
            'title': 'Test',
            'outline': [
                {'level': 'H1', 'text': 'Chapter 1', 'page': 0}
            ]
        }
        
        invalid_json = {
            'title': 'Test',
            'outline': 'not a list'
        }
        
        assert self.writer.validate_json_format(valid_json) is True
        assert self.writer.validate_json_format(invalid_json) is False
    
    def test_compare_outlines(self):
        """Test outline comparison functionality."""
        # Create predicted and gold directories
        pred_dir = self.temp_dir / 'predicted'
        gold_dir = self.temp_dir / 'gold'
        pred_dir.mkdir()
        gold_dir.mkdir()
        
        # Create test files
        pred_data = {
            'title': 'Test',
            'outline': [
                {'level': 'H1', 'text': 'Chapter 1', 'page': 0},
                {'level': 'H2', 'text': 'Section 1.1', 'page': 1}
            ]
        }
        
        gold_data = {
            'title': 'Test',
            'outline': [
                {'level': 'H1', 'text': 'Chapter 1', 'page': 0},
                {'level': 'H2', 'text': 'Section 1.2', 'page': 1}  # Different text
            ]
        }
        
        with open(pred_dir / 'test.json', 'w') as f:
            json.dump(pred_data, f)
        
        with open(gold_dir / 'test.json', 'w') as f:
            json.dump(gold_data, f)
        
        # Compare
        results = self.writer.compare_outlines(pred_dir, gold_dir)
        
        assert 'test' in results
        assert 'precision' in results['test']
        assert 'recall' in results['test']
        assert 'f1' in results['test']
    
    def test_calculate_metrics(self):
        """Test metrics calculation."""
        predicted = [
            {'level': 'H1', 'text': 'Chapter 1', 'page': 0},
            {'level': 'H2', 'text': 'Section 1.1', 'page': 1},
            {'level': 'H2', 'text': 'Wrong section', 'page': 2}
        ]
        
        gold = [
            {'level': 'H1', 'text': 'Chapter 1', 'page': 0},
            {'level': 'H2', 'text': 'Section 1.1', 'page': 1},
            {'level': 'H2', 'text': 'Correct section', 'page': 2}
        ]
        
        metrics = self.writer._calculate_metrics(predicted, gold)
        
        assert metrics['true_positives'] == 2
        assert metrics['false_positives'] == 1
        assert metrics['false_negatives'] == 1
        assert metrics['precision'] == 2/3
        assert metrics['recall'] == 2/3
    
    def test_generate_comparison_report(self):
        """Test comparison report generation."""
        results = {
            'file1': {
                'precision': 0.8,
                'recall': 0.7,
                'f1': 0.75,
                'true_positives': 4,
                'false_positives': 1,
                'false_negatives': 1
            }
        }
        
        report = self.writer.generate_comparison_report(results)
        
        assert 'PDF Outline Extraction Comparison Report' in report
        assert 'Overall Metrics:' in report
        assert 'Per-File Results:' in report
        assert 'file1:' in report


class TestIntegration:
    """Integration tests combining multiple components."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_no_pdf(self):
        """Test end-to-end workflow without actual PDF files."""
        extractor = PDFOutlineExtractor()
        
        # Test with empty directory
        input_dir = self.temp_dir / 'input'
        output_dir = self.temp_dir / 'output'
        input_dir.mkdir()
        output_dir.mkdir()
        
        results = extractor.extract_multiple_outlines(input_dir)
        assert results == {}
    
    def test_json_workflow(self):
        """Test complete JSON workflow."""
        # Create sample data
        outline_data = {
            'sample.pdf': {
                'title': 'Sample Document',
                'outline': [
                    {'level': 'H1', 'text': 'Chapter 1', 'page': 0}
                ]
            }
        }
        
        # Write JSON files
        output_dir = self.temp_dir / 'output'
        writer = JSONWriter(output_dir)
        written_files = writer.write_multiple_outlines(outline_data)
        
        assert len(written_files) == 1
        assert written_files[0].exists()
        
        # Read back and verify
        read_data = writer.read_json_file(written_files[0])
        assert read_data is not None
        assert read_data['title'] == 'Sample Document'
        assert len(read_data['outline']) == 1


@pytest.fixture
def sample_spans():
    """Fixture providing sample text spans for testing."""
    return [
        {
            'text': 'Document Title',
            'size': 24.0,
            'x': 50,
            'y': 50,
            'width': 300,
            'height': 24,
            'page': 0
        },
        {
            'text': 'Chapter 1: Introduction',
            'size': 18.0,
            'x': 50,
            'y': 100,
            'width': 250,
            'height': 18,
            'page': 0
        },
        {
            'text': '1.1 Background',
            'size': 14.0,
            'x': 70,
            'y': 130,
            'width': 200,
            'height': 14,
            'page': 0
        }
    ]


def test_sample_spans_fixture(sample_spans):
    """Test the sample spans fixture."""
    assert len(sample_spans) == 3
    assert sample_spans[0]['text'] == 'Document Title'
    assert sample_spans[1]['size'] == 18.0
    assert all('page' in span for span in sample_spans)
