$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
if (Test-Path "$root\.env") {
    foreach ($line in Get-Content "$root\.env") {
        if ($line -match '^(APP_ORIGIN|BACKEND_URL)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2].Trim().Trim('"'), "Process")
        }
    }
}
$origin = if ($env:APP_ORIGIN) { [uri]$env:APP_ORIGIN } else { [uri]"http://127.0.0.1:3000" }
if ($origin.Host -notin @("127.0.0.1", "localhost")) { throw "Use a loopback APP_ORIGIN for this unauthenticated local workspace." }
Set-Location "$root\frontend"
npm run start -- --port $origin.Port
if ($LASTEXITCODE) { throw "Frontend stopped with an error." }
