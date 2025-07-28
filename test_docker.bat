@echo off
REM Docker Test Script for PDF Outline Extractor (Windows AMD64)
REM Optimized for smooth AMD64 operation

echo === Adobe Hackathon PDF Extractor Docker Test (AMD64) ===
echo 🖥️  Target Architecture: AMD64
echo.

REM Check if Docker is available
echo 🔍 Checking Docker availability...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed or not in PATH
    echo    Please install Docker Desktop for Windows
    exit /b 1
)

REM Check if Docker daemon is running
echo 🔍 Checking Docker daemon...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker daemon is not running. Please start Docker Desktop.
    echo    Start Docker Desktop application from Windows
    exit /b 1
)

echo ✅ Docker is available and running

REM Check Docker version
echo 🔍 Checking Docker version...
for /f "tokens=3" %%i in ('docker version --format "{{.Server.Version}}" 2^>nul') do set docker_version=%%i
echo 📦 Docker version: %docker_version%

REM Build the Docker image with explicit AMD64 platform
echo.
echo 🔨 Building Docker image for AMD64...
echo    This may take a few minutes on first build...
docker build --platform linux/amd64 -t pdf-extractor . > build.log 2>&1
if errorlevel 1 (
    echo ❌ Failed to build Docker image
    echo    Check build.log for details
    exit /b 1
)
echo ✅ Docker image built successfully for AMD64

REM Check image size
for /f "tokens=*" %%i in ('docker images pdf-extractor:latest --format "{{.Size}}"') do set image_size=%%i
echo 📦 Image size: %image_size%

REM Create test directories
echo.
echo 📁 Creating test directories...
if not exist test_docker_input mkdir test_docker_input
if not exist test_docker_output mkdir test_docker_output

REM Copy test PDFs to input directory
echo 📄 Copying test PDFs...
if exist pdfs\*.pdf (
    copy pdfs\*.pdf test_docker_input\ >nul
    for /f %%i in ('dir /b test_docker_input\*.pdf 2^>nul ^| find /c /v ""') do set pdf_count=%%i
    echo    Copied %pdf_count% PDF files
) else (
    echo ❌ No PDF files found in pdfs\ directory
    echo    Please ensure PDF files are available for testing
    exit /b 1
)

REM Test Docker container health
echo.
echo 🏥 Testing container health...
docker run --rm --platform linux/amd64 pdf-extractor python -c "import pdf_outline_extractor; print('✅ All imports successful')" >nul 2>&1
if errorlevel 1 (
    echo ❌ Container health check failed
    exit /b 1
)
echo ✅ Container health check passed

REM Run the Docker container
echo.
echo 🐳 Running Docker container for PDF processing...
echo    Processing %pdf_count% PDF files...
docker run --rm --platform linux/amd64 -v "%cd%\test_docker_input:/app/input:ro" -v "%cd%\test_docker_output:/app/output:rw" pdf-extractor
if errorlevel 1 (
    echo ❌ Docker container failed to run
    echo    Check container logs for details
    exit /b 1
)
echo ✅ Docker container ran successfully

REM Check output files
echo 🔍 Checking output files...
set /a output_count=0
for %%f in (test_docker_output\*.json) do set /a output_count+=1

if %output_count%==5 (
    echo ✅ All 5 JSON files generated successfully
    
    REM Check file sizes
    for %%f in (test_docker_output\*.json) do (
        for %%a in ("%%f") do (
            if %%~za GTR 50 (
                echo ✅ %%~nxa: %%~za bytes
            ) else (
                echo ⚠️  %%~nxa: %%~za bytes ^(might be empty^)
            )
        )
    )
) else (
    echo ❌ Expected 5 JSON files, found %output_count%
    dir test_docker_output\
    exit /b 1
)

echo.
echo 🎉 Docker test completed successfully!
echo 📊 Results saved in test_docker_output\
echo.
echo To clean up test directories, run:
echo rmdir /s /q test_docker_input test_docker_output
