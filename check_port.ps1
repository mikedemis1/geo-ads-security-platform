$listening = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($listening) {
    foreach ($c in $listening) {
        $procId = $c.OwningProcess
        Write-Host "LISTENING PID=$procId"
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) { Write-Host "Process: $($proc.Name) Path: $($proc.Path)" }
        else { Write-Host "Process not found" }
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        Write-Host "Killed"
    }
} else {
    Write-Host "Nothing listening on port 8000"
}
