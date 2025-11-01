<#
.SYNOPSIS
    Script de ejecución del flujo HTTP Client -> HTTP Server
    INFO1157 - Proyecto #2 - Sistemas Inteligentes

.DESCRIPTION
    Este script ejecuta el flujo completo del proyecto:
    1. Activa el entorno virtual Python
    2. Genera el archivo data.dat con datos sintéticos
    3. Inicia el servidor Flask en modo consola
    4. Ejecuta el cliente HTTP que envía datos
    5. Descarga el gráfico generado
    6. Detiene el servidor

.PARAMETER NoGenerate
    Si se especifica, no genera data.dat (usa el existente)

.PARAMETER NoInstall
    Si se especifica, no instala dependencias

.PARAMETER ClientId
    ID del cliente a ejecutar (por defecto: client1)

.EXAMPLE
    .\run_http_flow.ps1
    Ejecuta el flujo completo

.EXAMPLE
    .\run_http_flow.ps1 -NoGenerate -ClientId client2
    Usa data.dat existente y ejecuta como client2
#>

param(
    [switch]$NoGenerate,
    [switch]$NoInstall,
    [string]$ClientId = "client1",
    [string]$Python = "python"
)

function Write-Header {
    param([string]$Title)
    Write-Host "`n$("="*60)" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Yellow
    Write-Host "$("="*60)`n" -ForegroundColor Cyan
}

function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host "[$Step] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-Success {
    param([string]$Message)
    Write-Host "[OK] " -ForegroundColor Green -NoNewline
    Write-Host $Message -ForegroundColor White
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] " -ForegroundColor Red -NoNewline
    Write-Host $Message -ForegroundColor White
}

# Banner principal
Clear-Host
Write-Host "`n"
Write-Host "  ╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "  ║                                                       ║" -ForegroundColor Cyan
Write-Host "  ║         HTTP Client/Server Flow - INFO1157           ║" -ForegroundColor Yellow
Write-Host "  ║         Proyecto #2 - Sistemas Inteligentes          ║" -ForegroundColor Yellow
Write-Host "  ║                 By Alberto Caro                       ║" -ForegroundColor White
Write-Host "  ║                                                       ║" -ForegroundColor Cyan
Write-Host "  ╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "`n"

# 1. Activar entorno virtual
Write-Header "PASO 1: Activar entorno virtual"
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Step "1.1" "Activando entorno virtual..."
    & $venvPath
    Write-Success "Entorno virtual activado"
} else {
    Write-Error-Custom "No se encontró el entorno virtual en .venv"
    Write-Host "Ejecuta primero: py -3 -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# 2. Instalar dependencias
if (-not $NoInstall) {
    Write-Header "PASO 2: Instalar dependencias"
    Write-Step "2.1" "Instalando requirements.txt..."
    & $Python -m pip install -q -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Dependencias instaladas"
    } else {
        Write-Error-Custom "Error instalando dependencias"
        exit 1
    }
} else {
    Write-Host "`n[SKIP] Instalación de dependencias omitida" -ForegroundColor Yellow
}

# 3. Generar data.dat
if (-not $NoGenerate) {
    Write-Header "PASO 3: Generar data.dat"
    Write-Step "3.1" "Generando archivo binario con datos sintéticos..."
    & $Python tools\generate_data_dat.py --out outputs\data.dat --count 10 --stations 10 --seed 42
    if ($LASTEXITCODE -eq 0) {
        $fileSize = (Get-Item outputs\data.dat).Length
        Write-Success "data.dat generado - $fileSize bytes"
    } else {
        Write-Host "ERROR: Error generando data.dat" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`nSKIP: Generacion de data.dat omitida" -ForegroundColor Yellow
    if (-not (Test-Path "outputs\data.dat")) {
        Write-Host "ERROR: No existe outputs\data.dat" -ForegroundColor Red
        exit 1
    }
}

# 4. Iniciar servidor Flask
Write-Header "PASO 4: Iniciar servidor Flask"
Write-Step "4.1" "Iniciando servidor HTTP en puerto 5000..."
$serverProcess = Start-Process -FilePath $Python -ArgumentList "-m","src.http_server.app" -PassThru -WindowStyle Normal
Write-Success "Servidor iniciado (PID: $($serverProcess.Id))"

# 5. Esperar a que el servidor esté listo
Write-Step "4.2" "Esperando a que el servidor acepte conexiones..."
$timeout = 30
$elapsed = 0
$serverReady = $false

while ($elapsed -lt $timeout) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/" -Method GET -TimeoutSec 1 -ErrorAction SilentlyContinue
        $serverReady = $true
        break
    } catch {
        Start-Sleep -Milliseconds 500
        $elapsed += 0.5
        Write-Host "." -NoNewline
    }
}

Write-Host ""
if (-not $serverReady) {
    Write-Host "ERROR: El servidor no respondio en $timeout segundos" -ForegroundColor Red
    Stop-Process -Id $serverProcess.Id -Force
    exit 1
}
Write-Success "Servidor listo y aceptando conexiones"

# 6. Ejecutar cliente HTTP
Write-Header "PASO 5: Ejecutar cliente HTTP"
Write-Step "5.1" "Enviando datos desde $ClientId..."
Write-Host ""
& $Python src\http_client\send_data.py --server http://127.0.0.1:5000 --data-file outputs\data.dat --client-id $ClientId
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Success "Datos enviados correctamente"
} else {
    Write-Host ""
    Write-Host "ERROR: Error enviando datos" -ForegroundColor Red
    Stop-Process -Id $serverProcess.Id -Force
    exit 1
}

# 7. Descargar gráfico
Write-Header "PASO 6: Descargar gráfico"
Write-Step "6.1" "Solicitando gráfico de $ClientId..."
$plotUrl = "http://127.0.0.1:5000/plot/$ClientId"
$plotFile = "outputs\plot_$ClientId.png"

try {
    Invoke-WebRequest -Uri $plotUrl -OutFile $plotFile -UseBasicParsing
    $plotSize = (Get-Item $plotFile).Length
    $plotSizeKB = [math]::Round($plotSize/1KB, 2)
    Write-Success "Grafico descargado: $plotFile - $plotSizeKB KB"
} catch {
    Write-Host "ERROR: Error descargando grafico - $_" -ForegroundColor Red
    Stop-Process -Id $serverProcess.Id -Force
    exit 1
}

# 8. Detener servidor
Write-Header "PASO 7: Detener servidor"
Write-Step "7.1" "Deteniendo servidor Flask (PID: $($serverProcess.Id))..."
try {
    Stop-Process -Id $serverProcess.Id -Force -ErrorAction Stop
    Write-Success "Servidor detenido"
} catch {
    Write-Host "ERROR: Error deteniendo servidor - $_" -ForegroundColor Red
}

# Resumen final
Write-Host "`n"
Write-Host "  ╔═══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "  ║                                                       ║" -ForegroundColor Green
Write-Host "  ║              PROCESO COMPLETADO EXITOSAMENTE          ║" -ForegroundColor Yellow
Write-Host "  ║                                                       ║" -ForegroundColor Green
Write-Host "  ╚═══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host "`n"
Write-Host "  Archivos generados:" -ForegroundColor Cyan
Write-Host "    • outputs\data.dat      - Datos binarios de sensores"
Write-Host "    • $plotFile - Gráfico PNG con 6 subplots"
Write-Host "    • data\data.db          - Base de datos SQLite"
Write-Host "`n"
Write-Host "  Para ver el gráfico:" -ForegroundColor Yellow
Write-Host "    Start $plotFile" -ForegroundColor White
Write-Host "`n"
