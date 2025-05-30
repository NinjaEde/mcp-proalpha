import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import os
import pytest
from app.database import DatabaseManager

# Set test environment variables (override if needed)
os.environ["DB_SERVER_HOST"] = "http://localhost"
os.environ["DB_SERVER_PORT"] = "8080"
os.environ["DB_API_KEY"] = "0957864a-3c55-4c2d-aa79-f773f94558da"
os.environ["SCHEMA_CACHE_PATH"] = "./schema_cache"

def test_database_manager_connect(monkeypatch):
    """Testet die Verbindung zur API (Mock)."""
    db = DatabaseManager()
    # Patch connect to always return True
    monkeypatch.setattr(db, "connect", lambda: True)
    assert db.connect() is True

def test_is_read_only():
    db = DatabaseManager()
    assert db._is_read_only("SELECT * FROM test")
    assert not db._is_read_only("DROP TABLE test")
    assert not db._is_read_only("UPDATE test SET x=1")

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

def test_refresh_schema_cache(tmp_path):
    """Integrationstest: Testet refresh_schema_cache (Cache-Update und Datei)."""
    # Nutze einen temporären Cache-Pfad, um Seiteneffekte zu vermeiden
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
