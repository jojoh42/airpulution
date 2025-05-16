from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
import os

load_dotenv()  # Muss vor os.getenv() stehen!

API_KEY = os.getenv("API_KEY")
print("API_KEY:", API_KEY)  # 👈 Teste es einmal

def fetcher_nearby_air_location(lat, lon):
    url = "https://api.openaq.org/v3/locations"
    headers = {"X-API-Key": API_KEY}
    cords = f"{float(lat):.4f},{float(lon):.4f}"
    params = {
        "coordinates": cords,
        "radius": 20000,
        "limit": 5,
        "order by": "distance"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        print("Luftdaten-Fehler:", e)
        return []

def fetch_by_city(city: str = "Hamburg"):
    url = "https://api.openaq.org/v3/locations"
    headers = {"X-API-Key": API_KEY}
    params = {
        "city": city,
        "limit": 5
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        return response.json().get("results", [])
    except Exception as e:
        print("Fehler beim Abrufen nach Stadt:", e)
        return []

def fetch_measurement_by_id(sensor_id: int):
    to_date = datetime.utcnow().date()
    from_date = to_date - timedelta(days=14)
    url = f"https://api.openaq.org/v3/sensors/{sensor_id}/hours/daily"

    headers = {
        "X-API-Key": API_KEY  # 👈 API-Key mitsenden!
    }

    params = {
        "datetime_from": from_date.isoformat() + "T23:59:59Z",
        "datetime_to": to_date.isoformat() + "T23:59:59Z",
        "limit": 14
    }
    print(params)

    response = requests.get(url, headers=headers, params=params, timeout=5)
    response.raise_for_status()
    return response.json().get("results", [])