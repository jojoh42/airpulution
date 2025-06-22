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
frontend_path = Path(__file__).parent.parent / "frontend2" / "src"

# Statische Dateien für React (JS, CSS)
app.mount("/assets", StaticFiles(directory=frontend_path / "assets"), name="assets")

# Alle anderen Routen liefern index.html (für React-Routing)
@app.get("/{path}")
async def serve_frontend():
    return FileResponse("index.html")
