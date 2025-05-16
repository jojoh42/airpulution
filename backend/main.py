from fastapi import FastAPI
from pyexpat.errors import messages

from app import api

app = FastAPI()

app.include_router(api.router, prefix="/api")

@app.get("/")
def root():
    return{"message": "Luftqualitäts-API Läuft"}