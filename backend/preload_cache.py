#!/usr/bin/env python3
"""
Preload cache with common cities for instant access
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.fetcher import fetch_air_quality_direct
from app.cache import air_quality_cache

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

def preload_cache():
    """Preload cache with common cities"""
    print("🚀 Preloading cache with common cities...")
    
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
    stats = air_quality_cache.get_stats()
    print(f"\n📊 Cache Stats:")
    print(f"   Total items: {stats['total_items']}")
    print(f"   Cache size: {stats['cache_size_mb']} MB")
    
    print("\n🎉 Cache preloading completed!")

if __name__ == "__main__":
    preload_cache() 