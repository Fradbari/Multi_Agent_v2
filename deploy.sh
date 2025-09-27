#!/bin/bash
# deploy.sh - Script di deployment automatizzato

set -e

DEPLOYMENT_TYPE=${1:-docker}
ENVIRONMENT=${2:-local}

echo "🚀 Multi-Agent Deployment Script"
echo "Tipo: $DEPLOYMENT_TYPE | Ambiente: $ENVIRONMENT"
echo "=========================================="

case $DEPLOYMENT_TYPE in
    "docker")
        echo "📦 Deployment Docker Compose..."

        # Verifica che .env esista
        if [[ ! -f .env ]]; then
            echo "⚠️  File .env non trovato, copio da .env.example"
            cp .env.example .env
            echo "🔧 Modifica .env con le tue credenziali prima di continuare"
            exit 1
        fi

        # Build e start
        docker-compose down -v 2>/dev/null || true
        docker-compose up -d --build

        # Attendi che i servizi siano pronti
        echo "⏳ Attendo che i servizi siano pronti..."
        sleep 30

        # Scarica modelli Ollama
        echo "📥 Download modelli Ollama..."
        docker exec ollama ollama pull mistral || echo "⚠️  Errore download mistral"
        docker exec ollama ollama pull llama2:7b-chat || echo "⚠️  Errore download llama2"

        echo "✅ Deployment Docker completato!"
        ;;

    "kubernetes")
        echo "☸️  Deployment Kubernetes..."

        # Verifica kubectl
        if ! kubectl cluster-info > /dev/null 2>&1; then
            echo "❌ kubectl non configurato o cluster non raggiungibile"
            exit 1
        fi

        # Crea namespace
        kubectl apply -f kubernetes/00-namespace.yml

        # Crea secrets
        kubectl create secret generic nextcloud-secrets \
            --from-env-file=.env \
            --namespace=multi-agent-ecosystem \
            --dry-run=client -o yaml | kubectl apply -f -

        # Deploy servizi
        kubectl apply -f kubernetes/

        # Attendi che i pod siano pronti
        echo "⏳ Attendo che i pod siano pronti..."
        kubectl wait --for=condition=ready pod -l app=ollama -n multi-agent-ecosystem --timeout=300s
        kubectl wait --for=condition=ready pod -l app=qdrant -n multi-agent-ecosystem --timeout=300s

        echo "✅ Deployment Kubernetes completato!"
        ;;

    *)
        echo "❌ Tipo deployment non valido: $DEPLOYMENT_TYPE"
        echo "Usa: ./deploy.sh [docker|kubernetes] [local|prod]"
        exit 1
        ;;
esac

echo
echo "🌐 Servizi disponibili:"
echo "   - Open WebUI: http://localhost:3000"
echo "   - FlowiseAI: http://localhost:3001"  
echo "   - Nextcloud: http://localhost:8080"
echo "   - Qdrant: http://localhost:6333/dashboard"
echo
echo "🔍 Esegui './scripts/health_check.sh' per verificare lo stato"
