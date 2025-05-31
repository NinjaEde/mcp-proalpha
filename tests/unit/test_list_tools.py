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
        assert "parameters" in tool


def test_list_tools_content():
    import app.server
    mcp = app.server.mcp
    tools_dict = getattr(mcp._tool_manager, "_tools", {})
    result = tools_dict["list_tools"].fn()
    for tool in result:
        # Name sollte ein nicht-leerer String sein
        assert isinstance(tool["name"], str) and tool["name"].strip() != ""
        # Description sollte ein String sein (darf leer sein, aber sollte existieren)
        assert isinstance(tool["description"], str)
        # Parameters sollte ein dict oder None sein
        assert tool["parameters"] is None or isinstance(tool["parameters"], dict)
        # Wenn parameters vorhanden, sollte mindestens 'type' oder 'properties' enthalten sein
        if isinstance(tool["parameters"], dict):
            assert "type" in tool["parameters"] or "properties" in tool["parameters"]
