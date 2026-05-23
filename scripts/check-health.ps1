# Health Check Script - Verify all services are running

Write-Host "🏥 CyberIntel Platform - Health Check" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{Name="Gateway"; Port=8000},
    @{Name="Backend"; Port=8001},
    @{Name="Orchestrator"; Port=8002},
    @{Name="AI-Router"; Port=8003},
    @{Name="Graph-Engine"; Port=8004}
)

$failed = 0

foreach ($service in $services) {
    Write-Host "Checking $($service.Name) (port $($service.Port))... " -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$($service.Port)/health" -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ OK" -ForegroundColor Green
        } else {
            Write-Host "❌ FAILED" -ForegroundColor Red
            $failed++
        }
    } catch {
        Write-Host "❌ FAILED" -ForegroundColor Red
        $failed++
    }
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan

if ($failed -eq 0) {
    Write-Host "✅ All services healthy!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ $failed service(s) failed health check" -ForegroundColor Red
    exit 1
}
