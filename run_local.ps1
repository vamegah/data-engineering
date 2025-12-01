# Run Portfolio APIs Locally Without Docker
Write-Host ""
Write-Host "Data Engineering Portfolio - Local Deployment" -ForegroundColor Cyan
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
    Write-Host "Python is not installed!" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check dependencies
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$hasDeps = $false
try {
    python -c "import fastapi" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $hasDeps = $true
        Write-Host "Dependencies are installed" -ForegroundColor Green
    }
} catch {
    $hasDeps = $false
}

if (-not $hasDeps) {
    Write-Host "Dependencies not installed. Installing now..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "Failed to install dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Starting APIs" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will open 6 PowerShell windows, one for each API." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Fraud Detection:  http://localhost:8001/docs" -ForegroundColor White
Write-Host "  E-commerce:       http://localhost:8002/docs" -ForegroundColor White
Write-Host "  Financial:        http://localhost:8003/docs" -ForegroundColor White
Write-Host "  Healthcare:       http://localhost:8004/docs" -ForegroundColor White
Write-Host "  HR Analytics:     http://localhost:8005/docs" -ForegroundColor White
Write-Host "  Restaurant:       http://localhost:8006/docs" -ForegroundColor White
Write-Host ""

$continue = Read-Host "Continue? (Y/N)"
if ($continue -ne "Y" -and $continue -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

$currentDir = Get-Location

function Start-API {
    param (
        [string]$Name,
        [string]$Path,
        [int]$Port
    )
    $command = "cd '$currentDir\$Path'; python -m uvicorn api.app:app --host 0.0.0.0 --port $Port; Read-Host 'Press Enter to close'"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $command -WindowStyle Normal
    Write-Host "Started $Name API on port $Port" -ForegroundColor Green
    Start-Sleep -Seconds 1
}

Write-Host ""
Write-Host "Starting APIs..." -ForegroundColor Yellow
Write-Host ""

Start-API -Name "Fraud Detection" -Path "fraud" -Port 8001
Start-API -Name "E-commerce" -Path "ecommerce" -Port 8002
Start-API -Name "Financial" -Path "financial" -Port 8003
Start-API -Name "Healthcare" -Path "healthcare" -Port 8004
Start-API -Name "HR Analytics" -Path "hr" -Port 8005
Start-API -Name "Restaurant" -Path "restaurant" -Port 8006

Write-Host ""
Write-Host "All APIs Started!" -ForegroundColor Green
Write-Host ""
Write-Host "Access them at:" -ForegroundColor Green
Write-Host "  http://localhost:8001/docs - Fraud Detection" -ForegroundColor Cyan
Write-Host "  http://localhost:8002/docs - E-commerce" -ForegroundColor Cyan
Write-Host "  http://localhost:8003/docs - Financial" -ForegroundColor Cyan
Write-Host "  http://localhost:8004/docs - Healthcare" -ForegroundColor Cyan
Write-Host "  http://localhost:8005/docs - HR Analytics" -ForegroundColor Cyan
Write-Host "  http://localhost:8006/docs - Restaurant" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop all APIs, close all PowerShell windows." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to close this window"
