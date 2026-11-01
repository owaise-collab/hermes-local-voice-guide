param(
    [string]$LlamaServer = 'C:\AI\llama.cpp\llama-server.exe',
    [string]$ModelPath = '',
    [string]$HermesHome = '',
    [string]$ModelAlias = 'local-hermes',
    [int]$Port = 8080,
    [int]$ContextSize = 65536,
    [int]$GpuLayers = 99
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Common.ps1')
if (-not $HermesHome) { $HermesHome = $env:HERMES_HOME }
if (-not $HermesHome) { $HermesHome = Join-Path $env:LOCALAPPDATA 'hermes' }
if (-not $ModelPath) { $ModelPath = Join-Path $HermesHome 'models\Agents-A1-4B-Q8_0.gguf' }
if ($ContextSize -lt 64000) { throw 'The tested Hermes version requires at least 64,000 context tokens.' }
$endpoint = Get-LocalEndpoint -Port $Port
$LlamaServer = (Resolve-Path -LiteralPath $LlamaServer).Path
$ModelPath = (Resolve-Path -LiteralPath $ModelPath).Path
$health = $null
try { $health = Invoke-RestMethod "$endpoint/health" -TimeoutSec 2 } catch { }
if ($health.status -eq 'ok') {
    $props = Invoke-RestMethod "$endpoint/props" -TimeoutSec 3
    if ($props.model_path -ne $ModelPath -or $props.model_alias -ne $ModelAlias) {
        throw 'This port is already serving a different model or alias. Choose another port or stop its owner.'
    }
    if ($props.default_generation_settings.n_ctx -lt 64000) { throw 'Running server context is below 64K; restart it with a larger window.' }
    Write-Host "Local server is ready at $endpoint/v1."
    return
}
$logDir = Join-Path $HermesHome 'logs'
$runDir = Join-Path $HermesHome 'runtime'
New-Item -ItemType Directory -Path $logDir,$runDir -Force | Out-Null
$serverArguments = @('-m', ('"' + $ModelPath + '"'), '--alias', $ModelAlias,
    '--host', '127.0.0.1', '--port', [string]$Port, '--jinja',
    '--ctx-size', [string]$ContextSize, '--parallel', '1', '--gpu-layers', [string]$GpuLayers,
    '--reasoning', 'off', '--temp', '0.85', '--top-p', '0.95', '--top-k', '20', '--min-p', '0.0')
$server = Start-Process -FilePath $LlamaServer -ArgumentList $serverArguments -WorkingDirectory (Split-Path $LlamaServer) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $logDir "llama-guide-$Port.stdout.log") -RedirectStandardError (Join-Path $logDir "llama-guide-$Port.stderr.log")
$record = @{ pid=$server.Id; executable=$LlamaServer; model=$ModelPath; started=$server.StartTime.ToUniversalTime().ToString('o') }
$record | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runDir "llama-guide-$Port.json") -Encoding UTF8
Write-Host "Loading the local model (PID $($server.Id))..."
$deadline = (Get-Date).AddMinutes(3)
while ((Get-Date) -lt $deadline) {
    $server.Refresh()
    if ($server.HasExited) { throw "Server exited. Read $logDir\llama-guide-$Port.stderr.log" }
    $health = $null
    try { $health = Invoke-RestMethod "$endpoint/health" -TimeoutSec 2 } catch { }
    if ($health.status -eq 'ok') {
        $props = Invoke-RestMethod "$endpoint/props" -TimeoutSec 3
        if ($props.default_generation_settings.n_ctx -lt 64000) { throw 'Model capped context below 64K. Select a model with a sufficient native window.' }
        Write-Host "Ready: $endpoint/v1, $($props.default_generation_settings.n_ctx) tokens."
        return
    }
    Start-Sleep -Seconds 2
}
throw "Startup timed out. Inspect the server logs in $logDir. CPU-only loading may need more time."
