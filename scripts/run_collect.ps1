# PowerShell script to execute web scraper and data preprocessing
Write-Host "Starting Data Ingestion & Preprocessing..." -ForegroundColor Cyan
python run.py scrape
Write-Host "Ingestion complete!" -ForegroundColor Green
