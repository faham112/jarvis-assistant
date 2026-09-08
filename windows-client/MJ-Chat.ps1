$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$cfg = Join-Path $here "config.txt"
if (-not (Test-Path $cfg)) { Write-Host "Pehle Setup-MJ.bat"; exit 1 }
$lines = Get-Content $cfg | Where-Object { $_.Trim() -ne "" }
$base = $lines[0].Trim().TrimEnd("/")
$key = if ($lines.Count -gt 1) { $lines[1].Trim() } else { "" }
$hdr = @{ "X-API-Key" = $key }
Write-Host "MJ -> $base"
try {
  $a = Invoke-RestMethod -Uri "$base/activate" -Headers $hdr -TimeoutSec 10
  Write-Host ("ACTIVATED ollama=" + $a.ollama + " " + $a.message)
} catch { Write-Host ("Activate fail: " + $_.Exception.Message) }
while ($true) {
  $t = Read-Host "Tum"
  if (-not $t) { continue }
  if ($t -match "^(quit|exit|band)$") { break }
  try {
    $r = Invoke-RestMethod -Method Post -Uri "$base/chat" -Headers $hdr -ContentType "application/json" -Body ((@{text=$t}|ConvertTo-Json)) -TimeoutSec 120
    Write-Host ("MJ: " + $r.reply)
  } catch { Write-Host $_.Exception.Message }
}
