# TRUSTLENS AI - Master Local Development Runner
# Launches the FastAPI backend (port 8000) and Next.js frontend (port 3000)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   TRUSTLENS AI - Launching Full-Stack Security Platform    " -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

$root = $PSScriptRoot

# 1. Start Backend in a separate window
Write-Host "`n[1/2] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
$backendCmd = "cd '$root'; .\.venv\Scripts\activate; python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -Title "TRUSTLENS AI - FastAPI Backend"

Start-Sleep -Seconds 3

# 2. Start Frontend in a separate window
Write-Host "[2/2] Starting Next.js Frontend on http://localhost:3000..." -ForegroundColor Yellow
$frontendCmd = "cd '$root\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd -Title "TRUSTLENS AI - Next.js Frontend"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host " TRUSTLENS AI is starting up!" -ForegroundColor Green
Write-Host " - Frontend UI:     http://localhost:3000" -ForegroundColor White
Write-Host " - API Docs:        http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host " - API Health:      http://127.0.0.1:8000/api/v1/health" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan

