#!/bin/bash
# setup_vscode_workspace.sh - Configurazione automatica workspace VSCode

set -e

echo "🚀 Configurazione Multi_Agent_v2 VSCode Workspace"
echo "=================================================="

# Crea directory .vscode se non esiste
mkdir -p .vscode

# Configurazione settings.json
cat > .vscode/settings.json << 'EOF'
{
    "docker.containers.groupBy": "Compose Project Name",
    "kubernetes.defaultNamespace": "multi-agent-ecosystem",
    "python.defaultInterpreterPath": "./crewai/.venv/bin/python",
    "python.analysis.extraPaths": ["./crewai"],
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "remote.containers.defaultExtensions": [
        "ms-vscode.vscode-json",
        "ms-python.python",
        "ms-kubernetes-tools.vscode-kubernetes-tools",
        "ms-vscode.docker"
    ],
    "files.watcherExclude": {
        "**/node_modules/**": true,
        "**/.git/objects/**": true,
        "**/data/**": true,
        "**/volumes/**": true,
        "**/.venv/**": true
    },
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
EOF

# Configurazione tasks.json
cat > .vscode/tasks.json << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "🐳 Docker: Build and Start All",
            "type": "shell",
            "command": "docker-compose",
            "args": ["up", "-d", "--build"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "🛑 Docker: Stop All Services",
            "type": "shell",
            "command": "docker-compose",
            "args": ["down"],
            "group": "build"
        },
        {
            "label": "🔄 Docker: Restart Service",
            "type": "shell",
            "command": "docker-compose",
            "args": ["restart", "${input:serviceName}"],
            "group": "build"
        },
        {
            "label": "☸️ Kubernetes: Deploy All",
            "type": "shell",
            "command": "bash",
            "args": ["-c", "kubectl apply -f kubernetes/00-namespace.yml && kubectl create secret generic nextcloud-secrets --from-env-file=.env --namespace=multi-agent-ecosystem --dry-run=client -o yaml | kubectl apply -f - && kubectl apply -f kubernetes/"],
            "group": "build"
        },
        {
            "label": "🤖 Ollama: Pull Models",
            "type": "shell",
            "command": "bash",
            "args": ["-c", "docker exec ollama ollama pull mistral && docker exec ollama ollama pull llama2:7b-chat && docker exec ollama ollama pull codellama:7b"],
            "group": "build"
        },
        {
            "label": "🔬 CrewAI: Run Analysis",
            "type": "shell",
            "command": "docker",
            "args": ["exec", "-it", "crewai", "python", "main.py"],
            "group": "test"
        },
        {
            "label": "🏥 System: Health Check",
            "type": "shell",
            "command": "bash",
            "args": ["./scripts/health_check.sh"],
            "group": "test"
        }
    ],
    "inputs": [
        {
            "id": "serviceName",
            "description": "Nome del servizio da riavviare",
            "default": "ollama",
            "type": "pickString",
            "options": [
                "ollama",
                "open-webui", 
                "flowise",
                "crewai",
                "qdrant",
                "nextcloud",
                "nextcloud-db",
                "nextcloud-redis"
            ]
        }
    ]
}
EOF

# Configurazione launch.json
cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "🐍 Python: Debug CrewAI Main",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/crewai/main.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/crewai",
            "env": {
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "PYTHONPATH": "${workspaceFolder}/crewai"
            }
        },
        {
            "name": "🐍 Python: Debug Custom Agent",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/crewai/custom_agent.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}/crewai",
            "env": {
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "PYTHONPATH": "${workspaceFolder}/crewai"
            }
        }
    ]
}
EOF

# Configurazione extensions.json
cat > .vscode/extensions.json << 'EOF'
{
    "recommendations": [
        "ms-vscode.docker",
        "ms-kubernetes-tools.vscode-kubernetes-tools",
        "ms-python.python",
        "ms-python.black-formatter",
        "ms-python.pylint",
        "ms-vscode.vscode-json",
        "ms-vscode-remote.remote-containers",
        "hashicorp.terraform",
        "redhat.vscode-yaml",
        "formulahendry.docker-explorer",
        "ms-vscode.vscode-yaml"
    ]
}
EOF

# Crea directory scripts
mkdir -p scripts

# Health check script
cat > scripts/health_check.sh << 'EOF'
#!/bin/bash
echo "🏥 Multi-Agent System Health Check"
echo "=================================="
echo

# Controlla Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker: NOT RUNNING"
    exit 1
fi
echo "✅ Docker: RUNNING"

# Controlla servizi
services=("ollama:11434" "open-webui:3000" "flowise:3001" "qdrant:6333" "nextcloud:8080")

for service in "${services[@]}"; do
    name=${service%:*}
    port=${service#*:}

    if curl -s --max-time 5 http://localhost:$port > /dev/null 2>&1; then
        echo "✅ $name: OK (port $port)"
    else
        echo "❌ $name: FAIL (port $port)"
    fi
done

echo
echo "🔍 Container Status:"
docker-compose ps --format "table {{.Name}}\t{{.State}}\t{{.Ports}}"
EOF

chmod +x scripts/health_check.sh

echo "✅ Configurazione VSCode completata!"
echo "📁 File creati:"
echo "   - .vscode/settings.json"
echo "   - .vscode/tasks.json" 
echo "   - .vscode/launch.json"
echo "   - .vscode/extensions.json"
echo "   - scripts/health_check.sh"
echo
echo "🎯 Prossimi passi:"
echo "   1. Riavvia VSCode per applicare le configurazioni"
echo "   2. Installa le estensioni raccomandate"
echo "   3. Usa Ctrl+Shift+P > Tasks: Run Task per eseguire i task"
