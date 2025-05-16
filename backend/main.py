from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app import api

app = FastAPI()

# API-Router einbinden
app.include_router(api.router, prefix="/api")

# Pfad zum React-Frontend-Build
frontend_path = Path(__file__).parent.parent / "frontend2" / "src"

# Statische Dateien für React (JS, CSS)
app.mount("/assets", StaticFiles(directory=frontend_path / "assets"), name="assets")

# Alle anderen Routen liefern index.html (für React-Routing)
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    return FileResponse(frontend_path / "index.html")
