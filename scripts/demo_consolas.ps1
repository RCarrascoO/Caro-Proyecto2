# Script de demostración: Servidor Flask + Cliente Lazarus
# Muestra ambas consolas funcionando en modo consola
#
# USO: .\scripts\demo_consolas.ps1

param(
    [switch]$NoInstall,
    [string]$ClientId = "client1"
)

# Colores para output
function Write-Header { param($msg) Write-Host "`n╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan; Write-Host "║ $msg" -ForegroundColor Cyan; Write-Host "╚════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "→ $msg" -ForegroundColor Yellow }
function Write-Error { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }

Write-Header "DEMOSTRACIÓN: SERVIDOR Y CLIENTE EN MODO CONSOLA"

# Verificar entorno virtual
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Error "Entorno virtual no encontrado. Ejecuta primero: py -3 -m venv .venv"
    exit 1
}

# Activar entorno virtual
Write-Info "Activando entorno virtual..."
& .\.venv\Scripts\Activate.ps1

# Instalar dependencias si es necesario
if (-not $NoInstall) {
    Write-Info "Instalando dependencias..."
    pip install -q -r requirements.txt
    Write-Success "Dependencias instaladas"
}

# Verificar si existe el cliente Lazarus compilado
$lazarusClient = ".\tools\pas_client_send_data.exe"
$useLazarus = Test-Path $lazarusClient

if ($useLazarus) {
    Write-Success "Cliente Lazarus encontrado: $lazarusClient"
    $clientType = "Lazarus Pascal"
} else {
    Write-Info "Cliente Lazarus NO compilado, usando cliente Python"
    $clientType = "Python"
}

# Generar datos si no existen
if (-not (Test-Path "outputs\data.dat")) {
    Write-Info "Generando datos sintéticos..."
    python tools\generate_data_dat.py --output outputs\data.dat --records 100
    Write-Success "Datos generados: outputs\data.dat"
}

# Preparar para iniciar servidor
Write-Header "INICIANDO SERVIDOR FLASK (MODO CONSOLA)"
Write-Info "El servidor mostrará un banner y logs en tiempo real"
Write-Info "Presiona Ctrl+C en la ventana del servidor para detenerlo"
Write-Host ""

# Iniciar servidor en nueva ventana de PowerShell
$serverScript = @"
& '.\.venv\Scripts\Activate.ps1'
Write-Host '╔═══════════════════════════════════════════════════╗' -ForegroundColor Green
Write-Host '║  VENTANA DEL SERVIDOR - Observa los logs aquí    ║' -ForegroundColor Green
Write-Host '╚═══════════════════════════════════════════════════╝' -ForegroundColor Green
Write-Host ''
python src\http_server\app.py
"@

$serverScriptPath = ".\temp_server.ps1"
$serverScript | Out-File -FilePath $serverScriptPath -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-File", $serverScriptPath -PassThru | Out-Null
Write-Success "Servidor iniciado en nueva ventana"

# Esperar a que el servidor esté listo
Write-Info "Esperando a que el servidor esté listo..."
Start-Sleep -Seconds 5

# Ejecutar cliente en nueva ventana
Write-Header "INICIANDO CLIENTE $clientType (MODO CONSOLA)"
Write-Info "El cliente mostrará el progreso del envío"
Write-Host ""

if ($useLazarus) {
    # Cliente Lazarus
    $clientScript = @"
Write-Host '╔═══════════════════════════════════════════════════╗' -ForegroundColor Magenta
Write-Host '║  VENTANA DEL CLIENTE LAZARUS - Observa el envío  ║' -ForegroundColor Magenta
Write-Host '╚═══════════════════════════════════════════════════╝' -ForegroundColor Magenta
Write-Host ''
& '$lazarusClient' http://127.0.0.1:5000 outputs\data.dat
Write-Host ''
Write-Host 'Presiona Enter para cerrar esta ventana...' -ForegroundColor Yellow
Read-Host
"@
} else {
    # Cliente Python
    $clientScript = @"
& '.\.venv\Scripts\Activate.ps1'
Write-Host '╔═══════════════════════════════════════════════════╗' -ForegroundColor Magenta
Write-Host '║  VENTANA DEL CLIENTE PYTHON - Observa el envío   ║' -ForegroundColor Magenta
Write-Host '╚═══════════════════════════════════════════════════╝' -ForegroundColor Magenta
Write-Host ''
python src\http_client\send_data.py config\$ClientId.json
Write-Host ''
Write-Host 'Presiona Enter para cerrar esta ventana...' -ForegroundColor Yellow
Read-Host
"@
}

$clientScriptPath = ".\temp_client.ps1"
$clientScript | Out-File -FilePath $clientScriptPath -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-File", $clientScriptPath -PassThru | Out-Null
Write-Success "Cliente iniciado en nueva ventana"

# Esperar a que el cliente termine
Write-Info "Esperando a que el cliente complete el envío..."
Start-Sleep -Seconds 8

# Descargar gráfico
Write-Header "DESCARGANDO GRÁFICO PNG"
$plotPath = "outputs\plot_$ClientId.png"

try {
    Invoke-WebRequest -Uri "http://127.0.0.1:5000/plot/$ClientId" -OutFile $plotPath
    Write-Success "Gráfico descargado: $plotPath"
} catch {
    Write-Error "Error al descargar gráfico: $_"
}

# Mostrar resumen
Write-Header "DEMOSTRACIÓN COMPLETADA"

Write-Host ""
Write-Host "Archivos generados:" -ForegroundColor Cyan
Write-Host "  • outputs\data.dat           - Datos binarios de sensores"
Write-Host "  • $plotPath  - Gráfico PNG con 6 subplots"
Write-Host "  • data\data.db               - Base de datos SQLite"
Write-Host ""

Write-Host "Ventanas abiertas:" -ForegroundColor Cyan
Write-Host "  • Ventana SERVIDOR (verde)   - Observa los logs de recepción"
Write-Host "  • Ventana CLIENTE (magenta)  - Observa el progreso del envío"
Write-Host ""

Write-Host "Observa:" -ForegroundColor Yellow
Write-Host "  1. Ventana del SERVIDOR muestra banner y logs en tiempo real"
Write-Host "  2. Ventana del CLIENTE muestra progreso del envío paso a paso"
Write-Host "  3. AMBAS ventanas NO tienen interfaz gráfica (modo consola)"
Write-Host "  4. La interacción se muestra en los logs del servidor"
Write-Host ""

Write-Host "Para ver el gráfico generado:" -ForegroundColor Yellow
Write-Host "  Start-Process $plotPath" -ForegroundColor White
Write-Host ""

Write-Host "Para detener el servidor:" -ForegroundColor Yellow
Write-Host "  1. Ve a la ventana del servidor (verde)"
Write-Host "  2. Presiona Ctrl+C"
Write-Host ""

Write-Host "Tipo de cliente usado: $clientType" -ForegroundColor $(if ($useLazarus) { "Green" } else { "Yellow" })
if (-not $useLazarus) {
    Write-Host ""
    Write-Host "NOTA: Para usar el cliente Lazarus:" -ForegroundColor Yellow
    Write-Host "  1. Instala Lazarus IDE"
    Write-Host "  2. Compila tools\pas_client_send_data.pas"
    Write-Host "  3. Ejecuta este script nuevamente"
}

# Limpiar scripts temporales después de 2 segundos
Start-Sleep -Seconds 2
Remove-Item $serverScriptPath -ErrorAction SilentlyContinue
Remove-Item $clientScriptPath -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Presiona Enter para salir..." -ForegroundColor Cyan
Read-Host
