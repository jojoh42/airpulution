from http.client import responses

import requests

def ip_to_location(ip: str):
    try:
        if not ip or ip == "127.0.0.1":
            url = "https://ipinfo.io/json"
        else:
            url = f"https://ipinfo.io/{ip}/json"

        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        print("API-Antwort:", data)  # ← Füge das ein
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        loc = data.get("loc", "")  # "lat,lon"
        if not loc:
            return None

        lat, lon = map(float, loc.split(","))
        return {
            "city": data.get("city"),
            "latitude": lat,
            "longitude": lon
        }

    except Exception as e:
        print("Geolocation-Fehler:", e)
        return None