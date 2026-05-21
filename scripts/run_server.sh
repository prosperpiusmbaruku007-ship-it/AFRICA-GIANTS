#!/bin/bash
# Bash script to run the local FastAPI serving endpoint
echo "Starting FastAPI Inference API Server..."
python run.py serve --port 8000
