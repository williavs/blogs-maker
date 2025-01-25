#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install or upgrade pip
python -m pip install --upgrade pip

# Install reportlab explicitly first
pip install reportlab

# Install all requirements
echo "Installing required packages..."
pip install -r requirements.txt

# Start the Streamlit app
echo "Starting Invoice Generator..."
streamlit run app.py 