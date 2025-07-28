# PDF Outline Extractor - Adobe Hackathon Round 1A

A high-performance PDF outline extraction tool that extracts structured document outlines (Title, H1, H2, H3 headings) from PDF files. Built specifically for Adobe Hackathon Round 1A challenge requirements.

## Quick Start (Hackathon Submission)

### Build and Run
```bash
# Build the Docker image
docker build --platform linux/amd64 -t pdf-outline-extractor .

# Run the container (place PDFs in ./input directory)
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-outline-extractor
```

### Expected Results
- Processes all PDF files from `./input/` directory
- Generates `filename.json` for each `filename.pdf` 
- Outputs saved to `./output/` directory
- Completes within 10 seconds for 50-page PDFs
- Works completely offline

## Output Format

The tool generates JSON files in the exact format specified by the challenge:

```json
{
  "title": "Understanding AI",
  "outline": [
    { "level": "H1", "text": "Introduction", "page": 1 },
    { "level": "H2", "text": "What is AI?", "page": 2 },
    { "level": "H3", "text": "History of AI", "page": 3 }
  ]
}
```

## Features

- **Fast Processing**: Processes 50-page PDFs in under 10 seconds
- **Hierarchical Extraction**: Identifies Title, H1, H2, and H3 headings with page numbers
- **High Accuracy**: Uses font size ratios and layout analysis for precise heading detection
- **Multilingual Support**: Handles various languages including RTL scripts and CJK characters
- **Offline Operation**: No internet connectivity required
- **AMD64 Optimized**: Built specifically for linux/amd64 architecture

## Technical Specifications

### Performance Requirements ✅
- **Execution Time**: ≤ 10 seconds for 50-page PDF
- **Model Size**: ≤ 200MB (no ML models used, pure rule-based)
- **Architecture**: AMD64 (x86_64) compatible
- **Network**: Fully offline operation
- **Resource Usage**: Optimized for 8 CPU / 16GB RAM systems

### Architecture
- **Pure Python Implementation**: No ML dependencies
- **PyMuPDF**: Fast PDF processing and text extraction
- **Font Analysis**: Size-ratio based heading detection
- **Layout Analysis**: Position-based hierarchy determination
- **Unicode Support**: Proper handling of multilingual content

## Algorithm Overview

1. **Text Extraction**: Uses PyMuPDF to extract text with font metadata
2. **Font Analysis**: Calculates font size distributions and ratios
3. **Heading Detection**: Identifies headings based on size ratios and layout
4. **Hierarchy Assignment**: Assigns H1/H2/H3 levels based on size and position
5. **Title Extraction**: Identifies document title from first page content
6. **JSON Generation**: Formats output according to challenge specifications

## Project Structure

```
adobe-1a/
├── Dockerfile                   # AMD64 optimized container
├── main.py                     # Entry point for Docker container
├── requirements.txt            # Minimal dependencies
├── setup.py                    # Package configuration
├── pyproject.toml             # Modern Python packaging
├── README.md                  # This file
└── src/
    └── pdf_outline_extractor/
        ├── __init__.py
        ├── extractor_new.py   # Core extraction logic
        ├── json_writer_new.py # JSON output formatting
        ├── layout_utils_new.py # Layout analysis utilities
        └── cli_hackathon.py   # CLI interface
```

## Local Development

### Prerequisites
- Python 3.10+
- Docker

### Installation
```bash
git clone <repository-url>
cd adobe-1a
pip install -r requirements.txt
pip install -e .
```

### Local Testing
```bash
# Create directories and add PDFs
mkdir -p input output
cp your_files.pdf input/

# Run locally (without Docker)
python main.py

# Or test with Docker
docker build -t pdf-extractor .
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-extractor
```

## Scoring Criteria Alignment

- **Heading Detection Accuracy**: Advanced font analysis and layout heuristics
- **Performance**: Optimized for speed with minimal dependencies
- **Size Compliance**: No ML models, pure Python implementation
- **Network Independence**: Completely offline operation

This project is developed for the Adobe Hackathon Round 1A challenge.
