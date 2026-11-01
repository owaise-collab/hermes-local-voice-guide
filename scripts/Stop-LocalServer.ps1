param([string]$HermesHome = '', [int]$Port = 8080)
$ErrorActionPreference = 'Stop'
if (-not $HermesHome) { $HermesHome = $env:HERMES_HOME }
if (-not $HermesHome) { $HermesHome = Join-Path $env:LOCALAPPDATA 'hermes' }
$recordPath = Join-Path $HermesHome "runtime\llama-guide-$Port.json"
if (-not (Test-Path -LiteralPath $recordPath)) { throw 'No guide-owned process record. This script will not stop another server.' }
$record = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
$server = Get-Process -Id ([int]$record.pid) -ErrorAction SilentlyContinue
if ($server) {
    if ($server.Path -ne $record.executable -or $server.StartTime.ToUniversalTime().ToString('o') -ne $record.started) {
        throw 'Process identity changed; refusing to stop a reused PID.'
    }
    Stop-Process -Id $server.Id
}
Remove-Item -LiteralPath $recordPath
Write-Host 'Guide-owned local server stopped.'
