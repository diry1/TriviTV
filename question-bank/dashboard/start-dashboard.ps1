$ErrorActionPreference = 'Stop'
$dashboardUrl = 'http://127.0.0.1:8791'
try { $dashboardReady = (Invoke-WebRequest "$dashboardUrl/api/meta" -UseBasicParsing -TimeoutSec 2).StatusCode -eq 200 } catch { $dashboardReady = $false }
if (-not $dashboardReady) {
    $dashboardPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (-not (Test-Path -LiteralPath $dashboardPython)) { $dashboardPython = (Get-Command python -ErrorAction Stop).Source }
    $dashboardScript = Join-Path $PSScriptRoot 'server.py'
    Start-Process -FilePath $dashboardPython -ArgumentList @('-X','utf8',('"' + $dashboardScript + '"')) -WindowStyle Hidden
    for ($dashboardAttempt=0; $dashboardAttempt -lt 30; $dashboardAttempt++) {
        Start-Sleep -Milliseconds 500
        try { if ((Invoke-WebRequest "$dashboardUrl/api/meta" -UseBasicParsing -TimeoutSec 1).StatusCode -eq 200) { $dashboardReady = $true; break } } catch {}
    }
    if (-not $dashboardReady) { throw 'Dashboard could not start on local port 8791.' }
}
Start-Process $dashboardUrl
