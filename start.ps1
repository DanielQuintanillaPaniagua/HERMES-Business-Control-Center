# start.ps1
# Arranca el servidor HERMES de forma limpia:
# 1. Mata cualquier proceso viejo de Python que pueda estar ocupando el puerto
# 2. Activa el entorno virtual
# 3. Levanta el servidor Flask

Write-Host "Cerrando procesos de Python anteriores..." -ForegroundColor Yellow
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
& "$PSScriptRoot\venv\Scripts\Activate.ps1"

Write-Host "Abriendo navegador..." -ForegroundColor Yellow
Start-Process "http://127.0.0.1:5000"

Write-Host "Iniciando servidor Flask..." -ForegroundColor Green
python "$PSScriptRoot\run.py"