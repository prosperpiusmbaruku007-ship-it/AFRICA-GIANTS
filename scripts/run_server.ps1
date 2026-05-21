# PowerShell script to run the local FastAPI serving endpoint
Write-Host "Starting FastAPI Inference API Server..." -ForegroundColor Cyan
python run.py serve --port 8000
