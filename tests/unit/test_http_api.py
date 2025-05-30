import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.http_api import app

client = TestClient(app)

def test_get_schema(monkeypatch):
    # Patch get_database_schema to return a test schema
    test_schema = {"tables": {}, "views": {}, "relationships": []}
    monkeypatch.setattr("app.http_api.db.get_database_schema", lambda: test_schema)
    response = client.get("/api/schema")
    assert response.status_code == 200
    assert response.json() == test_schema

def test_get_tables(monkeypatch):
    test_schema = {"tables": {"foo": {}}, "views": {}, "relationships": []}
    monkeypatch.setattr("app.http_api.db.get_database_schema", lambda: test_schema)
    response = client.get("/api/schema/tables")
    assert response.status_code == 200
    assert response.json() == ["foo"]
