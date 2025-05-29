from .server import run
import threading
import uvicorn

def start_http_api():
    uvicorn.run("app.http_api:app", host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    # Starte HTTP-API in separatem Thread auf Port 8000
    t = threading.Thread(target=start_http_api, daemon=True)
    t.start()
    # Starte MCP-Server (blockiert Hauptthread)
    run()
