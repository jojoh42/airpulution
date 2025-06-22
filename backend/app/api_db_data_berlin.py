from fastapi import APIRouter, Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .geo import ip_to_location
import pymysql
from .fetcher import (
    fetcher_nearby_air_location,
    fetch_by_city,
    fetch_measurement_by_id, fetch_world_data, fetch_world_station_data
)
import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus der db.env-Datei
load_dotenv("db.env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", 3306)

# Erstelle eine Verbindung zur Datenbank
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()

from sqlalchemy import text

def save_station_data(station_data):
    db = SessionLocal()
    try:
        for station in station_data:
            # Beispiel-Datenstruktur speichern, du musst diese anpassen je nach deiner Tabellenstruktur
            query = text("""
                INSERT INTO data_table (station_name, distance, coordinates, pm25_data, pm10_data)
                VALUES (:station_name, :distance, :coordinates, :pm25_data, :pm10_data)
            """)
            db.execute(query, {
                "station_name": station['station'],
                "distance": station['distance'],
                "coordinates": str(station['coordinates']),
                "pm25_data": str(station['pm25']),
                "pm10_data": str(station['pm10'])
            })
        db.commit()
    finally:
        db.close()


@router.get("/daily-values")
def all_station_data(requests: Request):
    raw_ip = get_client_ip(requests)
    ip = raw_ip if raw_ip != "127.0.0.1" else ""

    location = ip_to_location(ip)
    if not location:
        return {"error": "Standort konnte nicht erkannt werden."}

    lat = location["latitude"]
    lon = location["longitude"]
    city = location["city"]

    stations = fetcher_nearby_air_location(lat, lon)
    if not stations:
        return {"error": f"Keine Stationen bei {city} gefunden."}

    results = []
    for station in stations:
        sensors = station.get("sensors", [])

        sensor_pm25 = next((s for s in sensors if s.get("parameter", {}).get("name") == "pm25"), None)
        sensor_pm10 = next((s for s in sensors if s.get("parameter", {}).get("name") == "pm10"), None)

        pm25_data, pm10_data = [], []

        if sensor_pm25:
            try:
                pm25_data = fetch_measurement_by_id(sensor_pm25["id"])
            except Exception as e:
                print(f"PM2.5 Fehler bei {station.get('name')}: {e}")

        if sensor_pm10:
            try:
                pm10_data = fetch_measurement_by_id(sensor_pm10["id"])
            except Exception as e:
                print(f"PM10 Fehler bei {station.get('name')}: {e}")

        if pm25_data or pm10_data:
            results.append({
                "station": station.get("name"),
                "distance": station.get("distance"),
                "coordinates": station.get("coordinates"),
                "pm25": pm25_data,
                "pm10": pm10_data
            })

    # Speichern der abgerufenen Daten in der Datenbank
    save_station_data(results)

    return {
        "lat": lat,
        "lon": lon,
        "ip": ip,
        "location": location,
        "city": city,
        "stations": results
    }

def get_client_ip(request: Request):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.client.host if request.client else "127.0.0.1"
