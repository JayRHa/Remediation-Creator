$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

$pythonInstalled = Test-Path -Path "$env:ProgramFiles\Python\Python.exe" -PathType Leaf

if ($pythonInstalled) {
    Set-Location $scriptDir
    python -m pip install -r requirements.txt
    python -m streamlit run app.py
} else {
    Write-Host "Python is not installed. Please install Python before running this script."
    python
}
