# Multi_Agent_v2: Configurazione Locale Windows con Docker Desktop

## 🪟 Ambiente Windows - Configurazione Completa

### Prerequisiti Verificati ✅
- ✅ Windows 10/11 Pro (con Hyper-V) o Windows 11 Home (con WSL2)
- ✅ Docker Desktop installato e funzionante
- ✅ Kubernetes abilitato in Docker Desktop
- ✅ VSCode installato

### Software Aggiuntivo Necessario
```powershell
# Installa tramite winget (Windows Package Manager)
winget install Git.Git
winget install Microsoft.PowerShell
winget install Microsoft.WindowsTerminal

# Oppure scarica manualmente:
# - Git: https://git-scm.com/download/win
# - PowerShell 7: https://github.com/PowerShell/PowerShell/releases
# - Windows Terminal: Microsoft Store
```

## 📋 PASSO 1: Preparazione Directory e Clone Repository

### 1.1 Apri Windows Terminal come Amministratore
```powershell
# Verifica che Docker sia in esecuzione
docker version
docker info

# Verifica Kubernetes
kubectl version --client
kubectl cluster-info
```

### 1.2 Clone Repository
```powershell
# Crea directory di lavoro
New-Item -ItemType Directory -Path "C:\Dev\MultiAgent" -Force
Set-Location "C:\Dev\MultiAgent"

# Clone repository
git clone https://github.com/Fradbari/Multi_Agent_v2.git
Set-Location Multi_Agent_v2

# Apri in VSCode
code .
```

**COSA FA**: Crea una directory organizzata, clona il tuo repository e apre VSCode nel contesto giusto.

## 📋 PASSO 2: Configurazione Environment Variables

### 2.1 Crea File .env (Windows)
```powershell
# Copia template
Copy-Item .env.example .env

# Modifica con Notepad++ o VSCode
notepad .env
```

### 2.2 Contenuto .env Personalizzato
```env
# PostgreSQL Database per Nextcloud
POSTGRES_DB=nextcloud
POSTGRES_USER=nextcloud  
POSTGRES_PASSWORD=MySecureDbPass2025!

# Nextcloud Admin (quello che userai per login)
NEXTCLOUD_ADMIN_USER=francesco
NEXTCLOUD_ADMIN_PASSWORD=MyAdminPass2025!

# Ollama Configuration
OLLAMA_HOST=0.0.0.0
OLLAMA_BASE_URL=http://ollama:11434

# CrewAI - Analisi Finanziaria
STOCK_TICKER=TSLA
RESEARCH_DATE_START=2024-01-01
RESEARCH_DATE_END=2025-01-01
```

**COSA FA**: Configura tutte le credenziali e parametri che i container useranno. Le password devono essere sicure perché gestiscono l'accesso ai tuoi dati.

## 📋 PASSO 3: Configurazione VSCode per Windows

### 3.1 Installa Estensioni VSCode
```powershell
# Apri VSCode e installa estensioni tramite Command Palette (Ctrl+Shift+P)
# Oppure tramite CLI:
code --install-extension ms-vscode.docker
code --install-extension ms-kubernetes-tools.vscode-kubernetes-tools  
code --install-extension ms-python.python
code --install-extension ms-vscode-remote.remote-containers
code --install-extension ms-python.black-formatter
```

### 3.2 Configurazione Workspace Windows
Crea `.vscode/settings.json`:
```json
{
    "docker.containers.groupBy": "Compose Project Name",
    "kubernetes.defaultNamespace": "multi-agent-ecosystem", 
    "python.defaultInterpreterPath": "./crewai/.venv/Scripts/python.exe",
    "python.analysis.extraPaths": ["./crewai"],
    "terminal.integrated.defaultProfile.windows": "PowerShell",
    "terminal.integrated.profiles.windows": {
        "PowerShell": {
            "source": "PowerShell",
            "icon": "terminal-powershell"
        }
    },
    "files.eol": "\n",
    "files.watcherExclude": {
        "**/node_modules/**": true,
        "**/.git/objects/**": true,
        "**/data/**": true,
        "**/volumes/**": true
    }
}
```

