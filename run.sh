#!/bin/bash

# Check if we have the required arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <query> <analysis_depth> <api_key>"
    exit 1
fi

# Run the Python script with unbuffered output
PYTHONUNBUFFERED=1 python run_workflow.py "$1" "$2" "$3" 