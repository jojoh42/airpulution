from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.api import router
from app.background_updater import background_updater

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Start background data updater when the API starts"""
    background_updater.start_background_updates()
    print("🚀 Background data updater started")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background data updater when the API shuts down"""
    background_updater.stop_background_updates()
    print("🛑 Background data updater stopped")

# API-Router einbinden
app.include_router(router, prefix="/api")

# Pfad zum React-Frontend-Build
frontend_path = Path(__file__).parent.parent / "frontend2" / "dist"

# Statische Dateien für React (JS, CSS, etc.)
app.mount("/assets", StaticFiles(directory=frontend_path / "assets"), name="assets")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Alle anderen Routen liefern index.html (für React-Routing)
@app.get("/{path:path}")
async def serve_frontend(path: str):
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    else:
        return {"error": "index.html not found"}
