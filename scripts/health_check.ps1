# health_check.ps1 - Verifica stato servizi Multi-Agent
Write-Host "🏥 Multi-Agent System Health Check" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Verifica Docker
try {
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker: RUNNING" -ForegroundColor Green
    } else {
        throw "Docker non risponde"
    }
} catch {
    Write-Host "❌ Docker: NOT RUNNING" -ForegroundColor Red
    Write-Host "   Avvia Docker Desktop e riprova" -ForegroundColor Yellow
    exit 1
}

# Lista servizi da controllare
$services = @(
    @{name="Ollama LLM Backend"; port=11434; path="/api/version"; description="Serve modelli AI locali"},
    @{name="Open WebUI"; port=3000; path="/health"; description="Interfaccia chat come ChatGPT"},
    @{name="FlowiseAI"; port=3001; path="/"; description="Orchestrazione visuale agenti"},
    @{name="Qdrant Vector DB"; port=6333; path="/health"; description="Database vettoriale per RAG"},
    @{name="Nextcloud Storage"; port=8080; path="/status.php"; description="Storage self-hosted"}
)

Write-Host "🔍 Verifica servizi..." -ForegroundColor Yellow
Write-Host ""

foreach ($service in $services) {
    $url = "http://localhost:$($service.port)$($service.path)"
    try {
        $response = Invoke-WebRequest -Uri $url -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        Write-Host "✅ $($service.name): " -ForegroundColor Green -NoNewline
        Write-Host "OK " -ForegroundColor White -NoNewline
        Write-Host "(porta $($service.port))" -ForegroundColor DarkGray
        Write-Host "   → $($service.description)" -ForegroundColor DarkGray
    } catch {
        Write-Host "❌ $($service.name): " -ForegroundColor Red -NoNewline  
        Write-Host "FAIL " -ForegroundColor White -NoNewline
        Write-Host "(porta $($service.port))" -ForegroundColor DarkGray
        Write-Host "   → Servizio non raggiungibile" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Status container Docker Compose
Write-Host "🐳 Docker Compose Status:" -ForegroundColor Cyan
try {
    docker-compose ps --format "table {{.Name}}	{{.State}}	{{.Ports}}"
} catch {
    Write-Host "⚠️ Non posso leggere stato docker-compose" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🌐 Accessi rapidi:" -ForegroundColor Green
Write-Host "   Open WebUI:    http://localhost:3000" -ForegroundColor White
Write-Host "   FlowiseAI:     http://localhost:3001" -ForegroundColor White  
Write-Host "   Nextcloud:     http://localhost:8080" -ForegroundColor White
Write-Host "   Qdrant:        http://localhost:6333/dashboard" -ForegroundColor White
Write-Host ""
