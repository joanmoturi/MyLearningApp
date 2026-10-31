param([Parameter(Mandatory=$true)][string]$Snapshot, [string]$Origin = "http://127.0.0.1:3000", [switch]$Confirm)
$ErrorActionPreference = "Stop"
if (-not $Confirm) { throw "Restore replaces current data. Back up first, then explicitly pass -Confirm." }
$file = Get-Item -LiteralPath $Snapshot
if ($file.Length -gt 64MB) { throw "Snapshot exceeds 64 MB." }
Invoke-RestMethod "$Origin/api/data/restore" -Method Post -Headers @{
    "X-Academy-Client" = "local-workspace"
    "X-Academy-Confirm" = "restore"
} -ContentType "application/octet-stream" -InFile $file.FullName
