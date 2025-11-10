# Setup script for Python virtual environments (Windows PowerShell)
# Course des Impressionnistes Registration System

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setting up Python virtual environments" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion"

# Setup backend virtual environment
Write-Host ""
Write-Host "Setting up backend virtual environment..." -ForegroundColor Yellow
Set-Location backend

if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Created backend/venv" -ForegroundColor Green
} else {
    Write-Host "✓ backend/venv already exists" -ForegroundColor Green
}

# Activate and install dependencies
& .\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
deactivate
Write-Host "✓ Installed backend dependencies" -ForegroundColor Green

# Setup infrastructure virtual environment
Write-Host ""
Write-Host "Setting up infrastructure virtual environment..." -ForegroundColor Yellow
Set-Location ..\infrastructure

if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Created infrastructure/venv" -ForegroundColor Green
} else {
    Write-Host "✓ infrastructure/venv already exists" -ForegroundColor Green
}

# Activate and install dependencies
& .\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
deactivate
Write-Host "✓ Installed infrastructure dependencies" -ForegroundColor Green

Set-Location ..

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To activate virtual environments:"
Write-Host "  Backend:        cd backend; .\venv\Scripts\Activate.ps1"
Write-Host "  Infrastructure: cd infrastructure; .\venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "To deactivate: deactivate"
Write-Host ""
