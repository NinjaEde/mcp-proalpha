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

def test_get_table_schema_found(monkeypatch):
    test_schema = {"tables": {"foo": {"columns": ["col1"]}}, "views": {}, "relationships": []}
    monkeypatch.setattr("app.http_api.db.get_database_schema", lambda: test_schema)
    response = client.get("/api/schema/tables/foo")
    assert response.status_code == 200
    assert response.json() == {"columns": ["col1"]}

def test_get_table_schema_not_found(monkeypatch):
    test_schema = {"tables": {}, "views": {}, "relationships": []}
    monkeypatch.setattr("app.http_api.db.get_database_schema", lambda: test_schema)
    response = client.get("/api/schema/tables/foo")
    assert response.status_code == 404

def test_get_views(monkeypatch):
    test_schema = {"tables": {}, "views": {"bar": {}}, "relationships": []}
    monkeypatch.setattr("app.http_api.db.get_database_schema", lambda: test_schema)
    response = client.get("/api/schema/views")
    assert response.status_code == 200
    assert response.json() == ["bar"]

def test_get_view_schema_found(monkeypatch):
    test_schema = {"tables": {}, "views": {"bar": {"columns": ["col1"]}}, "relationships": []}
    monkeypatch.setattr("app.http_api.db.get_database_schema", lambda: test_schema)
    response = client.get("/api/schema/views/bar")
    assert response.status_code == 200
    assert response.json() == {"columns": ["col1"]}

def test_get_view_schema_not_found(monkeypatch):
    test_schema = {"tables": {}, "views": {}, "relationships": []}
    monkeypatch.setattr("app.http_api.db.get_database_schema", lambda: test_schema)
    response = client.get("/api/schema/views/bar")
    assert response.status_code == 404

def test_get_relationships(monkeypatch):
    test_relationships = [{"from": "table1", "to": "table2"}]
    test_schema = {"tables": {}, "views": {}, "relationships": test_relationships}
    monkeypatch.setattr("app.http_api.db.get_database_schema", lambda: test_schema)
    response = client.get("/api/schema/relationships")
    assert response.status_code == 200
    assert response.json() == test_relationships

def test_post_query_success(monkeypatch):
    monkeypatch.setattr("app.http_api.db.execute_query", lambda query: {"result": "ok"})
    response = client.post("/api/query", json={"query": "SELECT 1"})
    assert response.status_code == 200
    assert response.json() == {"result": "ok"}

def test_post_query_missing_query(monkeypatch):
    response = client.post("/api/query", json={})
    assert response.status_code == 400

def test_post_query_db_error(monkeypatch):
    def mock_execute_query(query):
        raise ValueError("DB Error")
    monkeypatch.setattr("app.http_api.db.execute_query", mock_execute_query)
    response = client.post("/api/query", json={"query": "SELECT 1"})
    assert response.status_code == 400
    assert "DB Error" in response.json()["detail"]

def test_refresh_schema(monkeypatch):
    def mock_refresh():
        # print("mock_refresh called")
        pass
    monkeypatch.setattr("app.http_api.db.refresh_schema_cache", mock_refresh)
    response = client.post("/api/schema/refresh")
    assert response.status_code == 200
    assert response.json() == {"status": "Schema cache refreshed"}

def test_get_tools(monkeypatch):
    test_tools = [{"name": "tool1", "description": "desc1", "parameters": {}}]
    monkeypatch.setattr("app.http_api.list_all_tools", lambda mcp: test_tools)
    response = client.get("/api/tools")
    assert response.status_code == 200
    assert response.json() == test_tools

def test_get_tool_found(monkeypatch):
    test_tools = [{"name": "tool1", "description": "desc1", "parameters": {}}]
    monkeypatch.setattr("app.http_api.list_all_tools", lambda mcp: test_tools)
    response = client.get("/api/tools/tool1")
    assert response.status_code == 200
    assert response.json() == test_tools[0]

def test_get_tool_not_found(monkeypatch):
    test_tools = [{"name": "tool1", "description": "desc1", "parameters": {}}]
    monkeypatch.setattr("app.http_api.list_all_tools", lambda mcp: test_tools)
    response = client.get("/api/tools/tool2")
    assert response.status_code == 404

def test_get_prompts(monkeypatch):
    test_prompts = {"prompt1": {"title": "title1", "description": "desc1"}}
    monkeypatch.setattr("app.http_api.load_prompts", lambda: test_prompts)
    response = client.get("/api/prompts")
    assert response.status_code == 200
    assert response.json() == [{"name": "prompt1", "title": "title1", "description": "desc1"}]

def test_get_prompt_found(monkeypatch):
    test_template = "This is a template"
    monkeypatch.setattr("app.http_api.get_prompt_template", lambda name: test_template)
    response = client.get("/api/prompts/prompt1")
    assert response.status_code == 200
    assert response.json() == {"name": "prompt1", "template": test_template}

def test_get_prompt_not_found(monkeypatch):
    def mock_get_template(name):
        raise KeyError
    monkeypatch.setattr("app.http_api.get_prompt_template", mock_get_template)
    response = client.get("/api/prompts/prompt2")
    assert response.status_code == 404
