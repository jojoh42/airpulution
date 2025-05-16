from fastapi import APIRouter, Request
from .geo import ip_to_location
from .fetcher import (
    fetcher_nearby_air_location,
    fetch_by_city,
    fetch_measurement_by_id, fetch_world_data, fetch_world_station_data
)

router = APIRouter()


@router.get("/air-quality")
def air_quality_from_ip(requests: Request):
    raw_ip = get_client_ip(requests)
    ip = raw_ip if raw_ip != "127.0.0.1" else ""

    location = ip_to_location(ip)
    if not location:
        return {"error": "Standort konnte nicht erkannt werden."}

    lat = location["latitude"]
    lon = location["longitude"]
    city = location["city"]

    data = fetcher_nearby_air_location(lat, lon)
    if not data:
        # Fallback auf Stadt
        data = fetch_by_city(city)
        if not data:
            return {"error": f"keine Luftdaten für {city} gefunden."}

    return {
        "ip": ip,
        "location": location,
        "city": city,
        "air_quality": data
    }


@router.get("/city")
def air_quality_from_city():
    city = "Hamburg"
    data = fetch_by_city(city)
    return {"city": city, "air_quality": data}

@router.get("/world")
def world_data(requests: Request):
    raw_ip = get_client_ip(requests)
    ip = raw_ip if raw_ip != "127.0.0.1" else ""

    location = ip_to_location(ip)
    if not location:
        return {"error": "Standort konnte nicht erkannt werden."}

    lat = location["latitude"]
    lon = location["longitude"]
    city = location["city"]

    data = fetch_world_data()
    results = []


    for station in data:
        sensors = station.get("sensors", [])

        sensor_pm25 = next((s for s in sensors if s.get("parameter", {}).get("name") == "pm25"), None)
        sensor_pm10 = next((s for s in sensors if s.get("parameter", {}).get("name") == "pm10"), None)

        pm25_data, pm10_data = [], []

        if sensor_pm25:
            try:
                pm25_data = fetch_world_station_data(sensor_pm25["id"])
            except Exception as e:
                print(f"PM2.5 Fehler bei {station.get('name')}: {e}")

        if sensor_pm10:
            try:
                pm10_data = fetch_world_station_data(sensor_pm10["id"])
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
        elif sensor_pm25 or sensor_pm10:
            print(f"Station {station.get('name')} hat Sensoren, aber keine Messdaten.")

    return {
        "lat": lat,
        "lon": lon,
        "city": city,
        "location": location,
        "stations": results
    }



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
    return request.client.host
