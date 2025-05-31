from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from .database import DatabaseManager
import logging
import asyncio
import json

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                # Beispiel: MCP-Tool-Request
                if msg.get("id") == "execute_sql":
                    query = msg["parameters"]["query"]
                    result = db.execute_query(query)
                    await websocket.send_text(json.dumps({"result": result}))
                elif msg.get("id") == "get_table_sample":
                    table = msg["parameters"]["table_name"]
                    limit = msg["parameters"].get("limit", 10)
                    result = db.get_table_sample(table, limit)
                    await websocket.send_text(json.dumps({"result": result}))
                else:
                    await websocket.send_text(json.dumps({"error": "Unknown tool id"}))
            except Exception as e:
                await websocket.send_text(json.dumps({"error": str(e)}))
    except WebSocketDisconnect:
        pass

@app.get("/sse")
async def sse_endpoint():
    async def event_generator():
        # Beispiel: Sende ein MCP-Tool-Request-Resultat als Stream
        yield f"data: {json.dumps({'result': 'SSE-Stream aktiv'})}\n\n"
        await asyncio.sleep(1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/sse")
async def sse_endpoint_post():
    async def event_generator():
        yield f"data: {json.dumps({'result': 'SSE-Stream aktiv'})}\n\n"
        await asyncio.sleep(1)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/tools")
def get_tools():
    """
    Gibt eine Liste aller verfügbaren Tools mit Name, Beschreibung und Parametern zurück (analog zu list_tools im MCP-Server).
    """
    from .server import mcp
    result = []
    for tool in getattr(mcp._tool_manager, "_tools", {}).values():
        entry = {
            "name": getattr(tool, "name", None) or getattr(tool, "__name__", None),
            "description": getattr(tool, "description", ""),
            "parameters": getattr(tool, "parameters_schema", None),
        }
        result.append(entry)
    return result
