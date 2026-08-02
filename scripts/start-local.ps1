$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

& .\.venv\Scripts\pip install -r backend\requirements-core.txt
Copy-Item .env backend\.env -Force

Push-Location backend
Start-Process -FilePath "..\.venv\Scripts\uvicorn.exe" -ArgumentList "main:app","--host","0.0.0.0","--port","8000","--reload" -WindowStyle Minimized
Pop-Location

Push-Location frontend
if (-not (Test-Path "node_modules")) { npm install }
Start-Process -FilePath "npm" -ArgumentList "run","dev" -WindowStyle Minimized
Pop-Location

Write-Host "Backend:  http://localhost:8000/docs"
Write-Host "Frontend: http://localhost:8911"
Write-Host "Demo login: patient@example.com / Patient@12345"
