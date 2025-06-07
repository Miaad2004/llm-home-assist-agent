# PowerShell script to start the Smart Home Assistant API server

param(
    [int]$Port = 8000,
    [string]$HostAddress = "0.0.0.0",
    [switch]$NoReload,
    [string]$LogLevel = "info",
    [string]$Workers = "1",
    [switch]$ForceInstall
)

# Clear terminal for clean start
Clear-Host

# Change to script directory to ensure correct .env loading
Set-Location $PSScriptRoot

$venvPath = "$PSScriptRoot\agent_venv"
$venvPython = "$venvPath\Scripts\python.exe"

# Check for required XTTS model files
$xttsPath = "$PSScriptRoot\app\voice\TTS\XTTS"
$requiredFiles = @(
    "dvae.pth",
    "mel_stats.pth", 
    "model.pth",
    "speakers_xtts.pth"
)

Write-Host "Checking for required XTTS model files..." -ForegroundColor Yellow
$missingFiles = @()

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $xttsPath $file
    if (-Not (Test-Path $filePath)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "Error: Missing required XTTS model files:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Please download the files from:" -ForegroundColor Yellow
    Write-Host "https://huggingface.co/coqui/XTTS-v2/tree/main" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Download the missing .pth files to: $xttsPath" -ForegroundColor Yellow
    exit 1
}

Write-Host "All required XTTS model files found." -ForegroundColor Green

Write-Host "Starting Smart Home Assistant API server..." -ForegroundColor Green

# Check if venv exists
if (-Not (Test-Path $venvPython)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
    Write-Host "Installing requirements..." -ForegroundColor Yellow
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r "$PSScriptRoot\requirements.txt"
}
else {
    Write-Host "Virtual environment already exists. Skipping setup." -ForegroundColor Yellow
    if ($ForceInstall) {
        Write-Host "Force installing requirements..." -ForegroundColor Yellow
        & $venvPython -m pip install --upgrade pip
        & $venvPython -m pip install -r "$PSScriptRoot\requirements.txt"
    }
}

# Set PYTHONPATH
$env:PYTHONPATH = "$PSScriptRoot"

Write-Host "Server will be available at: http://${HostAddress}:${Port}" -ForegroundColor Cyan
Write-Host "API documentation will be available at: http://${HostAddress}:${Port}/docs" -ForegroundColor Cyan
Write-Host "Use Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ("-" * 60) -ForegroundColor Gray

# Build uvicorn command with parameters
$uvicornArgs = @(
    "-m", "uvicorn",
    "app.api.main:app",
    "--host", $HostAddress,
    "--port", $Port,
    "--log-level", $LogLevel
)

if (-Not $NoReload) {
    $uvicornArgs += "--reload"
}

# Add workers if specified (and greater than 1)
if ([int]$Workers -gt 1) {
    $uvicornArgs += "--workers"
    $uvicornArgs += $Workers
}

# Start the server
try {
    & $venvPython $uvicornArgs
}
catch {
    Write-Host "Failed to start the API server: $_" -ForegroundColor Red
    exit 1
}