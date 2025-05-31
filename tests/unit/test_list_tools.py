def test_list_tools():
    import app.server
    mcp = app.server.mcp

    # FastMCP v2 speichert Tools als Dict unter mcp._tool_manager._tools
    tools_dict = getattr(mcp._tool_manager, "_tools", {})
    assert "list_tools" in tools_dict
    # list_tools aufrufen (Tool-Objekt, nicht direkt callable)
    result = tools_dict["list_tools"].fn()
    assert isinstance(result, list)
    found = any(tool.get("name") == "list_tools" for tool in result)
    assert found
    for tool in result:
        assert "name" in tool
        assert "description" in tool
        assert "parameters" in tool  # Sicherstellen, dass das Feld vorhanden ist
