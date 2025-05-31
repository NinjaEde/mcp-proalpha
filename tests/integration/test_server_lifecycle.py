import subprocess
import time
import requests
import os
from app.config import config

API_HOST = config.API_SERVER_HOST
API_PORT = config.API_SERVER_PORT
API_HOST_CLEAN = API_HOST.replace("http://", "").replace("https://", "")
SERVER_START_CMD = [
    "uvicorn", "app.http_api:app",
    "--host", API_HOST_CLEAN,
    "--port", str(API_PORT)
]
SERVER_URL = f"{API_HOST}:{API_PORT}/api/schema"


def wait_for_server(url, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def test_server_start_and_schema():
    """Startet die HTTP-API im Hintergrund und prüft, ob die API erreichbar ist."""
    env = os.environ.copy()
    env["DB_SERVER_HOST"] = config.DB_SERVER_HOST
    env["DB_SERVER_PORT"] = config.DB_SERVER_PORT_STR
    env["DB_API_KEY"] = config.DB_API_KEY or ""
    env["SCHEMA_CACHE_PATH"] = config.SCHEMA_CACHE_PATH
    env["API_SERVER_HOST"] = config.API_SERVER_HOST
    env["API_SERVER_PORT"] = str(config.API_SERVER_PORT)
    proc = subprocess.Popen(SERVER_START_CMD, env=env)
    try:
        assert wait_for_server(SERVER_URL, timeout=30), "Server nicht erreichbar!"
        # Optional: weitere API-Tests
        r = requests.get(SERVER_URL)
        assert r.status_code == 200
        assert "tables" in r.json() or isinstance(r.json(), list)
    finally:
        proc.terminate()
        proc.wait(timeout=10)
