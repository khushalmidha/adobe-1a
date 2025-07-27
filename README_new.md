# PDF Outline Extractor - Adobe Hackathon Round 1A

A pure Python library for extracting structured outlines from PDF documents. This solution uses rule-based algorithms and font analysis to identify document titles and hierarchical headings (H1, H2, H3, H4) without requiring machine learning models.

## 🎯 Problem Statement

Extract structured outlines from PDF documents up to 50 pages, identifying:
- Document title
- Hierarchical headings (H1, H2, H3, H4) with page numbers
- Output in JSON format with 0-based page indexing

## 🏗️ Architecture & Approach

### Core Algorithm
The solution uses a multi-layered approach for heading detection:

1. **Font Size Analysis**: Calculate font size ratios relative to page average
   - H1: ratio ≥ 1.5
   - H2: ratio ≥ 1.3 
   - H3: ratio ≥ 1.1
   - H4: ratio ≥ 1.0 (with additional conditions)

2. **Layout Analysis**: Use X-coordinate positioning for hierarchy
   - H2: X ≤ 20px (left-aligned)
   - H3: 20px < X ≤ 40px (slightly indented)
   - H4: X > 40px (further indented)

3. **Structural Pattern Recognition**: Detect numbering and bullets
   - Numbers: "1.", "1.1", "1.1.1"
   - Letters: "a.", "A.", "i.", "IV."
   - Bullets: "•", "-", "*"

4. **Content Pattern Matching**: Identify heading-like text
   - ALL CAPS patterns
   - Title case patterns
   - Common section names (Chapter, Section, Appendix)
   - Short standalone text

### Multilingual Support
- Unicode NFC normalization for consistent character representation
- Support for CJK (Chinese, Japanese, Korean) scripts
- Right-to-left scripts (Arabic, Hebrew)
- Preserves special characters including `\t`, `\n` as literal text
- No language detection models - uses character pattern analysis

## 📁 Project Structure

```
├── README.md
├── setup.py                    # Package installation
├── pyproject.toml             # Project metadata
├── Dockerfile                 # AMD64 compatible container
├── requirements.txt           # Minimal dependencies (no ML)
├── src/
│   └── pdf_outline_extractor/
│       ├── __init__.py
│       ├── cli_clean.py       # CLI interface with compare functionality
│       ├── extractor_new.py   # Core PDF processing & heading detection
│       └── extractor.py       # Legacy version
├── tests/
│   ├── test_comprehensive_new.py  # Complete test suite
│   ├── expected/              # Ground truth JSON files
│   ├── output/               # Generated test outputs
│   └── fixtures/             # Test PDF samples
└── examples/
    └── colab_notebook.ipynb  # Google Colab demo
```

## 🛠️ Installation & Usage

### Local Installation
```bash
# Clone the repository
git clone <repository-url>
cd pdf_outline_extractor

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Docker Usage (Recommended)
```bash
# Build the image (AMD64 compatible)
docker build --platform linux/amd64 -t pdf-outline-extractor:latest .

# Run with volume mounts
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-outline-extractor:latest
```

### CLI Commands
```bash
# Extract outlines from PDFs
python -m pdf_outline_extractor.cli_clean extract \
  --input-dir /path/to/pdfs \
  --output-dir /path/to/output \
  --verbose

# Compare results with ground truth
python -m pdf_outline_extractor.cli_clean compare \
  --pred-dir /path/to/output \
  --gold-dir /path/to/expected

# Custom parameters
python -m pdf_outline_extractor.cli_clean extract \
  --input-dir input \
  --output-dir output \
  --min-h1-size-ratio 1.6 \
  --h2-indent-threshold 25.0
```

## 📊 Output Format

The extractor generates JSON files with 0-based page indexing:

```json
{
    "title": "Document Title",
    "outline": [
        {
            "level": "H1",
            "text": "Introduction",
            "page": 0
        },
        {
            "level": "H2", 
            "text": "Background",
            "page": 1
        },
        {
            "level": "H3",
            "text": "Methodology",
            "page": 2
        }
    ]
}
```

## 🧪 Testing & Validation

### Running Tests
```bash
# Run comprehensive test suite
python -m pytest tests/test_comprehensive_new.py -v

