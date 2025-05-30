from .server import run
import threading
import uvicorn
import os

def start_http_api():
    port = int(os.environ.get("API_SERVER_PORT", 8081))
    uvicorn.run("app.http_api:app", host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    # Starte HTTP-API in separatem Thread auf API_SERVER_PORT
    t = threading.Thread(target=start_http_api, daemon=True)
    t.start()
    # Starte MCP-Server (blockiert Hauptthread)
    run()
