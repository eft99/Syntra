# Syntra API — yerel gelistirme
# WinError 10013: Port 8000 baskasi tarafindan kullaniliyorsa asagidaki Port'u 8080 yapin.
# OneDrive altinda --reload sorun cikarirsa --reload-dir app kullanilir (asagida).

Set-Location $PSScriptRoot
$Port = if ($env:PORT) { [int]$env:PORT } else { 8000 }

python -m uvicorn app.main:app `
  --host 127.0.0.1 `
  --port $Port `
  --reload `
  --reload-dir app
