# Richiede esecuzione come amministratore
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "⚠️ Esegui come Amministratore per configurazione completa" -ForegroundColor Yellow
}

Write-Host "🚀 Setup Multi_Agent_v2 per Windows" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Verifica prerequisiti
Write-Host "🔍 Verifica prerequisiti..." -ForegroundColor Yellow

# Docker
try {
    docker --version
    Write-Host "✅ Docker installato" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker non trovato. Installa Docker Desktop" -ForegroundColor Red
    Start-Process "https://www.docker.com/products/docker-desktop"
    exit 1
}

# Kubernetes
try {
    kubectl version --client
    Write-Host "✅ Kubectl disponibile" -ForegroundColor Green
} catch {
    Write-Host "❌ Kubectl non trovato. Verifica installazione Docker Desktop" -ForegroundColor Red
    exit 1
}

# Git
try {
    git --version
    Write-Host "✅ Git installato" -ForegroundColor Green
} catch {
    Write-Host "❌ Git non trovato. Installazione..." -ForegroundColor Yellow
    winget install Git.Git
}

# Crea directory se non esistono
New-Item -ItemType Directory -Path "scripts" -Force
New-Item -ItemType Directory -Path ".vscode" -Force
New-Item -ItemType Directory -Path "data" -Force

Write-Host "✅ Setup Windows completato!" -ForegroundColor Green