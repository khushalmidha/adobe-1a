#!/bin/bash
# Docker Test Script for PDF Outline Extractor
# Optimized for smooth AMD64 operation

echo "=== Adobe Hackathon PDF Extractor Docker Test (AMD64) ==="
echo "🖥️  Target Architecture: AMD64"
echo ""

# Check if Docker is available
echo "🔍 Checking Docker availability..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "   Please install Docker Desktop for your operating system"
    exit 1
fi

# Check if Docker daemon is running
echo "🔍 Checking Docker daemon..."
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker Desktop."
    echo "   On Windows/Mac: Start Docker Desktop application"
    echo "   On Linux: sudo systemctl start docker"
    exit 1
fi

echo "✅ Docker is available and running"

# Check Docker version and architecture support
echo "🔍 Checking Docker architecture support..."
docker_version=$(docker version --format '{{.Server.Version}}' 2>/dev/null)
echo "📦 Docker version: $docker_version"

# Verify AMD64 platform support
if docker buildx version &> /dev/null; then
    echo "✅ Docker Buildx available (multi-platform support)"
else
    echo "⚠️  Docker Buildx not available, using standard build"
fi

# Build the Docker image with explicit AMD64 platform
echo ""
echo "🔨 Building Docker image for AMD64..."
echo "   This may take a few minutes on first build..."
if docker build --platform linux/amd64 -t pdf-extractor . 2>&1 | tee build.log; then
    echo "✅ Docker image built successfully for AMD64"
    # Check image size
    image_size=$(docker images pdf-extractor:latest --format "{{.Size}}")
    echo "📦 Image size: $image_size"
else
    echo "❌ Failed to build Docker image"
    echo "   Check build.log for details"
    exit 1
fi

# Create test directories
echo ""
echo "📁 Creating test directories..."
mkdir -p test_docker_input test_docker_output

# Copy test PDFs to input directory
echo "📄 Copying test PDFs..."
if [ -d "pdfs" ] && [ "$(ls -A pdfs/*.pdf 2>/dev/null)" ]; then
    cp pdfs/*.pdf test_docker_input/
    pdf_count=$(ls test_docker_input/*.pdf 2>/dev/null | wc -l)
    echo "   Copied $pdf_count PDF files"
else
    echo "❌ No PDF files found in pdfs/ directory"
    echo "   Please ensure PDF files are available for testing"
    exit 1
fi

# Test Docker container health
echo ""
echo "🏥 Testing container health..."
if docker run --rm --platform linux/amd64 pdf-extractor python -c "import pdf_outline_extractor; print('✅ All imports successful')"; then
    echo "✅ Container health check passed"
else
    echo "❌ Container health check failed"
    exit 1
fi

# Run the Docker container
echo ""
echo "🐳 Running Docker container for PDF processing..."
echo "   Processing $pdf_count PDF files..."
start_time=$(date +%s)

if docker run --rm \
    --platform linux/amd64 \
    -v "$(pwd)/test_docker_input:/app/input:ro" \
    -v "$(pwd)/test_docker_output:/app/output:rw" \
    pdf-extractor; then
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    echo "✅ Docker container ran successfully in ${duration}s"
else
    echo "❌ Docker container failed to run"
    echo "   Check container logs for details"
    exit 1
fi

# Check output files
echo "🔍 Checking output files..."
output_count=$(ls test_docker_output/*.json 2>/dev/null | wc -l)
if [ "$output_count" -eq 5 ]; then
    echo "✅ All 5 JSON files generated successfully"
    
    # Check file sizes
    for file in test_docker_output/*.json; do
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
        if [ "$size" -gt 50 ]; then
            echo "✅ $(basename "$file"): $size bytes"
        else
            echo "⚠️  $(basename "$file"): $size bytes (might be empty)"
        fi
    done
else
    echo "❌ Expected 5 JSON files, found $output_count"
    ls -la test_docker_output/
    exit 1
fi

echo ""
echo "🎉 Docker test completed successfully!"
echo "📊 Results saved in test_docker_output/"
echo ""
echo "To clean up test directories, run:"
echo "rm -rf test_docker_input test_docker_output"
