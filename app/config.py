import os
from dotenv import load_dotenv

# .env nur einmal laden, falls noch nicht geschehen
def _load_env():
    if not getattr(_load_env, "_loaded", False):
        load_dotenv()
        _load_env._loaded = True
_load_env()

class Config:
    DB_SERVER_HOST = os.getenv("DB_SERVER_HOST", "http://localhost")
    DB_SERVER_PORT = os.getenv("DB_SERVER_PORT", "8080")
    DB_API_KEY = os.getenv("DB_API_KEY")
    SCHEMA_CACHE_PATH = os.getenv("SCHEMA_CACHE_PATH", "./schema_cache")
    API_SERVER_HOST = os.getenv("API_SERVER_HOST", "http://localhost")
    API_SERVER_PORT = os.getenv("API_SERVER_PORT", "8081")
    MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
    MCP_PORT = os.getenv("MCP_PORT", "8000")

# Instanz für konsistenten Zugriff
config = Config()
