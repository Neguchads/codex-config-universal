# Atalho para PowerShell 5.1 ou superior.
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$tokens = $null
$parseErrors = $null
$null = [System.Management.Automation.Language.Parser]::ParseFile($PSCommandPath, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count -gt 0) { throw 'Sintaxe PowerShell invalida.' }
Push-Location -LiteralPath $root
try {
    python scripts/test.py
    $result = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $result