**COSA FA**: Configura VSCode per riconoscere i container Docker, usare il namespace Kubernetes corretto, e impostare Python per il debug del codice CrewAI.

### 3.3 Task Automation per Windows
Crea `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "🐳 Docker: Avvia Tutti i Servizi",
            "type": "shell",
            "command": "docker-compose",
            "args": ["up", "-d", "--build"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always"
            },
            "options": {
                "shell": {
                    "executable": "powershell.exe"
                }
            }
        },
        {
            "label": "🛑 Docker: Ferma Tutti i Servizi", 
            "type": "shell",
            "command": "docker-compose",
            "args": ["down"],
            "group": "build",
            "options": {
                "shell": {
                    "executable": "powershell.exe"
                }
            }
        },
        {
            "label": "🤖 Ollama: Scarica Modelli",
            "type": "shell",
            "command": "powershell",
            "args": ["-Command", "docker exec ollama ollama pull mistral; docker exec ollama ollama pull llama2:7b-chat"],
            "group": "build"
        },
        {
            "label": "🔬 CrewAI: Esegui Analisi Finanziaria",
            "type": "shell", 
            "command": "docker",
            "args": ["exec", "-it", "crewai", "python", "main.py"],
            "group": "test"
        },
        {
            "label": "🏥 Sistema: Verifica Servizi",
            "type": "shell",
            "command": "powershell",
            "args": ["-File", "./scripts/health_check.ps1"],
            "group": "test"
        }
    ]
}
```

**COSA FA**: Crea scorciatoie in VSCode per operazioni comuni. Puoi usarle con `Ctrl+Shift+P` → "Tasks: Run Task".

## 📋 PASSO 4: Script di Utilità per Windows

### 4.1 Health Check Script
Crea `scripts/health_check.ps1`:
```powershell
Write-Host "🏥 Multi-Agent System Health Check" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Verifica Docker
try {
    docker info | Out-Null
    Write-Host "✅ Docker: RUNNING" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker: NOT RUNNING" -ForegroundColor Red
    exit 1
}

# Lista servizi da controllare
$services = @(
    @{name="Ollama"; port=11434; path="/api/version"},
    @{name="Open WebUI"; port=3000; path="/"},
    @{name="FlowiseAI"; port=3001; path="/"},
    @{name="Qdrant"; port=6333; path="/health"},
    @{name="Nextcloud"; port=8080; path="/status.php"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$($service.port)$($service.path)" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        Write-Host "✅ $($service.name): OK (port $($service.port))" -ForegroundColor Green
    } catch {
        Write-Host "❌ $($service.name): FAIL (port $($service.port))" -ForegroundColor Red
    }
}

Write-Host "`n🔍 Container Status:" -ForegroundColor Yellow
docker-compose ps
```

**COSA FA**: Verifica che tutti i servizi siano raggiungibili e funzionanti. Molto utile per debug.

### 4.2 Script Setup Automatico
Crea `setup_windows.ps1`:
```powershell
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
```

## 📋 PASSO 5: Deployment Docker Compose (RACCOMANDATO)

### 5.1 Avvio Servizi
```powershell
# Dalla directory Multi_Agent_v2
# Avvia tutti i servizi in background
docker-compose up -d --build

# Verifica che tutti i container siano in esecuzione
docker-compose ps

