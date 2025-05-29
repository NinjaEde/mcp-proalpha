from .logging_config import setup_logging
from .database import DatabaseManager
from fastmcp import FastMCP, Context
import logging

setup_logging()
logger = logging.getLogger("mcp-proalpha")

db = DatabaseManager()
mcp = FastMCP("ProAlpha MCP Server")

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
def execute_sql(query: str, ctx: Context) -> list:
    """Führt eine Read-Only-SQL-Abfrage aus."""
    ctx.info(f"Executing query: {query}")
    return db.execute_query(query)

@mcp.tool()
def get_table_sample(table_name: str, limit: int = 10) -> list:
    """Gibt eine Stichprobe der Daten einer Tabelle zurück."""
    return db.get_table_sample(table_name, limit)

@mcp.tool()
def refresh_schema(ctx: Context) -> str:
    """Aktualisiert den Schema-Cache."""
    db.refresh_schema_cache()
    ctx.info("Schema cache refreshed.")
    return "Schema cache refreshed."

def run():
    mcp.run()
