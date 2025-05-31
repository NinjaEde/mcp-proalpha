from .logging_config import setup_logging
from .database import DatabaseManager
from fastmcp import FastMCP, Context
import logging
from .config import config


setup_logging()
logger = logging.getLogger("mcp-proalpha")

db = DatabaseManager()
mcp: FastMCP = FastMCP("ProAlpha MCP Server")

@mcp.resource("resource://database_schema")
def resource_database_schema() -> dict:
    """Vollständiges Schema der ProAlpha-Datenbank."""
    return db.get_database_schema()

@mcp.resource("resource://relationships")
def resource_relationships() -> list:
    """Beziehungen zwischen den Tabellen der Datenbank."""
    return db.get_database_schema().get("relationships", [])

@mcp.resource("table://{table_name}")
def resource_table_schema(table_name: str) -> dict:
    """Schema einer bestimmten Tabelle."""
    return db.get_database_schema().get("tables", {}).get(table_name, {})

@mcp.resource("view://{view_name}")
def resource_view_schema(view_name: str) -> dict:
    """Schema einer bestimmten View."""
    return db.get_database_schema().get("views", {}).get(view_name, {})

@mcp.tool()
async def execute_sql(query: str, ctx: Context) -> list:
    """Führt eine Read-Only-SQL-Abfrage aus."""
    await ctx.info(f"Executing query: {query}")
    return db.execute_query(query)

@mcp.tool()
def get_table_sample(table_name: str, limit: int = 10) -> list:
    """Gibt eine Stichprobe der Daten einer Tabelle zurück."""
    return db.get_table_sample(table_name, limit)

@mcp.tool()
async def refresh_schema(ctx: Context) -> str:
    """Aktualisiert den Schema-Cache."""
    db.refresh_schema_cache()
    await ctx.info("Schema cache refreshed.")
    return "Schema cache refreshed."

@mcp.tool()
def list_tools() -> list:
    """Gibt eine Liste aller verfügbaren Tools mit Beschreibung und Parametern zurück."""
    result = []
    # FastMCP v2: Tools werden in mcp._tool_manager._tools als Dict gespeichert
    for tool in getattr(mcp._tool_manager, "_tools", {}).values():
        entry = {
            "name": getattr(tool, "name", None) or getattr(tool, "__name__", None),
            "description": getattr(tool, "description", ""),
            "parameters": getattr(tool, "parameters", None),
        }
        result.append(entry)
    return result

def run():
    transport = (getattr(config, "MCP_TRANSPORT", None) or "streamable-http").lower()
    mcp_host = config.MCP_HOST
    mcp_port = int(config.MCP_PORT)
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "streamable-http":
        mcp.run(transport="streamable-http", host=mcp_host, port=mcp_port, path="/mcp")
    elif transport == "sse":
        mcp.run(transport="sse", host=mcp_host, port=mcp_port)
    else:
        raise ValueError(f"Unsupported MCP_TRANSPORT: {transport}")
