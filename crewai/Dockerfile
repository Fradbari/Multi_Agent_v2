# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Creazione dell'ambiente virtuale
RUN python -m venv /usr/src/app/crewai/.venv

# Attivazione dell'ambiente virtuale
ENV PATH="/usr/src/app/crewai/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/usr/src/app/crewai/.venv"

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt ./
RUN /usr/src/app/crewai/.venv/bin/pip install --upgrade pip && \
    /usr/src/app/crewai/.venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container
COPY . .

# Command to run the application
#CMD ["python", "main.py"]
CMD ["/usr/src/app/crewai/.venv/bin/python", "main.py"]