# Test with coverage
python -m pytest tests/ --cov=src/pdf_outline_extractor --cov-report=html
```

### Evaluation Metrics
The solution includes automatic comparison with ground truth:
- **Precision**: Correctly identified headings / Total identified headings
- **Recall**: Correctly identified headings / Total actual headings  
- **F1 Score**: Harmonic mean of precision and recall

### Edge Cases Handled
- ✅ No headings in document (graceful empty outline)
- ✅ Mixed-language headings (multilingual support)
- ✅ Tabs and newlines inside headings (preserved as literal characters)
- ✅ Unusual fonts and sizes (relative ratio-based detection)
- ✅ Complex document layouts (multiple column, irregular spacing)
- ✅ Special characters and Unicode (full Unicode support)

## ⚡ Performance & Constraints

### Specifications Met
- ✅ **Execution Time**: ≤10 seconds for 50-page PDF
- ✅ **Network**: No internet calls (fully offline)
- ✅ **Model Size**: No ML models used (0 MB)
- ✅ **Architecture**: AMD64 compatible
- ✅ **Runtime**: CPU-only, 8 vCPUs, 16GB RAM

### Dependencies
- **PyMuPDF**: PDF text extraction (pure Python binding)
- **Standard Library**: re, statistics, pathlib, json, unicodedata
- **No ML Dependencies**: No TensorFlow, PyTorch, scikit-learn, or language models

## 🌍 Multilingual Features

### Supported Scripts
- **Latin**: English, French, German, Spanish, etc.
- **CJK**: Chinese (Simplified/Traditional), Japanese, Korean
- **RTL**: Arabic, Hebrew, Farsi
- **Cyrillic**: Russian, Bulgarian, Serbian
- **Other**: Greek, Thai, Hindi (Devanagari), and more

### Character Handling
- Unicode NFC normalization for consistent representation
- Preservation of diacritics, combining characters
- Support for emoji and special punctuation
- Literal preservation of whitespace characters (`\t`, `\n`)

## 🚀 Google Colab Integration

See `examples/colab_notebook.ipynb` for a complete demonstration:

```python
# Install and run in Google Colab
!git clone https://github.com/youruser/pdf_outline_extractor.git
%cd pdf_outline_extractor
!pip install -r requirements.txt
!pip install -e .

# Process sample PDFs
!python -m pdf_outline_extractor.cli_clean extract \
  --input-dir examples/input_pdfs \
  --output-dir examples/output_json \
  --verbose

# Compare with ground truth
!python -m pdf_outline_extractor.cli_clean compare \
  --pred-dir examples/output_json \
  --gold-dir examples/expected_json
```

## 🏆 Hackathon Scoring Alignment

### Heading Detection Accuracy (25 points)
- Rule-based algorithm with multiple heuristics
- Font size ratios + layout analysis + pattern recognition
- Comprehensive testing across various document types
- Support for complex hierarchies (H1-H4)

### Performance & Compliance (10 points)
- Pure Python implementation (no ML overhead)
- Optimized for speed with compiled regex patterns
- Memory efficient text processing
- Docker container under 200MB

### Multilingual Handling Bonus (10 points)
- Full Unicode support including CJK and RTL scripts
- Character normalization and preservation
- Language-agnostic pattern detection
- Tested with Japanese, Arabic, Chinese samples

## 🔧 Configuration Options

### Tunable Parameters
```python
extractor = PDFOutlineExtractor(
    min_h1_size_ratio=1.5,      # H1 font size threshold
    min_h2_size_ratio=1.3,      # H2 font size threshold
    min_h3_size_ratio=1.1,      # H3 font size threshold
    h2_indent_threshold=20.0,   # H2 indentation limit
    h3_indent_threshold=40.0    # H3 indentation limit
)
```

### Environment Variables
```bash
PYTHONPATH=/app/src           # Module path
PYTHONUNBUFFERED=1           # Immediate output
```

## 📈 Algorithm Details

### Title Extraction
1. Focus on first page (page 0)
2. Find largest font size spans
3. Check line width coverage (>80%)
4. Validate text length (>3 characters)
5. Fallback to first substantial text

### Heading Classification Priority
1. **Font Size Ratio** (primary indicator)
2. **X-coordinate Position** (hierarchy refinement)  
3. **Numbering/Bullets** (structural hints)
4. **Pattern Matching** (content analysis)
5. **Length & Context** (validation)

### Quality Assurance
- Duplicate removal (same text + page)
- Minimum text length filtering
- Page-based sorting
- Unicode normalization consistency

## 📝 License & Contributing

This project is developed for Adobe Hackathon Round 1A. The solution demonstrates production-ready code with comprehensive testing, documentation, and Docker deployment.

---

**Built with ❤️ for Adobe Hackathon Round 1A - Connecting the Dots Through Docs**
