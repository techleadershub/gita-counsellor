$ErrorActionPreference = "Stop"

$workspacePath = $PSScriptRoot
$backendPath = Join-Path $workspacePath "backend"
$frontendPath = Join-Path $workspacePath "frontend"

Write-Host "=== Starting Bhagavad Gita Research Agent ===" -ForegroundColor Green
Write-Host ""

# Check if directories exist
if (-not (Test-Path $backendPath)) {
    Write-Host "ERROR: Backend directory not found at $backendPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $frontendPath)) {
    Write-Host "ERROR: Frontend directory not found at $frontendPath" -ForegroundColor Red
    exit 1
}

# Start Backend
Write-Host "Starting Backend on http://localhost:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; Write-Host '=== Backend Service ===' -ForegroundColor Green; python -m uvicorn main:app --reload --port 8000"

Start-Sleep -Seconds 2

# Start Frontend
Write-Host "Starting Frontend on http://localhost:3000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; Write-Host '=== Frontend Service ===' -ForegroundColor Green; npm run dev"

Write-Host ""
Write-Host "Services are starting in separate windows..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: It may take 10-30 seconds for services to fully start." -ForegroundColor Gray
Write-Host "Check the PowerShell windows for any errors." -ForegroundColor Gray

