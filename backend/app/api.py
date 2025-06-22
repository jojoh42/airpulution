from fastapi import APIRouter, Request, HTTPException, Query
from typing import Optional, List, Dict, Any
import time
from datetime import datetime
import urllib.parse

from .geo import ip_to_location
from .fetcher import (
    fetcher_nearby_air_location,
    fetch_by_city,
    fetch_measurement_by_id,
    fetch_air_quality_direct
)
from .mysql_cache import mysql_air_quality_cache
from .background_updater import background_updater

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
            return {"error": "Keine Daten für diesen Standort gefunden."}

    return {"data": data, "location": location}

@router.get("/city")
def air_quality_from_city():
    data = fetch_by_city("Berlin")
    return {"data": data}

@router.get("/direct-air-quality")
def direct_air_quality(requests: Request, lat: Optional[float] = None, lon: Optional[float] = None, city: Optional[str] = None):
    """Get air quality data directly from API with caching"""
    start_time = time.time()
    
    try:
        # If coordinates not provided, get from IP
        if lat is None or lon is None:
            location = ip_to_location(get_client_ip(requests))
            if not location:
                return {"error": "Standort konnte nicht erkannt werden."}
            lat = location["latitude"]
            lon = location["longitude"]
            city = city or location["city"]
        
        # Ensure coordinates are valid
        if lat is None or lon is None:
            return {"error": "Ungültige Koordinaten"}
        
        # First, try to get from cache
        cached_data = mysql_air_quality_cache.get(float(lat), float(lon), city)
        
        if cached_data:
            # Cache hit - return immediately
            response_time = time.time() - start_time
            return {
                "data": cached_data,
                "source": "cache",
                "response_time": round(response_time, 3)
            }
        
        # Cache miss - fetch fresh data
        print(f"Cache miss for {city or f'({lat}, {lon})'}, fetching fresh data...")
        data = fetch_air_quality_direct(float(lat), float(lon), city)
        
        if data:
            # Store in cache for future requests
            mysql_air_quality_cache.set(float(lat), float(lon), city, data)
            
            response_time = time.time() - start_time
            return {
                "data": data,
                "source": "api",
                "response_time": round(response_time, 3),
                "cached": True
            }
        else:
            raise HTTPException(status_code=404, detail="No air quality data found for this location")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cache management endpoints
@router.get("/cache/stats")
def get_cache_stats():
    """Get cache statistics"""
    try:
        stats = mysql_air_quality_cache.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache/clear")
def clear_cache():
    """Clear all cached data"""
    try:
        mysql_air_quality_cache.clear_cache()
        return {"message": "Cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/top-cities")
def get_top_cities(limit: int = Query(10, description="Number of top cities to return")):
    """Get top cities by cache hits"""
    try:
        cities = mysql_air_quality_cache.get_top_cities(limit)
        return {"cities": cities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/historical/{station_name}")
def get_historical_data(
    station_name: str,
    days: int = Query(7, description="Number of days of historical data")
):
    """Get historical data for a specific station"""
    try:
        data = mysql_air_quality_cache.get_historical_data(station_name, days)
        return {"station": station_name, "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background updater endpoints
@router.get("/background/status")
def get_background_status():
    """Get background updater status"""
    try:
        status = background_updater.get_update_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/background/start")
def start_background_updates():
    """Start background updates"""
    try:
        background_updater.start_background_updates()
        return {"message": "Background updates started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/background/stop")
def stop_background_updates():
    """Stop background updates"""
    try:
        background_updater.stop_background_updates()
        return {"message": "Background updates stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/background/force-update")
def force_update_city(
    city_name: str = Query(..., description="City name"),
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """Force update data for a specific city"""
    try:
        success = background_updater.force_update_city(city_name, lat, lon)
        if success:
            return {"message": f"Successfully updated {city_name}"}
        else:
            raise HTTPException(status_code=404, detail=f"Failed to update {city_name}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/station/{station_name}")
def get_station_data(station_name: str):
    """Get air quality data for a specific station by name"""
    start_time = time.time()
    
    try:
        # Decode the station name
        decoded_station_name = urllib.parse.unquote(station_name)
        
        # Try to find the station in cache first
        cached_data = mysql_air_quality_cache.get_station_by_name(decoded_station_name)
        
        if cached_data:
            response_time = time.time() - start_time
            return {
                "data": cached_data,
                "source": "cache",
                "response_time": round(response_time, 3),
                "cached": True
            }
        
        # If not in cache, try to find it in recent data
        # For now, we'll use a default location and search for the station
        # This could be improved by storing station coordinates in the cache
        
        # Try with Hamburg coordinates as default
        lat, lon = 53.5511, 9.9937
        data = fetch_air_quality_direct(lat, lon, "Hamburg")
        
        if data:
            # Find the specific station
            station_data = [station for station in data if station.get("station") == decoded_station_name]
            
            if station_data:
                response_time = time.time() - start_time
                return {
                    "data": station_data,
                    "source": "api",
                    "response_time": round(response_time, 3),
                    "cached": False
                }
        
        raise HTTPException(status_code=404, detail=f"Station '{decoded_station_name}' not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_client_ip(request: Request):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.client.host if request.client else "127.0.0.1"
    return ip