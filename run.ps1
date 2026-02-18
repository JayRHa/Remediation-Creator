$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

if (Get-Command python -ErrorAction SilentlyContinue) {
    $pyCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pyCmd = "py"
} else {
    Write-Host "Python is not installed. Please install Python 3.10+ before running this script."
    exit 1
}

& $pyCmd -m pip install --upgrade pip
& $pyCmd -m pip install -r requirements.txt
& $pyCmd -m streamlit run app.py
