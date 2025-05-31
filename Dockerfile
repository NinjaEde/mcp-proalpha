FROM python:3.13-alpine

WORKDIR /app

# Systemabhängige Pakete (Alpine: build-base statt build-essential)
RUN apk add --no-cache build-base

# Installiere Abhängigkeiten
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den Rest des Codes
COPY . .

# Standard-Entrypoint (kann durch docker-compose überschrieben werden)
CMD ["python", "-m", "app"]
