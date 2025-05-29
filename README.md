# ProAlpha MCP Server

Ein Model-Context-Protocol (MCP) Server für ProAlpha MSSQL-Datenbanken, der eine Read-Only-Schnittstelle zu Ihrer Datenbank bereitstellt und automatisch Schemas erfasst.


## Funktionen

- Verbindung zu ProAlpha MSSQL-Datenbanken
- Automatische Erfassung des Datenbankschemas
- Bereitstellung von Tabellenstrukturen als MCP-Ressourcen
- Tools für Read-Only SQL-Abfragen
- Prompts für gängige Datenanalyseaufgaben
- REST-API für direkten Zugriff auf Schemainformationen

## Anforderungen

- Python 3.8 oder höher
- ODBC-Treiber für SQL Server
- Zugriff auf eine ProAlpha MSSQL-Datenbank

## Installation

1. Repository klonen oder herunterladen

2. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

3. Konfigurationsdateien erstellen:

Erstellen Sie eine `.env` Datei mit den folgenden Einstellungen:

```ini
DB_SERVER=your_server_address
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_DRIVER={ODBC Driver 17 for SQL Server}
MCP_PORT=8000
MCP_HOST=0.0.0.0
SCHEMA_CACHE_PATH=./schema_cache
```

4. Optional: Erstellen Sie eine Standard-Konfiguration für MCP-Prompts:

```bash
./generate_prompts.py
```

Dies erstellt eine `mcp_prompts.json`-Datei mit Standardvorlagen für Prompts und Toolbeispiele.

## Verwendung

### Server starten

```bash
python main.py
```

Der Server wird standardmäßig auf Port 8000 gestartet.

### REST-API verwenden

- `GET /api/schema` - Gibt das gesamte Datenbankschema zurück
- `GET /api/schema/tables` - Gibt eine Liste aller Tabellen zurück
- `GET /api/schema/tables/{table_name}` - Gibt das Schema einer bestimmten Tabelle zurück
- `GET /api/schema/views` - Gibt eine Liste aller Views zurück
- `GET /api/schema/views/{view_name}` - Gibt das Schema einer bestimmten View zurück
- `GET /api/schema/relationships` - Gibt alle Tabellenbeziehungen zurück
- `POST /api/query` - Führt eine Read-Only-SQL-Abfrage aus
- `POST /api/schema/refresh` - Aktualisiert den Schema-Cache

### MCP-Endpunkt

Der MCP-Endpunkt ist über die SSE-Schnittstelle (Server-Sent Events) erreichbar:
- `/sse` - SSE-Endpunkt für die MCP-Kommunikation
- `/messages/` - Endpunkt für MCP-Nachrichten

## MCP-Ressourcen

Der Server stellt folgende MCP-Ressourcen bereit:

- `database_schema` - Das vollständige Datenbankschema
- `table_{name}` - Schema jeder Tabelle
- `view_{name}` - Schema jeder View
- `relationships` - Beziehungen zwischen den Tabellen

## MCP-Tools

Der Server stellt folgende MCP-Tools bereit:

- `execute_sql` - Führt eine Read-Only-SQL-Abfrage aus
- `get_table_sample` - Gibt eine Stichprobe der Daten einer Tabelle zurück
- `refresh_schema` - Aktualisiert den Schema-Cache
- `generate_table_documentation` - Erstellt eine detaillierte Dokumentation einer Tabelle
- `search_schema` - Sucht nach Tabellen und Spalten im Datenbankschema

## Testen des Servers

Das Repository enthält ein Test-Skript, mit dem die grundlegende Funktionalität des Servers überprüft werden kann:

```bash
# Server in einem Terminal starten
python main.py

# In einem anderen Terminal das Test-Skript ausführen
./test_server.py
```

Das Test-Skript überprüft die Web-API-Endpunkte und gibt Informationen zu deren Status aus.

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

### Tabellendokumentation erstellen

```json
{
  "resources": [],
  "tools": [
    {
      "id": "generate_table_documentation",
      "parameters": {
        "table_name": "BeispielTabelle",
        "include_sample_data": true
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

## Lizenz

MIT