#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

if command -v python3 >/dev/null 2>&1; then
    py_cmd="python3"
elif command -v python >/dev/null 2>&1; then
    py_cmd="python"
else
    echo "Python is not installed. Please install Python 3.10+ before running this script."
    exit 1
fi

"$py_cmd" -m pip install --upgrade pip
"$py_cmd" -m pip install -r requirements.txt
"$py_cmd" -m streamlit run app.py
