<#
start_all.ps1
Convenience PowerShell launcher for the project E2E flow.

Features:
- Optionally create and activate a virtualenv `.venv` (if not present)
- Optionally install requirements
- Optionally generate `data.dat` (or use existing fixtures)
- Run `run_all.py` (the project runner)

Usage examples:
# Run full flow (install deps + generate data)
.\start_all.ps1

# Skip install and data generation (faster)
.\start_all.ps1 -NoInstall -NoGenerate

# Show help
.\start_all.ps1 -Help
#>
param(
    [switch]$NoInstall,
    [switch]$NoGenerate,
    [switch]$KeepVenv,
    [string]$Python = 'py'
)

function Write-Log($msg){ Write-Host "[start_all] $msg" }

# 1) Create venv if missing
if (-not (Test-Path -Path ".\.venv")) {
    Write-Log "Creating virtualenv .venv..."
    & $Python '-3' '-m' 'venv' '.venv'
    if ($LASTEXITCODE -ne 0) { Write-Log "Failed to create virtualenv"; exit 1 }
} else {
    Write-Log "Virtualenv .venv already exists"
}

# 2) Activate venv for this script session
$activate = Join-Path -Path ".\.venv\Scripts" -ChildPath "Activate.ps1"
if (Test-Path $activate) {
    Write-Log "Activating virtualenv"
    . $activate
} else {
    Write-Log "Activation script not found; proceeding without activation"
}

# 3) Install dependencies (unless asked not to)
if (-not $NoInstall) {
    Write-Log "Installing requirements (pip install -r requirements.txt)"
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { Write-Log "pip install failed"; exit 1 }
} else { Write-Log "Skipping dependency installation (--NoInstall)" }

# 4) Run the project runner
$runner = Join-Path $PWD "run_all.py"
if (-not (Test-Path $runner)) { Write-Log "run_all.py not found in repo root"; exit 1 }

$runnerArgs = @()
if ($NoInstall) { $runnerArgs += '--no-install' }
if ($NoGenerate) { $runnerArgs += '--no-generate' }

$execArgs = @('-3', $runner) + $runnerArgs
Write-Log "Executing: $Python -3 $runner $($runnerArgs -join ' ')"
Write-Log "Running runner..."
Start-Process -FilePath $Python -ArgumentList $execArgs -NoNewWindow -Wait
$rc = $LASTEXITCODE
Write-Log "Runner exited with code $rc"
$rc = $LASTEXITCODE
Write-Log "Runner exited with code $rc"

# 5) Optional cleanup: do not remove venv by default
if (-not $KeepVenv) {
    Write-Log "(Keeping .venv by default; pass -KeepVenv to keep it)"
} else {
    Write-Log "Keeping .venv as requested"
}

Write-Log "Done."
