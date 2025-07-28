# Adobe Hackathon Round 1A - PDF Outline Extractor
# Optimized for AMD64 architecture
FROM --platform=linux/amd64 python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for PyMuPDF on AMD64
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libc-dev \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies optimized for AMD64
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Copy source code
COPY src/ ./src/
COPY setup.py .
COPY pyproject.toml .
COPY README.md .

# Install the package
RUN pip install --no-cache-dir -e .

# Create input and output directories
RUN mkdir -p /app/input /app/output && \
    chmod 755 /app/input /app/output

# Set environment for optimal AMD64 performance
ENV PYTHONPATH="/app/src:$PYTHONPATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Health check for container validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import pdf_outline_extractor; print('OK')" || exit 1

# Default command - process PDFs from /app/input to /app/output
CMD ["python", "-m", "pdf_outline_extractor.cli_hackathon"]

# Metadata
LABEL maintainer="Adobe Hackathon Team"
LABEL description="PDF Outline Extractor for AMD64"
LABEL version="1.0.0"
LABEL architecture="amd64"
