import os
import requests
import pytest
from app.database import DatabaseManager
from app.config import config

# Set test environment variables (override if needed)
os.environ["DB_SERVER_HOST"] = config.DB_SERVER_HOST
os.environ["DB_SERVER_PORT"] = config.DB_SERVER_PORT
os.environ["DB_API_KEY"] = config.DB_API_KEY or ""
os.environ["SCHEMA_CACHE_PATH"] = config.SCHEMA_CACHE_PATH

def api_available():
    try:
        r = requests.get(f"{config.DB_SERVER_HOST}:{config.DB_SERVER_PORT}/q/health", timeout=2)
        return r.status_code == 200
    except Exception:
        return False

@pytest.mark.skipif(not api_available(), reason="API-Server nicht erreichbar")
def test_database_integration():
    """Integrationstest: Testet die wichtigsten Datenbankmethoden mit echter API."""
    db = DatabaseManager()
    if not db.connect():
        pytest.fail("API nicht erreichbar, Integrationstest fehlgeschlagen.")
    # Teste get_database_schema
    schema = db.get_database_schema()
    assert isinstance(schema, dict)
    assert "tables" in schema
    # Teste execute_query (nur wenn Tabellen vorhanden)
    tables = list(schema.get("tables", {}).keys())
    if tables:
        table = tables[0]
        query = f"SELECT TOP 1 * FROM [{table}]"
        results = db.execute_query(query)
        assert isinstance(results, list)
        # Teste get_table_sample
        sample = db.get_table_sample(table, limit=1)
        assert isinstance(sample, list)
    else:
        pytest.fail("Keine Tabellen im Schema gefunden.")

@pytest.mark.skipif(not api_available(), reason="API-Server nicht erreichbar")
def test_refresh_schema_cache(tmp_path):
    """Integrationstest: Testet refresh_schema_cache (Cache-Update und Datei)."""
    os.environ["SCHEMA_CACHE_PATH"] = str(tmp_path)
    db = DatabaseManager()
    if not db.connect():
        pytest.fail("API nicht erreichbar, Integrationstest fehlgeschlagen.")
    db.refresh_schema_cache()
    # Prüfe, ob die Datei existiert
    cache_file = tmp_path / "schema.json"
    assert cache_file.exists()
    # Prüfe, ob schema_cache ein dict mit 'tables' ist
    assert isinstance(db.schema_cache, dict)
    assert "tables" in db.schema_cache

@pytest.mark.skipif(not api_available(), reason="API-Server nicht erreichbar")
def test_execute_query_s_kunde():
    """Integrationstest: SELECT TOP 10 * FROM [s_kunden]"""
    db = DatabaseManager()
    if not db.connect():
        pytest.fail("API nicht erreichbar, Test übersprungen.")
    schema = db.get_database_schema()
    if "s_kunden" not in schema.get("tables", {}):
        pytest.fail("Tabelle 's_kunden' nicht im Schema gefunden.")
    results = db.execute_query("SELECT TOP 10 * FROM [s_kunden]")
    assert isinstance(results, list)
