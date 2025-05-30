from .logging_config import setup_logging
from .database import DatabaseManager
from fastmcp import FastMCP, Context
import logging
import os

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

def run():
    mcp_port = int(os.environ.get("MCP_PORT", 8000))    
    mcp.run(transport="streamable-http", host="127.0.0.1", port=mcp_port, path="/mcp")
