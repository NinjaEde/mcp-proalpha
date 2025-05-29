import os
from dotenv import load_dotenv

load_dotenv()

DB_SERVER_HOST = os.getenv("DB_SERVER_HOST", "http://localhost")
DB_SERVER_PORT = os.getenv("DB_SERVER_PORT", "8080")
DB_API_KEY = os.getenv("DB_API_KEY")
SCHEMA_CACHE_PATH = os.getenv("SCHEMA_CACHE_PATH", "./schema_cache")
