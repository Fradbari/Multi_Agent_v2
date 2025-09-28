# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Crea le directory necessarie
RUN mkdir -p /app/storage /app/outputs

# Creazione dell'ambiente virtuale
RUN python -m venv /usr/src/app/crewai/.venv

# Attivazione dell'ambiente virtuale
ENV PATH="/usr/src/app/crewai/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/usr/src/app/crewai/.venv"

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt ./

# Install dependencies
RUN /usr/src/app/crewai/.venv/bin/pip install --upgrade pip && \
    /usr/src/app/crewai/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Assicurati che le directory abbiano i permessi corretti
RUN chmod -R 755 /app/storage /app/outputs

# Install Ollama and pull the Mistral model
RUN curl -fsSL https://ollama.ai/install.sh | sh
RUN ollama serve & sleep 5 && ollama pull mistral-nemo:12b-instruct-2407-q5_K_M

# Command to run the application
CMD ["/usr/src/app/crewai/.venv/bin/python", "main.py"]