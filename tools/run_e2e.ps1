param(
    [string]$ServerUrl = 'http://127.0.0.1:5000',
    [int]$Port = 5000
)

$python = 'py'

Write-Host "1) Installing requirements..."
& $python -3 -m pip install -r requirements.txt

Write-Host "2) Generating data.dat (synthetic)..."
& $python -3 tools/generate_data_dat.py --out data.dat --count 10 --stations 10 --seed 42

Write-Host "3) Starting Flask server as module (detached)..."
$proc = Start-Process -FilePath $python -ArgumentList '-3','-m','src.http_server.app' -PassThru
Write-Host "  Server PID: $($proc.Id)"

Write-Host "4) Waiting for server to accept connections on port $Port..."
$maxWait = 30
$waited = 0
while ($waited -lt $maxWait) {
    $c = Test-NetConnection -ComputerName '127.0.0.1' -Port $Port -WarningAction SilentlyContinue
    if ($c.TcpTestSucceeded) { break }
    Start-Sleep -Seconds 1
    $waited++
}
if ($waited -ge $maxWait) {
    Write-Warning "Server did not start within $maxWait seconds. Check logs."
} else {
    Write-Host "Server is up (waited $waited s)."
}

Write-Host "5) Sending data.dat with client..."
& $python -3 src/http_client/send_data.py --server $ServerUrl --data-file data.dat --client-id client1

Write-Host "6) Downloading plot for client1"
$plotUrl = "$ServerUrl/plot/client1"
try {
    Invoke-WebRequest -Uri $plotUrl -OutFile plot_client1.png -UseBasicParsing -ErrorAction Stop
    Write-Host "Saved plot to plot_client1.png"
} catch {
    Write-Warning "Failed to download plot: $_"
}

Write-Host "7) Stopping server (PID $($proc.Id))"
try {
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Server stopped."
} catch {
    Write-Warning "Unable to stop server process: $_"
}

Write-Host "E2E run finished. Check plot_client1.png and data/data.db for results."