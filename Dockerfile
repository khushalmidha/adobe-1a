# Adobe Hackathon Round 1A - PDF Outline Extractor
# Pure Python implementation, no ML models, AMD64 compatible
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PyMuPDF
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py .
COPY pyproject.toml .
COPY README.md .

# Install the package
RUN pip install -e .

# Create input and output directories
RUN mkdir -p /app/input /app/output /app/expected

# Set Python path and environment
ENV PYTHONPATH="/app/src:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1

# Default command - process PDFs from /app/input to /app/output
CMD ["python", "-m", "pdf_outline_extractor.cli_clean"]

# Labels for metadata
LABEL maintainer="Adobe Hackathon Team <team@example.com>"
LABEL description="PDF Outline Extractor - Extract structured outlines from PDF documents"
LABEL version="1.0.0"
LABEL architecture="amd64"