# Segui i log in tempo reale
docker-compose logs -f
```

**COSA FA OGNI SERVIZIO**:

**ollama**: Scarica e serve i modelli LLM (Mistral, Llama2, ecc.). È il "cervello" del sistema.

**open-webui**: Interfaccia web simile a ChatGPT. Ti permette di chattare con i modelli locali.

**qdrant**: Database che memorizza "significati" dei testi (embeddings) per ricerche intelligenti.

**flowise**: Strumento visuale per creare workflow di agenti trascinando e collegando blocchi.

**crewai**: Container Python che esegue analisi finanziarie automatiche con agenti specializzati.

**nextcloud**: Il tuo "Google Drive" personale per caricare documenti.

**nextcloud-db**: Database PostgreSQL che memorizza i metadati di Nextcloud.

**nextcloud-redis**: Cache per velocizzare Nextcloud.

### 5.2 Download Modelli LLM
```powershell
# Attendi che Ollama sia completamente avviato (circa 1-2 minuti)
Start-Sleep -Seconds 60

# Scarica i modelli (ATTENZIONE: files di diversi GB)
docker exec ollama ollama pull mistral          # ~4GB - Modello generale
docker exec ollama ollama pull llama2:7b-chat  # ~3.8GB - Chat ottimizzato  
docker exec ollama ollama pull codellama:7b    # ~3.8GB - Programmazione

# Verifica modelli scaricati
docker exec ollama ollama list
```

**COSA FA**: Scarica i modelli AI che userai per chat e analisi. Mistral è veloce e preciso per uso generale.

### 5.3 Verifica Installazione
```powershell
# Esegui health check
./scripts/health_check.ps1

# Oppure verifica manualmente
Start-Process "http://localhost:3000"    # Open WebUI
Start-Process "http://localhost:3001"    # FlowiseAI  
Start-Process "http://localhost:8080"    # Nextcloud
Start-Process "http://localhost:6333/dashboard"  # Qdrant
```

## 📋 PASSO 6: Configurazione Kubernetes (OPZIONALE - Per Produzione)

### 6.1 Verifica Kubernetes Docker Desktop
```powershell
# Verifica che Kubernetes sia attivo
kubectl cluster-info
kubectl get nodes

# Se non funziona, vai in Docker Desktop > Settings > Kubernetes > Enable Kubernetes
```

### 6.2 Deploy su Kubernetes
```powershell
# Crea namespace dedicato
kubectl apply -f kubernetes/00-namespace.yml

# Crea secrets dalle variabili .env
kubectl create secret generic nextcloud-secrets --from-env-file=.env --namespace=multi-agent-ecosystem

# Deploy tutti i servizi
kubectl apply -f kubernetes/

# Verifica che tutto funzioni
kubectl get pods -n multi-agent-ecosystem -w
```

### 6.3 Port Forwarding per Accesso Locale
```powershell
# Apri terminali separati per ogni servizio
Start-Process powershell -ArgumentList "-Command", "kubectl port-forward -n multi-agent-ecosystem service/open-webui-service 3000:80"
Start-Process powershell -ArgumentList "-Command", "kubectl port-forward -n multi-agent-ecosystem service/flowise-service 3001:3000"  
Start-Process powershell -ArgumentList "-Command", "kubectl port-forward -n multi-agent-ecosystem service/nextcloud-service 8080:80"
Start-Process powershell -ArgumentList "-Command", "kubectl port-forward -n multi-agent-ecosystem service/qdrant-service 6333:6333"
```

**DIFFERENZA DOCKER VS KUBERNETES**:
- **Docker Compose**: Semplice, tutto su una macchina, perfetto per sviluppo
- **Kubernetes**: Complesso ma scalabile, può gestire più macchine, produzione

## 📋 PASSO 7: Utilizzo Pratico del Sistema

### 7.1 Analisi Finanziaria con CrewAI
```powershell
# Modifica il ticker azionario da analizzare
(Get-Content crewai/main.py) -replace 'TSLA', 'AAPL' | Set-Content crewai/main.py

# Esegui l'analisi
docker exec -it crewai python main.py

