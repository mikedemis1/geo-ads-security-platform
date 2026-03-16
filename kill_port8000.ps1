$conns = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
foreach ($c in $conns) {
    $pid = $c.OwningProcess
    Write-Host "PID=$pid State=$($c.State)"
    try {
        $proc = Get-Process -Id $pid -ErrorAction Stop
        Write-Host "Process: $($proc.Name) - $($proc.Path)"
        Stop-Process -Id $pid -Force
        Write-Host "Killed PID $pid"
    } catch {
        Write-Host "Could not get/kill PID $pid (may need elevated permissions)"
    }
}
Write-Host "Done. Remaining on :8000:"
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object OwningProcess,State
