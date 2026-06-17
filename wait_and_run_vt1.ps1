$mainPid = 14488
$logFile = "$PSScriptRoot\import_log.txt"
$vt1Log  = "$PSScriptRoot\import_vt1_log.txt"

Write-Host "Gaidu kameer process $mainPid beidzas..."

# Gaida kamēr galvenais imports beidzas
while (Get-Process -Id $mainPid -ErrorAction SilentlyContinue) {
    Start-Sleep -Seconds 30
}

Write-Host "Galvenais imports beidzies. Saku VT1 importu..."
Add-Content $logFile "`n=== VT1 reimport sakts ==="

$env:PYTHONIOENCODING = 'utf-8'
& "$PSScriptRoot\venv\Scripts\python.exe" -u "$PSScriptRoot\xado_vt1_only.py" | Tee-Object -FilePath $vt1Log

Write-Host "VT1 imports beidzies. Skatiet: $vt1Log"
