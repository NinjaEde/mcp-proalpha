# Placeholder for future tool logic or custom MCP tools
# You can implement additional MCP tools here if needed

def list_tools(mcp_instance) -> list:
    """Gibt eine Liste aller verfügbaren Tools mit Beschreibung und Parametern zurück."""
    result = []
    for tool in getattr(mcp_instance._tool_manager, "_tools", {}).values():
        entry = {
            "name": getattr(tool, "name", None) or getattr(tool, "__name__", None),
            "description": getattr(tool, "description", ""),
            "parameters": getattr(tool, "parameters", None),
        }
        result.append(entry)
    return result
