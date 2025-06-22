#!/usr/bin/env python3
"""
Preload MySQL cache with common cities for instant access
"""

import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.fetcher import fetch_air_quality_direct
from app.mysql_cache import mysql_air_quality_cache

# Common German cities with their approximate coordinates
COMMON_CITIES = [
    {"name": "Berlin", "lat": 52.5200, "lon": 13.4050},
    {"name": "Hamburg", "lat": 53.5511, "lon": 9.9937},
    {"name": "München", "lat": 48.1351, "lon": 11.5820},
    {"name": "Köln", "lat": 50.9375, "lon": 6.9603},
    {"name": "Frankfurt", "lat": 50.1109, "lon": 8.6821},
    {"name": "Stuttgart", "lat": 48.7758, "lon": 9.1829},
    {"name": "Düsseldorf", "lat": 51.2277, "lon": 6.7735},
    {"name": "Dortmund", "lat": 51.5136, "lon": 7.4653},
    {"name": "Essen", "lat": 51.4556, "lon": 7.0116},
    {"name": "Leipzig", "lat": 51.3397, "lon": 12.3731},
]

def preload_mysql_cache():
    """Preload MySQL cache with common cities"""
    print("🚀 Preloading MySQL cache with common cities...")
    
    for city in COMMON_CITIES:
        print(f"📡 Loading data for {city['name']}...")
        try:
            # Fetch data for the city
            data = fetch_air_quality_direct(city['lat'], city['lon'], city['name'])
            
            if data:
                print(f"✅ Cached {len(data)} stations for {city['name']}")
            else:
                print(f"⚠️  No data found for {city['name']}")
                
        except Exception as e:
            print(f"❌ Error loading {city['name']}: {e}")
    
    # Show cache stats
    stats = mysql_air_quality_cache.get_stats()
    print(f"\n📊 MySQL Cache Stats:")
    print(f"   Cache items: {stats.get('cache_items', 0)}")
    print(f"   Total stations: {stats.get('total_stations', 0)}")
    print(f"   Total measurements: {stats.get('total_measurements', 0)}")
    print(f"   Database size: {stats.get('db_size_mb', 0)} MB")
    
    # Show top cities
    top_cities = mysql_air_quality_cache.get_top_cities(5)
    if top_cities:
        print(f"\n🏆 Top Cities by Station Count:")
        for city in top_cities:
            print(f"   {city['city']}: {city['station_count']} stations")
    
    print("\n🎉 MySQL cache preloading completed!")

if __name__ == "__main__":
    preload_mysql_cache() 