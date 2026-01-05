Write-Host "=== Triggering Bhagavad Gita Ingestion ===" -ForegroundColor Green
Write-Host ""
Write-Host "This will ingest all 700 verses into the vector database." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes. Please wait..." -ForegroundColor Cyan
Write-Host ""

$body = @{
    epub_path = $null
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/ingest" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 600
    
    Write-Host ""
    Write-Host "=== Ingestion Complete! ===" -ForegroundColor Green
    Write-Host "Status: $($response.status)" -ForegroundColor Green
    Write-Host "Message: $($response.message)" -ForegroundColor Green
    Write-Host "Progress: $($response.progress)%" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now use the Research Agent!" -ForegroundColor Cyan
} catch {
    Write-Host ""
    Write-Host "=== Ingestion Error ===" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        $responseBody = $reader.ReadToEnd()
        Write-Host "Details: $responseBody" -ForegroundColor Yellow
    }
}

Write-Host ""
Read-Host "Press Enter to exit"

