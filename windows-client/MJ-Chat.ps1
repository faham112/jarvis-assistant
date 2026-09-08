$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$lines = Get-Content (Join-Path $here "config.txt") | Where-Object { $_.Trim() -ne "" }
$base = $lines[0].Trim().TrimEnd("/")
$key = if ($lines.Count -gt 1) { $lines[1].Trim() } else { "change-me" }
Write-Host "MJ -> $base"
try {
  $h = Invoke-RestMethod -Uri "$base/health" -Headers @{ "X-API-Key" = $key } -TimeoutSec 8
  Write-Host ("OK ollama=" + $h.ollama)
} catch { Write-Host "API band. VPS pe uvicorn :8080" }
while ($true) {
  $t = Read-Host "Tum"
  if ($t -match "^(quit|exit|band)$") { break }
  if (-not $t) { continue }
  try {
    $r = Invoke-RestMethod -Method Post -Uri "$base/chat" -Headers @{ "X-API-Key" = $key } -ContentType "application/json" -Body ((@{text=$t} | ConvertTo-Json)) -TimeoutSec 120
    Write-Host ("MJ: " + $r.reply)
  } catch { Write-Host $_.Exception.Message }
}
