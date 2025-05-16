import time
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
    sensor_cache = {}

    headers = {
        "X-API-Key": API_KEY  # 👈 API-Key mitsenden!
    }

    params = {
        "datetime_from": from_date.isoformat() + "T23:59:59Z",
        "datetime_to": to_date.isoformat() + "T23:59:59Z",
        "limit": 14
    }
    print(params)

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.status_code == 429:
            print(f"Rate Limit erreicht bei Sensor {sensor_id}. Warte 2 Sekunden...")
            time.sleep(2)
            return []
        response.raise_for_status()
        results = response.json().get("results", [])
        sensor_cache[sensor_id] = results
        time.sleep(1)  # Wartezeit zur Limitvermeidung
        return results
    except Exception as e:
        print(f"Fehler bei Messwerten für Sensor {sensor_id}:", e)
    return response.json().get("results", [])

def fetch_world_data(limit=100, max_pages=3):
    url = "https://api.openaq.org/v3/locations"
    headers = {"X-API-Key": API_KEY}
    all_results = []

    for page in range(1, max_pages + 1):
        params = {
            "limit": limit,
            "page": page,
        }
        try:
            res = requests.get(url, headers=headers, params=params, timeout=10)
            res.raise_for_status()
            results = res.json().get("results", [])
            if not results:
                break
            all_results.extend(results)
        except Exception as e:
            print(f"Fehler auf Seite {page}: {e}")
            break

    return all_results

def fetch_world_station_data(sensor_id: int):
    to_date = datetime.utcnow().date()
    url = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements"
    headers = {"X-API-Key": API_KEY}
    sensor_cache = {}

    params = {"sensor_id": sensor_id,"limit": 2, "order_by": "datetime", "datetime_to": to_date.isoformat()}

    print(params)

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)

        if response.status_code == 429:
            print(f"Rate Limit erreicht bei Sensor {sensor_id}. Warte 2 Sekunden...")
            time.sleep(2)
            return []
        response.raise_for_status()
        results = response.json().get("results", [])
        sensor_cache[sensor_id] = results
        time.sleep(1)
        return results
    except Exception as e:
        print(f"Fehler bei Messwerten für Sensor {sensor_id}:", e)
    return response.json().get("results", [])

