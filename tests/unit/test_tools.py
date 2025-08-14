import pytest
from unittest.mock import MagicMock, AsyncMock
from app.server import mcp
import app.server as server_module

# It's better to access the tools via the mcp instance as they are registered there
execute_sql_tool = mcp._tool_manager._tools['execute_sql']
get_table_sample_tool = mcp._tool_manager._tools['get_table_sample']
refresh_schema_tool = mcp._tool_manager._tools['refresh_schema']

@pytest.mark.asyncio
async def test_execute_sql(monkeypatch):
    # Mock the db.execute_query method
    mock_execute = MagicMock(return_value=[{"col1": "value1"}])
    monkeypatch.setattr(server_module.db, "execute_query", mock_execute)

    # Mock the context object
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    # Call the tool function
    query = "SELECT * FROM test_table"
    result = await execute_sql_tool.fn(query, mock_ctx)

    # Assertions
    mock_execute.assert_called_once_with(query)
    mock_ctx.info.assert_awaited_once_with(f"Executing query: {query}")
    assert result == [{"col1": "value1"}]

def test_get_table_sample(monkeypatch):
    # Mock the db.get_table_sample method
    mock_get_sample = MagicMock(return_value=[{"col1": "sample_value"}])
    monkeypatch.setattr(server_module.db, "get_table_sample", mock_get_sample)

    # Call the tool function
    table_name = "test_table"
    limit = 5
    result = get_table_sample_tool.fn(table_name, limit=limit)

    # Assertions
    mock_get_sample.assert_called_once_with(table_name, limit)
    assert result == [{"col1": "sample_value"}]

@pytest.mark.asyncio
async def test_refresh_schema(monkeypatch):
    # Mock the db.refresh_schema_cache method
    mock_refresh = MagicMock()
    monkeypatch.setattr(server_module.db, "refresh_schema_cache", mock_refresh)

    # Mock the context object
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    # Call the tool function
    result = await refresh_schema_tool.fn(mock_ctx)

    # Assertions
    mock_refresh.assert_called_once()
    mock_ctx.info.assert_awaited_once_with("Schema cache refreshed.")
    assert result == "Schema cache refreshed."
