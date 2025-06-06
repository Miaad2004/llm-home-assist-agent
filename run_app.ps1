# run_app.ps1

param(
    [switch]$ForceInstall
)

$venvPath = "$PSScriptRoot\agent_venv"
$venvPython = "$venvPath\Scripts\python.exe"

# Check if venv exists
if (-Not (Test-Path $venvPython)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venvPath
    Write-Host "Installing requirements..."
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r "$PSScriptRoot\requirements.txt"
}
else {
    Write-Host "Virtual environment already exists. Skipping setup."
    if ($ForceInstall) {
        Write-Host "Force installing requirements..."
        & $venvPython -m pip install --upgrade pip
        & $venvPython -m pip install -r "$PSScriptRoot\requirements.txt"
    }
}

# Set PYTHONPATH and run the app
$env:PYTHONPATH = "$PSScriptRoot"
& $venvPython "$PSScriptRoot\scripts\run_app.py"