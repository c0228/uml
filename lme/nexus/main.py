import os
import sys
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Bundled FastAPI App")

# --------------------------------------------------
# 🔐 Resolve path when running as .exe (PyInstaller)
# --------------------------------------------------
def get_frontend_dist():
    if getattr(sys, 'frozen', False):
        # Running inside PyInstaller bundle
        base_path = sys._MEIPASS
    else:
        # Running normally (dev mode)
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, "gway", "dist")

DIST_DIR = get_frontend_dist()
print("DIST_DIR =", DIST_DIR)
if os.path.exists(DIST_DIR):
    print("DIST CONTENT:", os.listdir(DIST_DIR))

# --------------------------------------------------
# 1️⃣ HELLO WORLD API
# --------------------------------------------------
@app.get("/api/hello")
async def hello():
    return {"message": "Hello from secured FastAPI"}

# --------------------------------------------------
# 2️⃣ FRONTEND (React dist) — SAME PORT
# --------------------------------------------------
ASSETS_DIR = os.path.join(DIST_DIR, "assets")

if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
else:
    print("⚠️ Assets directory not found:", ASSETS_DIR)

@app.get("/{path:path}")
async def serve_frontend(path: str):
    file_path = os.path.join(DIST_DIR, path)
    if path and os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(DIST_DIR, "index.html"))

# --------------------------------------------------
# 3️⃣ WEBSOCKET SERVER
# --------------------------------------------------
@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    while True:
        msg = await ws.receive_text()
        await ws.send_text(f"Echo: {msg}")