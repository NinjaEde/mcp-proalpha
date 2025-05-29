import os
import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger("mcp-proalpha")

DB_SERVER_HOST = os.getenv("DB_SERVER_HOST", "http://localhost")
DB_SERVER_PORT = os.getenv("DB_SERVER_PORT", "8080")
DB_API_KEY = os.getenv("DB_API_KEY")
SCHEMA_CACHE_PATH = os.getenv("SCHEMA_CACHE_PATH", "./schema_cache")

class DatabaseManager:
    def __init__(self):
        self.api_host = DB_SERVER_HOST.rstrip("/")
        self.api_port = DB_SERVER_PORT
        self.base_url = f"{self.api_host}:{self.api_port}"
        self.api_url = f"{self.base_url}/q/"
        self.api_key = DB_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.query_url = f"{self.base_url}/sql/query"
        self.session = None
        self.schema_cache = {
            "tables": {},
            "views": {},
            "relationships": []
        }
        self.schema_cache_dir = Path(SCHEMA_CACHE_PATH)
        self.schema_cache_dir.mkdir(exist_ok=True)
        try:
            self.refresh_schema_cache()
        except Exception as e:
            logger.error(f"Fehler beim Laden des Datenbankschemas: {e}")
            logger.warning("Der Server wird mit einem leeren Schema gestartet. Überprüfen Sie Ihre API-Verbindung und führen Sie 'refresh_schema' aus.")

    def connect(self) -> bool:
        try:
            self.session = requests.Session()
            self.session.headers.update(self.headers)
            health_url = f"{self.api_url}health"
            response = self.session.get(health_url, timeout=5)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Fehler bei der API-Verbindung: {e}")
            return False

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        query = query.strip()
        if not self._is_read_only(query):
            raise ValueError("Nur Read-Only-Abfragen sind erlaubt")
        if not self.session:
            if not self.connect():
                raise ConnectionError("Keine Verbindung zur API möglich")
        try:
            logger.info(f"SQL-Proxy-Request: GET {self.query_url} | query={query}")
            params = {"query": query}
            response = self.session.get(self.query_url, params=params)
            response.raise_for_status()
            data = response.json()
            if "error" in data:
                raise ValueError(f"API-Fehler: {data['error']}")
            if "results" in data:
                return data["results"]
            else:
                logger.warning("Unerwartete API-Antwortstruktur, versuche direktes Parsen")
                return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"Fehler bei der Ausführung der Abfrage über die API: {e}")
            raise

    def _is_read_only(self, query: str) -> bool:
        query = query.lower()
        allowed_prefixes = ["select ", "with ", "declare ", "print "]
        forbidden_keywords = [
            "insert ", "update ", "delete ", "drop ", "create ", "alter ", 
            "truncate ", "merge ", "exec ", "execute ", "sp_", "xp_"
        ]
        is_allowed = any(query.startswith(prefix) for prefix in allowed_prefixes)
        contains_forbidden = any(keyword in query for keyword in forbidden_keywords)
        return is_allowed and not contains_forbidden

    def get_database_schema(self) -> Dict[str, Any]:
        if not self.session:
            if not self.connect():
                raise ConnectionError("Keine Verbindung zur API möglich")
        try:
            schema_url = f"{self.api_url}schema"
            schema_response = self.session.get(schema_url, timeout=10)
            schema_response.raise_for_status()
            schema_data = schema_response.json()
            if "tables" in schema_data and "views" in schema_data and "relationships" in schema_data:
                logger.info("Schema erfolgreich über /schema-API abgerufen")
                return schema_data
            else:
                logger.warning("Schema-API liefert unerwartete Struktur, Rückfall auf Cache")
                return self.schema_cache
        except Exception as e:
            logger.error(f"Fehler beim Erfassen des Schemas: {e}")
            return self.schema_cache

    def refresh_schema_cache(self) -> None:
        schema = self.get_database_schema()
        self.schema_cache = schema
        cache_file = self.schema_cache_dir / "schema.json"
        with open(cache_file, "w") as f:
            json.dump(schema, f, indent=2)
        logger.info("Schema-Cache wurde aktualisiert")

    def get_table_sample(self, table_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        if table_name not in self.schema_cache["tables"]:
            raise ValueError(f"Tabelle '{table_name}' nicht gefunden")
        query = f"SELECT TOP {limit} * FROM [{table_name}]"
        return self.execute_query(query)
