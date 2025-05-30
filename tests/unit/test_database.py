from app.database import DatabaseManager
from app.config import config

# Set test environment variables (override if needed)
import os
os.environ["DB_SERVER_HOST"] = config.DB_SERVER_HOST
os.environ["DB_SERVER_PORT"] = config.DB_SERVER_PORT
os.environ["DB_API_KEY"] = config.DB_API_KEY or ""
os.environ["SCHEMA_CACHE_PATH"] = config.SCHEMA_CACHE_PATH

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
