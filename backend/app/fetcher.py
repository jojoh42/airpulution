import time
from datetime import datetime, timedelta, date
from typing import Optional

import requests
from dotenv import load_dotenv
import os
from .mysql_cache import mysql_air_quality_cache

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
    from_date = to_date - timedelta(days=7)
    url = f"https://api.openaq.org/v3/sensors/{sensor_id}/hours/daily"
    sensor_cache = {}

    headers = {
        "X-API-Key": API_KEY  # 👈 API-Key mitsenden!
    }

    params = {
        "datetime_from": from_date.isoformat() + "T23:59:59Z",
        "datetime_to": to_date.isoformat() + "T23:59:59Z",
        "limit": 7
    }
    print(params)

    try:
        response = requests.get(url, headers=headers, params=params, timeout=3)
        if response.status_code == 429:
            print(f"Rate Limit erreicht bei Sensor {sensor_id}. Warte 1 Sekunde...")
            time.sleep(1)
            return []
        response.raise_for_status()
        results = response.json().get("results", [])
        sensor_cache[sensor_id] = results
        time.sleep(0.3)
        return results
    except Exception as e:
        print(f"Fehler bei Messwerten für Sensor {sensor_id}:", e)
    return response.json().get("results", [])

def fetch_air_quality_direct(lat: float, lon: float, city: Optional[str] = None):
    """
    Direct fetcher for air quality data - with MySQL caching for instant responses
    Returns air quality data for given coordinates or city
    """
    # Check MySQL cache first for instant response
    cached_data = mysql_air_quality_cache.get(lat, lon, city)
    if cached_data:
        print(f"[MYSQL-CACHE] Returning cached data for {city or f'({lat}, {lon})'}")
        return cached_data
    
    print(f"[FETCH] No cache hit, fetching fresh data for {city or f'({lat}, {lon})'}")
    
    # Try nearby stations first
    data = fetcher_nearby_air_location(lat, lon)
    
    if not data and city:
        # Fallback to city-based search
        data = fetch_by_city(city)
    
    if not data:
        # Cache the empty result to avoid repeated failed requests
        mysql_air_quality_cache.set(lat, lon, city, [])
        return []
    
    # Get detailed measurements for each station (optimized)
    results = []
    for i, station in enumerate(data):
        sensors = station.get("sensors", [])
        
        sensor_pm25 = next((s for s in sensors if s.get("parameter", {}).get("name") == "pm25"), None)
        sensor_pm10 = next((s for s in sensors if s.get("parameter", {}).get("name") == "pm10"), None)
        
        pm25_data, pm10_data = [], []
        
        # Only fetch if we have sensors and haven't exceeded rate limits
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
        
        # Add station even if only one type of data is available
        if pm25_data or pm10_data:
            results.append({
                "station": station.get("name"),
                "city": station.get("city"),
                "country": station.get("country"),
                "distance": station.get("distance"),
                "coordinates": station.get("coordinates"),
                "pm25": pm25_data,
                "pm10": pm10_data
            })
        
        # Reduced sleep time for faster response
        if i < len(data) - 1:  # Don't sleep after the last station
            time.sleep(0.5)  # Reduced from 1 second to 0.5 seconds
    
    # Cache the results in MySQL for future requests
    mysql_air_quality_cache.set(lat, lon, city, results)
    
    # Also store historical data for analysis
    if results:
        mysql_air_quality_cache.store_historical_data(results)
    
    return results


