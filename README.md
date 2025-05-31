# ProAlpha MCP Server

Ein Model-Context-Protocol (MCP) Server für ProAlpha MSSQL-Datenbanken, der eine Read-Only-Schnittstelle zu Ihrer Datenbank bereitstellt und automatisch Schemas erfasst.

## Funktionen

- Verbindung zu ProAlpha MSSQL-Datenbanken
- Automatische Erfassung des Datenbankschemas
- Bereitstellung von Tabellenstrukturen als MCP-Ressourcen
- Tools für Read-Only SQL-Abfragen
- Prompts für gängige Datenanalyseaufgaben

## Anforderungen

- Python 3.8 oder höher
- Zugriff auf eine laufende ProAlpha-API (siehe .env: DB_SERVER_HOST, DB_SERVER_PORT, DB_API_KEY)
- Eine ProAlpha MSSQL-Datenbank (über die API erreichbar)

> **Hinweis:** Ein ODBC-Treiber für SQL Server wird nur auf dem API-Server benötigt, der die Verbindung zur MSSQL-Datenbank herstellt. Für den MCP-Server selbst ist keine ODBC-Installation erforderlich.

## Installation

1. Repository klonen oder herunterladen

2. Neue Umgebung mit conda anlegen (empfohlen):

```bash
conda create -n mcp-proalpha python=3.11
conda activate mcp-proalpha
```

3. uv installieren (falls nicht vorhanden):

```bash
pip install uv
```

4. Abhängigkeiten installieren:

```bash
uv pip install -r requirements.txt
```

> **Hinweis:** uv ist ein schneller, moderner Ersatz für pip und wird für die Installation empfohlen. Alternativ kann weiterhin pip verwendet werden.

5. Konfigurationsdateien erstellen:

Erstellen Sie eine `.env` Datei mit den folgenden Einstellungen:

```ini
DB_SERVER_PORT=8080
DB_SERVER_HOST=http://localhost
DB_API_KEY=your_api_key
MCP_PORT=8000
MCP_HOST=0.0.0.0
API_SERVER_PORT=8081
API_SERVER_HOST=http://localhost
SCHEMA_CACHE_PATH=./schema_cache
# Transport-Protokoll für den MCP-Server: stdio, streamable-http oder sse
MCP_TRANSPORT=streamable-http
```

- **MCP_TRANSPORT** bestimmt das Transport-Protokoll für den Server:

| Transport-Protokoll   | Beschreibung                                         | Endpoint                         |
|-----------------------|------------------------------------------------------|----------------------------------|
| streamable-http       | Empfohlen für Web-Deployments  (Default)             | `http://localhost:8000/mcp`      |
| stdio                 | Für lokale Tools und CLI-Skripte                     |                                  |
| sse                   | Für Kompatibilität mit bestehenden SSE-Clients       | `http://localhost:8000/sse`      |

6. Optional: Erstellen Sie eine Standard-Konfiguration für MCP-Prompts:

```bash
./app/generate_prompts.py
```

Dies erstellt eine `mcp_prompts.json`-Datei mit Standardvorlagen für Prompts und Toolbeispiele.

## Verwendung

### Server starten

Der Server verwendet das in der `.env` konfigurierte Transport-Protokoll (`MCP_TRANSPORT`).

- Für lokale CLI-Tools: `MCP_TRANSPORT=stdio`
- Für Web-Deployments: `MCP_TRANSPORT=streamable-http`
- Für SSE-Clients: `MCP_TRANSPORT=sse`

```bash
python -m app
```

(optional) mit fastmcp-cli:
```bash
fastmcp run mcp-proalpha.py
```

Der Server wird standardmäßig auf Port 8000 gestartet (außer bei stdio).

### Verbindung mit MCP Inspector

