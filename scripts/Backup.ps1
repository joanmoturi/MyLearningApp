param([string]$Origin = "http://127.0.0.1:3000", [string]$Destination)
$ErrorActionPreference = "Stop"
if (-not $Destination) {
    $folder = Join-Path (Split-Path $PSScriptRoot -Parent) "backups"
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
    $Destination = Join-Path $folder ("academy-" + (Get-Date -Format "yyyyMMdd-HHmmss") + ".sqlite3")
}
Invoke-WebRequest "$Origin/api/data/backup" -OutFile $Destination
Write-Output "Snapshot saved to $Destination. Treat it as private learning data."
