<#
start_services.ps1

Opciones:
 -StartMosquitto  : intenta iniciar el servicio mosquitto; si falla, arranca mosquitto.exe en nueva ventana
 -OpenSubscriber  : abre una ventana con mosquitto_sub para monitorear topics DATA/#
 -StartClients    : lanza client1..client4 en background usando el Python del venv

Ejemplo:
 .\start_services.ps1 -StartMosquitto -OpenSubscriber -StartClients
#>

[CmdletBinding()]
param(
    [switch]$StartMosquitto,
    [switch]$OpenSubscriber,
    [switch]$StartClients
)

function Start-MosquittoInNewWindow {
    $exe = 'C:\Program Files\mosquitto\mosquitto.exe'
    if (Test-Path $exe) {
        Write-Output "Iniciando Mosquitto en nueva ventana..."
        Start-Process -FilePath $exe -ArgumentList '-v' -WorkingDirectory 'C:\Program Files\mosquitto' -WindowStyle Normal
    } else {
        Write-Output "No se encontró mosquitto.exe en ruta esperada: $exe"
    }
}

if ($StartMosquitto) {
    try {
        # Intentar iniciar el servicio (requiere permisos administrativos)
        Start-Service mosquitto -ErrorAction Stop
        Write-Output "Servicio mosquitto iniciado."
    } catch {
        Write-Output "No se pudo iniciar el servicio mosquitto (probablemente permisos). Se abrirá mosquitto en nueva ventana."
        Start-MosquittoInNewWindow
    }
}

if ($OpenSubscriber) {
    $subExe = 'C:\Program Files\mosquitto\mosquitto_sub.exe'
    if (Test-Path $subExe) {
        Write-Output "Abriendo ventana de suscripción (DATA/#)..."
        Start-Process -FilePath $subExe -ArgumentList '-h 127.0.0.1 -t "DATA/#" -v' -WorkingDirectory 'C:\Program Files\mosquitto' -WindowStyle Normal
    } else {
        Write-Output "No se encontró mosquitto_sub.exe"
    }
}

if ($StartClients) {
    $python = Join-Path -Path (Get-Location) -ChildPath '.venv\Scripts\python.exe'
    if (Test-Path $python) {
        for ($i = 1; $i -le 4; $i++) {
                $cfg = "client$i.json"
                if (Test-Path $cfg) {
                    Write-Output "Iniciando client$i con $cfg"
                    # Ejecutar el subscriber desde la nueva ruta en src/clients
                    Start-Process -NoNewWindow -FilePath $python -ArgumentList "src\clients\mqtt_subscriber.py --config $cfg --loglevel INFO"
                    Start-Sleep -Milliseconds 300
                } else {
                    Write-Output "No encontrado $cfg, saltando"
                }
            }
    } else {
        Write-Output "No se encontró el python del venv en $python. Asegúrate de crear el .venv primero."
    }
}

Write-Output "start_services.ps1 finalizado."
