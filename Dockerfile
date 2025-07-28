# Adobe Hackathon Round 1A - PDF Outline Extractor
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables early
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies (PyMuPDF has pre-built wheels, no compilation needed)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Copy source code and main script
COPY src/ ./src/
COPY main.py .
COPY setup.py .
COPY pyproject.toml .
COPY README.md .

# Install the package
RUN pip install --no-cache-dir -e .

# Create input and output directories
RUN mkdir -p /app/input /app/output && \
    chmod 755 /app/input /app/output

# Health check for container validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "from pdf_outline_extractor.extractor_new import PDFOutlineExtractor; print('OK')" || exit 1

# Default command - process PDFs from /app/input to /app/output
CMD ["python", "main.py"]
