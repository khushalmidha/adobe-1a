#!/bin/bash
# Docker Health Check Script for AMD64
# Quick validation of Docker setup

echo "🔍 Docker AMD64 Health Check"
echo "=========================="

# Check Docker installation
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
    docker --version
else
    echo "❌ Docker not found"
    exit 1
fi

# Check Docker daemon
if docker info &> /dev/null; then
    echo "✅ Docker daemon is running"
else
    echo "❌ Docker daemon not running"
    exit 1
fi

# Check platform support
if docker buildx version &> /dev/null; then
    echo "✅ Multi-platform support available"
    docker buildx ls | grep -E "linux/amd64|default"
else
    echo "⚠️  Using standard Docker build"
fi

# Test build capability
echo ""
echo "🧪 Testing AMD64 build capability..."
cat > test.Dockerfile << EOF
FROM --platform=linux/amd64 python:3.10-slim
RUN echo "AMD64 test successful"
EOF

if docker build --platform linux/amd64 -f test.Dockerfile -t test-amd64 . &> /dev/null; then
    echo "✅ AMD64 build test passed"
    docker rmi test-amd64 &> /dev/null
else
    echo "❌ AMD64 build test failed"
fi

rm -f test.Dockerfile

echo ""
echo "🎉 Health check complete!"