```bash
npx @modelcontextprotocol/inspector python -m app
```
Öffnen Sie den [MCP Inspector](http://127.0.0.1:6274/) und verbinden Sie sich mit Ihrem Server (z.B. `http://localhost:8000/sse`).

#### Alternativ: MCP Inspector mit uvx

Falls Sie uvx (Node.js-Toolrunner von uv) installiert haben, können Sie den Inspector auch so starten:

```bash
uvx @modelcontextprotocol/inspector python -m app
```

> **Hinweis:** uvx funktioniert analog zu npx, ist aber oft schneller und kann für Node.js-basierte Tools verwendet werden.

### HTTP REST-API verwenden

Die REST-API ist parallel zum MCP-Server auf Port 8000 verfügbar. Beispiele für Endpunkte:

- `GET /api/schema` – Gibt das gesamte Datenbankschema zurück
- `GET /api/schema/tables` – Gibt eine Liste aller Tabellen zurück
- `GET /api/schema/tables/{table_name}` – Gibt das Schema einer bestimmten Tabelle zurück
- `GET /api/schema/views` – Gibt eine Liste aller Views zurück
- `GET /api/schema/views/{view_name}` – Gibt das Schema einer bestimmten View zurück
- `GET /api/schema/relationships` – Gibt alle Tabellenbeziehungen zurück
- `POST /api/query` – Führt eine Read-Only-SQL-Abfrage aus (JSON: `{ "query": "SELECT ..." }`)
- `POST /api/schema/refresh` – Aktualisiert den Schema-Cache
- `GET /api/tools` – Gibt eine Liste aller verfügbaren Tools mit Name, Beschreibung und Parametern zurück (Tool-Discovery, analog zu `list_tools` im MCP-Server)

Beispiel für eine SQL-Abfrage per curl:

```bash
curl -X POST http://localhost:8000/api/query -H "Content-Type: application/json" -d '{"query": "SELECT TOP 5 * FROM BeispielTabelle"}'
```

## MCP-Ressourcen

Der Server stellt folgende MCP-Ressourcen bereit:

- `resource://database_schema` – Das vollständige Datenbankschema
- `table://{table_name}` – Schema jeder Tabelle
- `view://{view_name}` – Schema jeder View
- `resource://relationships` – Beziehungen zwischen den Tabellen

## MCP-Tools

Der Server stellt folgende MCP-Tools bereit:

- `execute_sql` – Führt eine Read-Only-SQL-Abfrage aus
- `get_table_sample` – Gibt eine Stichprobe der Daten einer Tabelle zurück
- `refresh_schema` – Aktualisiert den Schema-Cache
- `list_tools` – Gibt eine Liste aller verfügbaren Tools mit Beschreibung und Parametern zurück (nützlich für LLMs und Clients zur Tool-Discovery)

## Testen des Servers

Das Repository enthält ein Test-Skript, mit dem die grundlegende Funktionalität des Servers überprüft werden kann:

```bash
# Server in einem Terminal starten
python -m app

# In einem anderen Terminal das Test-Skript ausführen
./test_server.py
```

Das Test-Skript prüft die MCP-Serverfunktionalität und kann auch REST-API-Endpunkte testen.

## Beispiel für MCP-Anfragen

### SQL-Abfrage ausführen

```json
{
  "resources": [],
  "tools": [
    {
      "id": "execute_sql",
      "parameters": {
        "query": "SELECT TOP 10 * FROM BeispielTabelle"
      }
    }
  ]
}
```

### Tabellendaten abrufen

```json
{
  "resources": [],
  "tools": [
    {
      "id": "get_table_sample",
      "parameters": {
        "table_name": "BeispielTabelle",
        "limit": 5
      }
    }
  ]
}
```

## Integration mit LLMs

Dieser MCP-Server ist kompatibel mit jedem LLM, das das Model-Context-Protocol unterstützt. 

### Beispiel-Prompts

#### Datenbankanalyse

```
Analysiere die Tabelle [TabellenName] und beschreibe ihre Struktur und Beziehungen.
```

#### Datenabfrage

```
Schreibe eine SQL-Abfrage, um [Geschäftsfrage] zu beantworten.
```

#### Schema-Erkundung

```
Finde alle Tabellen und Spalten, die mit [Suchbegriff] zu tun haben könnten.
```

> **Hinweis:** Mit dem Tool `list_tools` können LLMs und Clients alle verfügbaren Tools und deren Parameter dynamisch abfragen und so die Interaktion automatisieren oder Vorschläge generieren.

## Lizenz

MIT ([siehe LICENSE](./LICENSE))