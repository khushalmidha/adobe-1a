# Adobe Hackathon - PDF Outline Extractor

## AUTOMATED EVALUATION INSTRUCTIONS

### For Computer/Automated Systems:

**SINGLE COMMAND TO RUN:**

```bash
docker build -t pdf-extractor . && docker run --rm -v "$(pwd)/input:/app/input" -v "$(pwd)/output:/app/output" pdf-extractor
```

### Setup:
1. Ensure `input/` directory contains PDF files
2. The `output/` directory will be created automatically
3. JSON results will appear in `output/` directory

### What it does:
- Builds the Docker container with all dependencies
- Processes all PDF files from `input/` directory  
- Generates structured JSON outlines in `output/` directory
- Runs completely offline, no internet required

### Expected Output:
Each PDF file `input/filename.pdf` produces `output/filename.json` with structure:
```json
{
  "title": "Document Title",
  "outline": [
    {"level": "H1", "text": "Chapter 1", "page": 0},
    {"level": "H2", "text": "Section 1.1", "page": 1}
  ]
}
```

### Architecture: 
- AMD64 compatible
- Python 3.10 with PyMuPDF
- No ML models, pure algorithmic approach
- Memory efficient for large documents
