for ($i=1; $i -le 7; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000/auth/token" -Method POST -Headers @{"X-Admin-Secret"="CHANGE_ME_32BYTES_DEV_ONLY_000000"; "Content-Type"="application/json"} -Body '{"sub":"test","scopes":["ads:read"]}'
        Write-Host "#$i : $($r.StatusCode)"
    } catch {
        Write-Host "#$i : $($_.Exception.Response.StatusCode.value__)"
    }
}
