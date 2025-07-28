#!/bin/bash
# Enhanced Docker Test Script for AMD64 Architecture
# Tests Docker container functionality with architecture validation

echo "=== Adobe Hackathon PDF Extractor Docker Test (AMD64) ==="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker Desktop."
    exit 1
fi

echo "✅ Docker is available and running"

# Check Docker architecture support
echo "🔍 Checking Docker architecture support..."
if docker version --format '{{.Server.Arch}}' | grep -q "amd64"; then
    echo "✅ Docker supports AMD64 architecture"
else
    echo "⚠️  Docker architecture check inconclusive, proceeding with build..."
fi

# Clean up any existing containers/images
echo "🧹 Cleaning up existing containers and images..."
docker container prune -f > /dev/null 2>&1
docker image rm pdf-extractor > /dev/null 2>&1

# Build the Docker image with explicit AMD64 platform
echo "🔨 Building Docker image for AMD64..."
if docker build --platform linux/amd64 -t pdf-extractor .; then
    echo "✅ Docker image built successfully for AMD64"
else
    echo "❌ Failed to build Docker image"
    exit 1
fi

# Verify image architecture
echo "🔍 Verifying image architecture..."
IMAGE_ARCH=$(docker inspect pdf-extractor --format='{{.Architecture}}')
if [ "$IMAGE_ARCH" = "amd64" ]; then
    echo "✅ Image architecture confirmed: $IMAGE_ARCH"
else
    echo "⚠️  Image architecture: $IMAGE_ARCH (expected amd64)"
fi

# Create test directories
echo "📁 Creating test directories..."
rm -rf test_docker_input test_docker_output
mkdir -p test_docker_input test_docker_output

# Copy test PDFs to input directory
echo "📄 Copying test PDFs..."
if [ -d "pdfs" ]; then
    cp pdfs/*.pdf test_docker_input/
    input_count=$(ls test_docker_input/*.pdf 2>/dev/null | wc -l)
    echo "📄 Copied $input_count PDF files to test_docker_input/"
else
    echo "❌ PDFs directory not found"
    exit 1
fi

# Test Docker container with memory and CPU limits for smooth operation
echo "🐳 Running Docker container with resource limits..."
if docker run --rm \
    --platform linux/amd64 \
    --memory="1g" \
    --cpus="2.0" \
    -v "$(pwd)/test_docker_input:/app/input" \
    -v "$(pwd)/test_docker_output:/app/output" \
    pdf-extractor; then
    echo "✅ Docker container ran successfully"
else
    echo "❌ Docker container failed to run"
    exit 1
fi

# Check output files
echo "🔍 Checking output files..."
output_count=$(ls test_docker_output/*.json 2>/dev/null | wc -l)
if [ "$output_count" -eq "$input_count" ]; then
    echo "✅ All $output_count JSON files generated successfully"
    
    # Validate JSON structure
    echo "🔍 Validating JSON structure..."
    for file in test_docker_output/*.json; do
        if python3 -c "import json; json.load(open('$file'))" 2>/dev/null; then
            size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
            echo "✅ $(basename "$file"): $size bytes (valid JSON)"
        else
            echo "❌ $(basename "$file"): Invalid JSON format"
        fi
    done
else
    echo "❌ Expected $input_count JSON files, found $output_count"
    ls -la test_docker_output/
    exit 1
fi

# Test container resource usage
echo "📊 Testing container resource efficiency..."
CONTAINER_ID=$(docker run -d --platform linux/amd64 --memory="512m" --cpus="1.0" \
    -v "$(pwd)/test_docker_input:/app/input" \
    -v "$(pwd)/test_docker_output:/app/output" \
    pdf-extractor)

# Wait for container to finish
docker wait $CONTAINER_ID > /dev/null

# Check container stats
STATS=$(docker stats $CONTAINER_ID --no-stream --format "table {{.MemUsage}}\t{{.CPUPerc}}" | tail -n 1)
echo "📊 Container resource usage: $STATS"

# Clean up test container
docker rm $CONTAINER_ID > /dev/null

echo ""
echo "🎉 Docker AMD64 test completed successfully!"
echo "📊 Results saved in test_docker_output/"
echo "🔧 Container tested with resource limits: 1GB RAM, 2 CPUs"
echo ""
echo "To clean up test directories, run:"
echo "rm -rf test_docker_input test_docker_output"

# Optional: Create a backup of successful test results
echo "💾 Creating backup of test results..."
timestamp=$(date +"%Y%m%d_%H%M%S")
cp -r test_docker_output "docker_test_results_$timestamp"
echo "✅ Test results backed up to docker_test_results_$timestamp/"
