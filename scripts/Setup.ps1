$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
    if ($LASTEXITCODE) { throw "Python virtual environment creation failed." }
}
& ".venv\Scripts\python.exe" -m pip install --quiet -r backend\requirements.lock
if ($LASTEXITCODE) { throw "Backend dependency installation failed." }
& ".venv\Scripts\python.exe" -m pip install --quiet --no-deps -e backend
if ($LASTEXITCODE) { throw "Backend package installation failed." }
Push-Location frontend
try {
    npm ci --no-fund --no-audit
    if ($LASTEXITCODE) { throw "Frontend dependency installation failed." }
    npm run build
    if ($LASTEXITCODE) { throw "Frontend build failed." }
} finally { Pop-Location }
Write-Output "Dependencies and production frontend installed. Start backend and frontend in separate terminals."
