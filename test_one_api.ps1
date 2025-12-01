# Quick Test - Run One API Locally
Write-Host ""
Write-Host "Testing Fraud Detection API..." -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python") {
        Write-Host "Python is installed: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "Python not found. Install from https://www.python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install fastapi uvicorn pandas scikit-learn python-multipart -q

if ($LASTEXITCODE -eq 0) {
    Write-Host "Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "Some dependencies may have failed" -ForegroundColor Yellow
}

# Start Fraud API
Write-Host ""
Write-Host "Starting Fraud Detection API..." -ForegroundColor Cyan
Write-Host ""
Write-Host "API will be available at: http://localhost:8001/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

Set-Location fraud
python -m uvicorn api.app:app --host 0.0.0.0 --port 8001
