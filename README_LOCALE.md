# Multi_Agent_v2: Configurazione Locale Completa

## 🎯 Panoramica del Sistema

Il repository **Multi_Agent_v2** implementa un ecosistema completo di agenti AI multi-modali con supporto per:

### 🏗️ Architettura
- **Backend LLM**: Ollama per modelli locali (Mistral, Llama2, CodeLlama)
- **Interfaccia Web**: Open WebUI per chat, playground e RAG
- **Database Vettoriale**: Qdrant per embeddings e memoria degli agenti  
- **Orchestrazione Agenti**:
  - **FlowiseAI**: Orchestrazione visuale no-code/low-code
  - **CrewAI**: Framework Python per agenti specializzati (analisi finanziaria)
- **Storage Self-hosted**: Nextcloud + PostgreSQL + Redis

### 🚀 Configurazione Rapida

#### Prerequisiti
```bash
# Verifica che Docker Desktop sia installato e Kubernetes abilitato
docker --version
kubectl version --client
```

#### Setup Veloce
```bash
# 1. Clone e preparazione
git clone https://github.com/Fradbari/Multi_Agent_v2.git
cd Multi_Agent_v2

# 2. Configurazione automatica VSCode
chmod +x setup_vscode_workspace.sh
./setup_vscode_workspace.sh

# 3. Configurazione environment
cp .env.example .env
# Modifica .env con le tue credenziali sicure

# 4. Deployment (scegli una opzione)
# Opzione A: Docker Compose (raccomandato per sviluppo)
./deploy.sh docker

# Opzione B: Kubernetes (per produzione/scalabilità)  
./deploy.sh kubernetes
```

### 📱 Accesso ai Servizi

Dopo il deployment, i servizi saranno disponibili su:

| Servizio | URL | Descrizione |
|----------|-----|-------------|
| **Open WebUI** | http://localhost:3000 | Chat e playground LLM |
| **FlowiseAI** | http://localhost:3001 | Orchestrazione visuale agenti |
| **Nextcloud** | http://localhost:8080 | Storage self-hosted |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | Database vettoriale |
| **Ollama API** | http://localhost:11434 | API LLM backend |

### 🛠️ Sviluppo con VSCode

#### Configurazione Automatica
Lo script `setup_vscode_workspace.sh` configura automaticamente:
- ✅ Settings VSCode ottimizzati
- ✅ Task automation per Docker/Kubernetes
- ✅ Launch configurations per debug
- ✅ Estensioni raccomandate
- ✅ Dev container setup

#### Task Disponibili (`Ctrl+Shift+P` → `Tasks: Run Task`)
- 🐳 **Docker: Build and Start All** - Avvia tutti i servizi
- 🛑 **Docker: Stop All Services** - Ferma tutti i servizi
- ☸️ **Kubernetes: Deploy All** - Deploy su Kubernetes
- 🤖 **Ollama: Pull Models** - Scarica modelli LLM
- 🔬 **CrewAI: Run Analysis** - Esegue analisi finanziaria
- 🏥 **System: Health Check** - Verifica stato servizi

#### Debug Python CrewAI
1. Apri `crewai/main.py`
2. Imposta breakpoint
3. Premi `F5` → "Python: Debug CrewAI Main"

### 🤖 Personalizzazione CrewAI

#### Modifica Agente Finanziario
```python
# In crewai/main.py
STOCK_TICKER = "AAPL"  # Cambia ticker
RESEARCH_DATE_START = "2024-01-01"
RESEARCH_DATE_END = "2024-12-01"
```

#### Aggiungi Nuovo Agente
```python
risk_analyst = Agent(
    role='Risk Assessment Specialist',
    goal=f'Evaluate investment risks for {STOCK_TICKER}',
    backstory="Expert in risk management and portfolio optimization...",
    verbose=True,
    tools=[search_tool, financial_tool.get_stock_data],
    llm=ollama_llm
)
```

### 🔗 Integrazione FlowiseAI

#### Setup Connessioni
1. Vai su http://localhost:3001
2. Crea nuovo chatflow
3. Configura:
   - **LLM**: Ollama → `http://ollama:11434`
   - **Vector Store**: Qdrant → `http://qdrant:6333`
   - **Memory**: Qdrant collections

#### Workflow Multi-Agente
```yaml
nodes:
  - ChatOllama:
      baseUrl: "http://ollama:11434"
      modelName: "mistral"
  - QdrantVectorStore:
      url: "http://qdrant:6333"
  - ConversationChain:
      llm: "ChatOllama"
      memory: "QdrantVectorStore"
```

### 🧪 Testing e Monitoraggio

