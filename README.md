# Multi-Agent AI Ecosystem on Kubernetes

This repository contains the configuration to deploy a comprehensive, self-hosted AI agent ecosystem using Docker and Kubernetes. The architecture is designed to be modular and scalable, providing a powerful platform for local Large Language Model (LLM) interaction, agent orchestration, and data management.

## Architecture Overview

The ecosystem is composed of the following core components, all deployed within a dedicated Kubernetes namespace:

- **Local LLM Backend:** `Ollama` serves as the core engine, running and exposing LLMs locally.
- **Web Interface:** `Open WebUI` provides a user-friendly chat and playground interface for interacting with the local LLMs.
- **Vector Database:** `Qdrant` acts as the vector store for embeddings, enabling Retrieval-Augmented Generation (RAG) and providing long-term memory for AI agents.
- **Agent Orchestration:**
  - `FlowiseAI`: A visual, no-code/low-code tool for building and orchestrating agentic workflows.
  - `CrewAI`: A Python-based framework for creating sophisticated, role-based multi-agent systems. This deployment includes a financial analysis example that runs as a Kubernetes Job.
- **Data Storage:** `Nextcloud` offers a self-hosted cloud storage solution, integrated with a `Postgres` database and `Redis` for caching.

## Prerequisites

-   A running Kubernetes cluster (e.g., from Docker Desktop, Minikube, etc.).
-   `kubectl` command-line tool configured to connect to your cluster.
-   Docker (to build the custom CrewAI image).
-   A container registry (e.g., Docker Hub, GHCR, or a local registry) that your Kubernetes cluster can access.

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Multi_Agent_v2.git
cd Multi_Agent_v2
```

### 2. Configure Secrets

The deployment uses a Kubernetes Secret to manage sensitive information like database passwords and admin credentials.

First, create your personal `.env` file from the provided example:
```bash
cp .env.example .env
```
Next, **edit the `.env` file** and replace the placeholder values with your own secure passwords.

### 3. Build and Push the CrewAI Docker Image

The CrewAI agent runs as a custom Docker image. You need to build this image and push it to a container registry that your Kubernetes cluster can pull from.

```bash
# Replace 'your-registry/your-repo' with your actual registry path
export DOCKER_IMAGE="your-registry/your-repo/crewai-financial-agent:latest"

# Build the image
docker build -t $DOCKER_IMAGE ./crewai

# Push the image
docker push $DOCKER_IMAGE
```

After pushing the image, you **must update the image name** in the Kubernetes job manifest. Open `kubernetes/06-crewai-job.yml` and change the `image:` field to the `$DOCKER_IMAGE` path you just used.

### 4. Deploy to Kubernetes

First, create the namespace that will contain all the resources:
```bash
kubectl apply -f kubernetes/00-namespace.yml
```

Next, create the Kubernetes secret from your `.env` file:
```bash
kubectl create secret generic nextcloud-secrets \
  --from-env-file=.env \
  --namespace=multi-agent-ecosystem
```
*Note: This command replaces the placeholder secret definition in `01-secrets.yml`. The file exists to document the required keys.*

Finally, apply all the remaining manifests to deploy the applications:
```bash
# Apply all service, deployment, and volume claim manifests
kubectl apply -f kubernetes/
```
This command will deploy Qdrant, Ollama, Open WebUI, Flowise, Nextcloud (with its database and cache), and run the CrewAI financial analysis job.

### 5. Check Deployment Status

You can monitor the status of the pods as they are being created:
```bash
kubectl get pods -n multi-agent-ecosystem -w
```
Wait until all pods are in the `Running` or `Completed` (for the CrewAI job) state.

## Accessing Services

The services are exposed via `LoadBalancer`. In a local cluster like Docker Desktop, this makes them available on `localhost` at the specified ports.

-   **Open WebUI:** `http://localhost:3000`
-   **FlowiseAI:** `http://localhost:3001`
-   **Nextcloud:** `http://localhost:8080`
-   **Qdrant Dashboard:** `http://localhost:6333/dashboard`
-   **Ollama API:** `http://localhost:11434`

To see the output of the financial analysis job, you can view the logs of the completed pod:
```bash
# Get the name of the pod created by the job
POD_NAME=$(kubectl get pods -n multi-agent-ecosystem -l job-name=crewai-financial-analysis-job -o jsonpath='{.items[0].metadata.name}')

# View the logs
kubectl logs $POD_NAME -n multi-agent-ecosystem
```