# =============================================================================
# STAGE 1: Dependencies and Build Environment
# =============================================================================
FROM python:3.11-slim as dependencies

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# =============================================================================
# STAGE 2: Application Runtime (Production)
# =============================================================================
FROM python:3.11-slim as production

# Labels for better container management
LABEL maintainer="FDL"
LABEL version="1.0.0"
LABEL description="CrewAI Financial Analysis API Service"

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"

# Create non-root user for security
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m -s /bin/bash appuser

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Create required directories with proper permissions
RUN mkdir -p /app/storage /app/outputs && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser ./app ./app
RUN chmod -R 755 /app/storage /app/outputs

# Create entrypoint script for flexible configuration
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for Ollama service if specified\n\
if [ ! -z "$OLLAMA_BASE_URL" ]; then\n\
    echo "Waiting for Ollama service at $OLLAMA_BASE_URL..."\n\
    until curl -f "$OLLAMA_BASE_URL/api/tags" >/dev/null 2>&1; do\n\
        echo "Ollama not ready, waiting 5 seconds..."\n\
        sleep 5\n\
    done\n\
    echo "Ollama service is ready!"\n\
fi\n\
\n\
# Start the FastAPI application\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --log-level info\n\
' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh && \
    chown appuser:appuser /app/entrypoint.sh

# Switch to non-root user
USER appuser

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose application port
EXPOSE 8000

# Use entrypoint for startup
ENTRYPOINT ["/app/entrypoint.sh"]

# =============================================================================
# STAGE 3: Development Environment (Optional)
# =============================================================================
FROM production as development

USER root

# Install additional development tools
RUN pip install --no-cache-dir \
    pytest \
    black \
    isort \
    mypy \
    flake8 \
    pytest-asyncio

# Switch back to appuser
USER appuser

# Override CMD for development with hot reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
