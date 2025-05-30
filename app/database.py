import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Any
from .config import config

logger = logging.getLogger("mcp-proalpha")

class DatabaseManager:
    def __init__(self):
        self.db_host = config.DB_SERVER_HOST.rstrip("/")
        self.db_port = config.DB_SERVER_PORT
        self.db_url = f"{self.db_host}:{self.db_port}"

        self.api_host = config.API_SERVER_HOST.rstrip("/")
        self.api_port = config.API_SERVER_PORT
        self.api_url = f"{self.api_host}:{self.api_port}/api/"        

        self.api_key = config.DB_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.query_url = f"{self.db_url}/sql/query"
        self.health_url = f"{self.db_url}/q/health"

        self.session = None
        self.schema_cache = {
            "tables": {},
            "views": {},
            "relationships": []
        }
        self.schema_cache_dir = Path(config.SCHEMA_CACHE_PATH)
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
            response = self.session.get(self.health_url, timeout=5)
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
            # Entscheide GET oder POST je nach Query
            if "\n" in query or len(query) > 120:
                logger.info(f"SQL-Proxy-Request: POST {self.query_url} | query={query}")
                response = self.session.post(self.query_url, json={"query": query})
            else:
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
        cache_file = self.schema_cache_dir / "schema.json"
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    schema = json.load(f)
                logger.info("Schema erfolgreich aus Cache geladen")
                return schema
            except Exception as e:
                logger.error(f"Fehler beim Laden des Schemas aus dem Cache: {e}")
                return self.schema_cache
        else:
            logger.warning("Kein Schema-Cache gefunden, Rückfall auf leeres Schema")
            return self.schema_cache

    def refresh_schema_cache(self) -> None:
        if not self.session:
            if not self.connect():
                raise ConnectionError("Keine Verbindung zur API möglich")
        try:
            # Tabellen abfragen
            tables_query = """
                SELECT TABLE_NAME, TABLE_TYPE 
                FROM INFORMATION_SCHEMA.TABLES
            """
            tables = self.execute_query(tables_query)
            # Spalten abfragen
            columns_query = """
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
                FROM INFORMATION_SCHEMA.COLUMNS
            """
            columns = self.execute_query(columns_query)
            # Views abfragen
            views_query = """
                SELECT TABLE_NAME
                FROM INFORMATION_SCHEMA.VIEWS
            """
            views = self.execute_query(views_query)
            # Beziehungen (Foreign Keys) abfragen
            relationships_query = """
                SELECT
                    fk.name AS FK_Name,
                    tp.name AS ParentTable,
                    tr.name AS ReferencedTable,
                    cp.name AS ParentColumn,
                    cr.name AS ReferencedColumn
                FROM sys.foreign_keys fk
                INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
                INNER JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
                INNER JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
                INNER JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
                INNER JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
            """
            relationships = self.execute_query(relationships_query)

            # Struktur für das Schema
            tables_dict: dict[str, dict] = {}
            views_dict: dict[str, dict] = {}
            schema = {
                "tables": tables_dict,
                "views": views_dict,
                "relationships": relationships
            }
            # Tabellen und Spalten zuordnen
            for table in tables:
                tname = table["TABLE_NAME"]
                tables_dict[tname] = {
                    "type": table["TABLE_TYPE"],
                    "columns": [col for col in columns if col["TABLE_NAME"] == tname]
                }
            # Views zuordnen
            for view in views:
                vname = view["TABLE_NAME"]
                views_dict[vname] = {
                    "columns": [col for col in columns if col["TABLE_NAME"] == vname]
                }
            # Schreibe JSON-Dateien
            cache_dir = self.schema_cache_dir
            (cache_dir / "tables").mkdir(exist_ok=True)
            (cache_dir / "views").mkdir(exist_ok=True)
            # Gesamtschema
            with open(cache_dir / "schema.json", "w") as f:
                json.dump(schema, f, indent=2)
            # Einzelne Tabellen
            for tname, tdata in tables_dict.items():
                with open(cache_dir / "tables" / f"{tname}.json", "w") as f:
                    json.dump(tdata, f, indent=2)
            # Einzelne Views
            for vname, vdata in views_dict.items():
                with open(cache_dir / "views" / f"{vname}.json", "w") as f:
                    json.dump(vdata, f, indent=2)
            # Beziehungen
            with open(cache_dir / "relationships.json", "w") as f:
                json.dump(relationships, f, indent=2)
            self.schema_cache = schema
            logger.info("Schema und Cache-Dateien wurden direkt aus der Datenbank aktualisiert")
        except Exception as e:
            logger.error(f"Fehler beim Erfassen und Schreiben des Schemas: {e}")

    def get_table_sample(self, table_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        if table_name not in self.schema_cache["tables"]:
            raise ValueError(f"Tabelle '{table_name}' nicht gefunden")
        query = f"SELECT TOP {limit} * FROM [{table_name}]"
        return self.execute_query(query)
