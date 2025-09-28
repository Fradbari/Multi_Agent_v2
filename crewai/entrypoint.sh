#!/bin/bash

# Exit on any error
set -e

# Function to handle errors
handle_error() {
    echo "❌ Error occurred at line $1"
    echo "🔄 Retrying in 30 seconds..."
    sleep 30
    exit 1
}

# Trap errors
trap 'handle_error ${LINENO}' ERR

# Aspetta che Ollama sia disponibile
echo "🔍 Checking Ollama availability..."
RETRY_COUNT=0
MAX_RETRIES=30

until curl -s http://ollama:11434/api/tags > /dev/null 2>&1; do
    echo "⏳ Waiting for Ollama service... (attempt $((++RETRY_COUNT))/$MAX_RETRIES)"
    
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "❌ Failed to connect to Ollama after $MAX_RETRIES attempts"
        exit 1
    fi
    
    sleep 10
done

echo "✅ Ollama service is ready!"

# Verifica se il modello è già presente
echo "🔍 Checking if model exists..."
MODEL_EXISTS=$(curl -s http://ollama:11434/api/tags | grep -c "mistral-nemo:12b-instruct-2407-q5_K_M" || echo "0")

if [ "$MODEL_EXISTS" -eq 0 ]; then
    echo "📥 Downloading model mistral-nemo:12b-instruct-2407-q5_K_M..."
    
    # Download con gestione errori
    DOWNLOAD_RESPONSE=$(curl -s -w "%{http_code}" -X POST http://ollama:11434/api/pull \
        -H "Content-Type: application/json" \
        -d '{"name": "mistral-nemo:12b-instruct-2407-q5_K_M"}')
    
    HTTP_CODE="${DOWNLOAD_RESPONSE: -3}"
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "✅ Model download completed!"
        
        # Verifica che il modello sia effettivamente disponibile
        sleep 5
        FINAL_CHECK=$(curl -s http://ollama:11434/api/tags | grep -c "mistral-nemo:12b-instruct-2407-q5_K_M" || echo "0")
        
        if [ "$FINAL_CHECK" -eq 0 ]; then
            echo "❌ Model download failed - model not found after download"
            exit 1
        fi
        
        echo "✅ Model verified and ready!"
    else
        echo "❌ Model download failed with HTTP code: $HTTP_CODE"
        echo "Response: ${DOWNLOAD_RESPONSE%???}"
        exit 1
    fi
else
    echo "✅ Model already exists, skipping download."
fi

# Avvia l'applicazione CrewAI
echo "🚀 Starting CrewAI Financial Analysis..."
exec python main.py
