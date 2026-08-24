# Wrapper PowerShell cho ./mo — nội dung thật nằm ở file `mo` (bash).
# Dùng: .\mo.ps1 verify
$ErrorActionPreference = 'Stop'
& bash "$PSScriptRoot/mo" @args
exit $LASTEXITCODE