# Visualizza risultati
docker logs crewai
```

**COSA FA**: CrewAI crea due agenti AI:
1. **Market Analyst**: Raccoglie dati finanziari e notizie
2. **Investment Strategist**: Analizza e dà raccomandazioni Buy/Hold/Sell

### 7.2 Chat con Modelli via Open WebUI
1. Vai su http://localhost:3000
2. Crea account (primo accesso)
3. Seleziona modello (mistral raccomandato)
4. Inizia a chattare come ChatGPT ma tutto locale!

### 7.3 Orchestrazione Visuale con FlowiseAI
1. Vai su http://localhost:3001
2. Crea nuovo "Chatflow"
3. Trascina blocchi: LLM → Memory → Tools
4. Collega Ollama: `http://ollama:11434`
5. Collega Qdrant: `http://qdrant:6333`

### 7.4 Storage con Nextcloud
1. Vai su http://localhost:8080
2. Login: francesco / MyAdminPass2025! (o quello che hai impostato)
3. Carica documenti per RAG (Retrieval Augmented Generation)
4. Integra con FlowiseAI per ricerche intelligenti

## 🔧 Troubleshooting Windows

### Problemi Comuni Windows

#### Error: "docker-compose non riconosciuto"
```powershell
# Verifica installazione Docker Desktop
docker --version
docker-compose --version

# Se non funziona, riavvia Docker Desktop
Restart-Service docker
```

#### Porte occupate
```powershell
# Verifica cosa usa la porta 3000
netstat -ano | findstr :3000

# Termina processo se necessario (sostituisci PID)
taskkill /PID 1234 /F
```

#### Container non si avviano
```powershell
# Verifica risorse Docker Desktop
# Docker Desktop > Settings > Resources
# RAM: minimo 8GB raccomandato
# CPU: minimo 4 core

# Pulisci sistema Docker
docker system prune -a
docker volume prune
```

#### Kubernetes non si connette
```powershell
# Reset cluster Kubernetes
# Docker Desktop > Settings > Kubernetes > Reset Kubernetes Cluster

# Verifica context
kubectl config current-context
kubectl config use-context docker-desktop
```

### Performance Windows

#### Ottimizzazione Docker Desktop
```powershell
# Impostazioni raccomandate:
# Docker Desktop > Settings > General:
# - Use WSL 2 based engine ✅
# - Send usage statistics ❌

# Resources > Advanced:
# - Memory: 8GB (minimo 6GB)
# - CPUs: 4 (o tutti disponibili)
# - Disk image size: 100GB
```

#### WSL2 Ottimizzazione (se usi WSL2)
```powershell
# Crea file .wslconfig in %USERPROFILE%
@"
[wsl2]
memory=8GB
processors=4
"@ | Out-File -FilePath "$env:USERPROFILE\.wslconfig" -Encoding ASCII

# Riavvia WSL
wsl --shutdown
```

## 🎯 Recap: Cosa Hai Ottenuto

### Sistema Multi-Agente Completo
1. **Backend LLM locale** (Ollama) - Nessuna dipendenza cloud
2. **Chat Interface** (Open WebUI) - Come ChatGPT ma privato
3. **Orchestrazione Agenti** (FlowiseAI + CrewAI) - Automazione intelligente
4. **Database Vettoriale** (Qdrant) - Memoria e ricerche semantiche
5. **Storage Personale** (Nextcloud) - Il tuo cloud privato

### Vantaggi del Setup
- ✅ **Zero costi** - Tutto open source e locale
- ✅ **Privacy totale** - I tuoi dati non lasciano il PC
- ✅ **Personalizzabile** - Modifica agenti e workflow
- ✅ **Scalabile** - Da laptop a cluster Kubernetes
- ✅ **Professionale** - Debug VSCode integrato

### Prossimi Passi Consigliati
1. **Esplora Open WebUI**: Prova diversi modelli e conversazioni
2. **Crea workflow FlowiseAI**: Esperimenta con drag&drop
3. **Personalizza CrewAI**: Aggiungi nuovi agenti e domini
4. **Integra dati**: Carica documenti in Nextcloud per RAG
5. **Monitor sistema**: Usa health check regolarmente

Il tuo ambiente Multi-Agente è ora completamente operativo su Windows! 🚀