#### Health Check
```bash
./scripts/health_check.sh
```

#### Logs Monitoring
```bash
# Docker Compose
docker-compose logs -f [servizio]

# Kubernetes
kubectl logs -f deployment/ollama -n multi-agent-ecosystem
```

#### Performance Monitoring
```bash
# Container resources
docker stats

# Kubernetes resources  
kubectl top pods -n multi-agent-ecosystem
```

### 🔧 Troubleshooting

#### Problemi Comuni

**Ollama non risponde**
```bash
docker logs ollama
docker-compose restart ollama
```

**Open WebUI errore connessione**
```bash
docker exec open-webui curl http://ollama:11434/api/version
```

**CrewAI Python errors**
```bash
docker-compose build crewai --no-cache
docker exec -it crewai bash
```

**Kubernetes pods CrashLoopBackOff**
```bash
kubectl describe pod <pod-name> -n multi-agent-ecosystem
kubectl logs <pod-name> -n multi-agent-ecosystem
```

### 📈 Performance Tuning

#### Docker Resource Limits
```yaml
# In docker-compose.yml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 8G
        reservations:
          memory: 4G
```

#### Kubernetes Scaling
```bash
# Scale Ollama replicas
kubectl scale deployment ollama --replicas=2 -n multi-agent-ecosystem

# Auto-scaling
kubectl autoscale deployment ollama --cpu-percent=70 --min=1 --max=5 -n multi-agent-ecosystem
```

### 🔐 Sicurezza

#### Network Isolation
- Docker Compose usa rete `multi-agent-net`
- Kubernetes usa namespace `multi-agent-ecosystem`
- Secrets gestiti tramite Kubernetes Secrets

#### Credenziali Sicure
```bash
# Genera password sicure
openssl rand -base64 32  # Per POSTGRES_PASSWORD
openssl rand -base64 24  # Per NEXTCLOUD_ADMIN_PASSWORD
```

### 📚 Struttura Progetto

```
Multi_Agent_v2/
├── 📁 crewai/              # Framework Python multi-agenti
│   ├── main.py             # Agente analisi finanziaria
│   ├── requirements.txt    # Dipendenze Python
│   └── Dockerfile          # Container CrewAI
├── 📁 kubernetes/          # Configurazioni K8s
│   ├── 00-namespace.yml    # Namespace
│   ├── 02-qdrant.yml      # Database vettoriale
│   ├── 03-ollama.yml      # Backend LLM
│   ├── 04-open-webui.yml  # Interfaccia web
│   ├── 05-flowise.yml     # Orchestrazione visuale
│   └── 07-nextcloud.yml   # Storage stack
├── 📁 .vscode/             # Configurazione VSCode
│   ├── settings.json       # Impostazioni workspace
│   ├── tasks.json         # Task automation
│   └── launch.json        # Debug configuration
├── 📁 scripts/             # Script utilità
│   └── health_check.sh    # Verifica servizi
├── docker-compose.yml     # Orchestrazione Docker
├── .env.example           # Template variabili ambiente
└── setup_vscode_workspace.sh  # Setup automatico
```

### 🎓 Esempi d'Uso

#### Analisi Finanziaria con CrewAI
```bash
# Modifica ticker in crewai/main.py
sed -i 's/TSLA/AAPL/g' crewai/main.py

# Esegui analisi
docker exec -it crewai python main.py
```

#### Workflow RAG con FlowiseAI
1. Carica documenti in Nextcloud
2. Crea embeddings in Qdrant
3. Configura chatflow in FlowiseAI
4. Testa retrieval augmented generation

#### Multi-Agent Collaboration
- CrewAI per analisi strutturata
- FlowiseAI per orchestrazione workflow
- Open WebUI per interazione utente
- Qdrant per memoria condivisa

### 🚀 Prossimi Sviluppi

#### Funzionalità Pianificate
- [ ] Integrazione API esterne (news, mercati)
- [ ] Dashboard monitoring custom
- [ ] Template agenti pre-configurati
- [ ] Auto-scaling intelligente
- [ ] Pipeline CI/CD automatizzate

#### Contributi
Questo è un progetto di ricerca e sviluppo. Contributi e miglioramenti sono benvenuti!

### 📞 Supporto

Per problemi o domande:
1. Controlla la sezione Troubleshooting
2. Esegui `./scripts/health_check.sh`
3. Consulta i logs dei servizi
4. Apri issue su GitHub

---

**🎯 Sistema Multi-Agente Pronto per la Produzione!** 

Configurazione completa per sviluppo locale professionale con VSCode, Docker e Kubernetes.
