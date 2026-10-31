$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
Set-Location $root
& ".venv\Scripts\python.exe" -m uvicorn academy.main:app --host 127.0.0.1 --port 8000 --workers 1
if ($LASTEXITCODE) { throw "Backend stopped with an error." }
