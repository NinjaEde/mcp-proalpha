from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

# .env nur einmal laden, falls noch nicht geschehen
def _load_env():
    if not getattr(_load_env, "_loaded", False):
        load_dotenv()
        _load_env._loaded = True
_load_env()

class Config(BaseSettings):
    DB_SERVER_HOST: str = "http://localhost"
    DB_SERVER_PORT: int = 8080
    DB_API_KEY: str = ""
    SCHEMA_CACHE_PATH: str = "./schema_cache"
    API_SERVER_HOST: str = "http://localhost"
    API_SERVER_PORT: int = 8081
    MCP_TRANSPORT: str = "streamable-http"  # stdio, streamable-http, sse
    MCP_HOST: str = "0.0.0.0"
    MCP_PORT: int = 8000

    @property
    def DB_SERVER_PORT_STR(self) -> str:
        return str(self.DB_SERVER_PORT)

    @property
    def API_SERVER_PORT_STR(self) -> str:
        return str(self.API_SERVER_PORT)

    @property
    def MCP_PORT_STR(self) -> str:
        return str(self.MCP_PORT)

    model_config = {
        "env_file": ".env"
    }

# Instanz für konsistenten Zugriff
config = Config()
