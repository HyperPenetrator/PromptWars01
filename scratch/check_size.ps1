$total = 0
Get-ChildItem -Path . -Recurse | Where-Object { $_.FullName -notmatch "\\\.venv\\" -and $_.FullName -notmatch "\\\.git\\" } | ForEach-Object { 
    if (!$_.PSIsContainer) { 
        $total += $_.Length 
    } 
}
Write-Host "Total Size: $($total / 1MB) MB"
