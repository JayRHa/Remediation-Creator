#!/bin/bash

scriptDir=$(dirname "$0")
if command -v python3 &>/dev/null; then
    cd "$scriptDir" || exit
    python3 -m pip install -r requirements.txt
    python3 -m streamlit run app.py
else
    echo "Python is not installed. Please install Python before running this script."
fi
