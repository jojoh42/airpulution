import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from concurrent.futures import ThreadPoolExecutor, as_completed

from fetcher import fetch_world_data, fetch_world_station_data

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "db.env")
load_dotenv(dotenv_path=dotenv_path)

# DB Setup
DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)

# Gestern
yesterday = datetime.utcnow().date() - timedelta(days=1)

def fetch_sensor_data(sensor_id):
    try:
        return sensor_id, fetch_world_station_data(sensor_id, date_param=yesterday)
    except Exception as e:
        print(f"[ERROR] Fehler bei Sensor {sensor_id}: {e}")
        return sensor_id, []

def update_database():
    print("[START] Lade Weltstationsdaten...")
    stations = fetch_world_data()
    print(f"[INFO] {len(stations)} Stationen gefunden.")

    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_map = {}
        for station in stations:
            sensors = station.get("sensors", [])
            for sensor in sensors:
                sid = sensor.get("id")
                if sid:
                    future = executor.submit(fetch_sensor_data, sid)
                    future_map[future] = (station, sensor)

        sensor_data = {}
        for future in as_completed(future_map):
            sensor_id, data = future.result()
            sensor_data[sensor_id] = data

    with engine.begin() as conn:
        for station in stations:
            name = station.get("name")
            dist = station.get("distance") or 0.0
            coords = str(station.get("coordinates"))
            sensors = station.get("sensors", [])

            pm25_data = []
            pm10_data = []

            for s in sensors:
                sid = s.get("id")
                if s["parameter"]["name"] == "pm25":
                    pm25_data = sensor_data.get(sid, [])
                elif s["parameter"]["name"] == "pm10":
                    pm10_data = sensor_data.get(sid, [])

            if pm25_data or pm10_data:
                query = text("""
                    INSERT INTO data_table (station_name, distance, coordinates, pm25_data, pm10_data, created_at)
                    VALUES (:station_name, :distance, :coordinates, :pm25_data, :pm10_data, :created_at)
                """)
                conn.execute(query, {
                    "station_name": name,
                    "distance": dist,
                    "coordinates": coords,
                    "pm25_data": str(pm25_data),
                    "pm10_data": str(pm10_data),
                    "created_at": datetime.utcnow()
                })
    print("✅ Daten gespeichert.")

if __name__ == "__main__":
    update_database()
