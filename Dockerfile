FROM python:3.11-slim

WORKDIR /app

# Systemabhängige Pakete (falls benötigt, z.B. für build tools)
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Installiere Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Codes
COPY . .

# Standard-Entrypoint (kann durch docker-compose überschrieben werden)
CMD ["python", "-m", "app"]
