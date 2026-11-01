param(
    [string]$HermesHome = '',
    [string]$HermesSource = '',
    [string]$LlamaServer = 'C:\AI\llama.cpp\llama-server.exe',
    [string]$ModelPath = '',
    [string]$ModelAlias = 'local-hermes',
    [int]$Port = 8080,
    [int]$ContextSize = 65536,
    [int]$GpuLayers = 99,
    [string[]]$ChatArgs = @()
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Common.ps1')
$context = Get-HermesContext -HermesHome $HermesHome -HermesSource $HermesSource
& (Join-Path $PSScriptRoot 'Start-LocalServer.ps1') -HermesHome $context.Home -LlamaServer $LlamaServer -ModelPath $ModelPath -ModelAlias $ModelAlias -Port $Port -ContextSize $ContextSize -GpuLayers $GpuLayers
$priorHome = $env:HERMES_HOME
try {
    $env:HERMES_HOME = $context.Home
    & $context.Command chat --cli @ChatArgs
    if ($LASTEXITCODE -ne 0) { throw "Hermes exited with code $LASTEXITCODE." }
} finally { $env:HERMES_HOME = $priorHome }
