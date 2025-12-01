# Quick Test - Run One API Locally
# Tests that everything works without Docker

Write-Host "`n🚀 Testing Fraud Detection API..." -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Install from https://www.python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "`n📦 Installing dependencies..." -ForegroundColor Yellow
pip install fastapi uvicorn pandas scikit-learn python-multipart -q

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "⚠ Some dependencies may have failed" -ForegroundColor Yellow
}

# Start Fraud API
Write-Host "`n🎯 Starting Fraud Detection API..." -ForegroundColor Cyan
Write-Host ""
Write-Host "API will be available at: " -NoNewline
Write-Host "http://localhost:8001/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

Set-Location fraud
python -m uvicorn api.app:app --host 0.0.0.0 --port 8001
