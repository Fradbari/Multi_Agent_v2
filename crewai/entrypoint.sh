#!/bin/bash

# Aspetta che Ollama sia disponibile
echo "🔍 Checking Ollama availability..."
until curl -s http://ollama:11434/api/tags > /dev/null 2>&1; do
    echo "⏳ Waiting for Ollama service..."
    sleep 5
done

echo "✅ Ollama service is ready!"

# Verifica se il modello è già presente
MODEL_EXISTS=$(curl -s http://ollama:11434/api/tags | grep -c "mistral-nemo:12b-instruct-2407-q5_K_M")

if [ "$MODEL_EXISTS" -eq 0 ]; then
    echo "📥 Downloading model mistral-nemo:12b-instruct-2407-q5_K_M..."
    curl -X POST http://ollama:11434/api/pull \
        -H "Content-Type: application/json" \
        -d '{"name": "mistral-nemo:12b-instruct-2407-q5_K_M"}'
    echo "✅ Model download completed!"
else
    echo "✅ Model already exists, skipping download."
fi

# Avvia l'applicazione CrewAI
echo "🚀 Starting CrewAI Financial Analysis..."
exec python main.py
