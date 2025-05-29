from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from .database import DatabaseManager
import logging

logger = logging.getLogger("mcp-proalpha-http")
app = FastAPI(title="ProAlpha MCP REST API")
db = DatabaseManager()

@app.get("/api/schema")
def get_schema():
    return db.get_database_schema()

@app.get("/api/schema/tables")
def get_tables():
    schema = db.get_database_schema()
    return list(schema.get("tables", {}).keys())

@app.get("/api/schema/tables/{table_name}")
def get_table_schema(table_name: str):
    schema = db.get_database_schema()
    table = schema.get("tables", {}).get(table_name)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table

@app.get("/api/schema/views")
def get_views():
    schema = db.get_database_schema()
    return list(schema.get("views", {}).keys())

@app.get("/api/schema/views/{view_name}")
def get_view_schema(view_name: str):
    schema = db.get_database_schema()
    view = schema.get("views", {}).get(view_name)
    if not view:
        raise HTTPException(status_code=404, detail="View not found")
    return view

@app.get("/api/schema/relationships")
def get_relationships():
    schema = db.get_database_schema()
    return schema.get("relationships", [])

@app.post("/api/query")
async def post_query(request: Request):
    data = await request.json()
    if not data or "query" not in data:
        raise HTTPException(status_code=400, detail="Missing 'query' in request body")
    try:
        results = db.execute_query(data["query"])
        return results
    except Exception as e:
        logger.error(f"Fehler bei SQL-Abfrage: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/schema/refresh")
def refresh_schema():
    db.refresh_schema_cache()
    return {"status": "Schema cache refreshed"}
