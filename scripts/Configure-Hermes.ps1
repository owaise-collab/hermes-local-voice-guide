param(
    [string]$HermesHome = '',
    [string]$HermesSource = '',
    [string]$ModelAlias = 'local-hermes',
    [int]$Port = 8080,
    [int]$ContextSize = 65536,
    [switch]$SkipDependencies,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Common.ps1')
$context = Get-HermesContext -HermesHome $HermesHome -HermesSource $HermesSource
$endpoint = (Get-LocalEndpoint -Port $Port) + '/v1'
$priorHome = $env:HERMES_HOME
try {
    $env:HERMES_HOME = $context.Home
    if (-not $DryRun -and -not $SkipDependencies) {
        & $context.Command pm install --extra voice --extra piper
        if ($LASTEXITCODE -ne 0) { throw 'Voice dependency installation failed; configuration was not changed.' }
    }
    $parameters = @('--hermes-home', $context.Home, '--base-url', $endpoint,
        '--model', $ModelAlias, '--context', [string]$ContextSize)
    if ($DryRun) { $parameters += '--dry-run' }
    & (Join-Path $PSScriptRoot 'Invoke-HermesPython.ps1') -Script (Join-Path $PSScriptRoot 'configure.py') -ScriptArgs $parameters -HermesHome $context.Home -HermesSource $context.Source
    if (-not $DryRun) { Write-Host 'Configuration saved. Start the local server, then restart Hermes before testing.' }
} finally { $env:HERMES_HOME = $priorHome }
