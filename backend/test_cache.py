#!/usr/bin/env python3
"""
Test cache functionality
"""

import time
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.fetcher import fetch_air_quality_direct

def test_cache():
    print("🧪 Testing cache functionality...")
    
    # Test Berlin (should be cached)
    print("\n📍 Testing Berlin (should be cached):")
    start_time = time.time()
    data = fetch_air_quality_direct(52.5200, 13.4050, 'Berlin')
    end_time = time.time()
    
    print(f"⏱️  Response time: {end_time - start_time:.3f} seconds")
    print(f"📊 Stations found: {len(data) if data else 0}")
    
    # Test Hamburg (should be cached)
    print("\n📍 Testing Hamburg (should be cached):")
    start_time = time.time()
    data = fetch_air_quality_direct(53.5511, 9.9937, 'Hamburg')
    end_time = time.time()
    
    print(f"⏱️  Response time: {end_time - start_time:.3f} seconds")
    print(f"📊 Stations found: {len(data) if data else 0}")
    
    # Test unknown city (should not be cached)
    print("\n📍 Testing unknown city (should not be cached):")
    start_time = time.time()
    data = fetch_air_quality_direct(50.0, 10.0, 'UnknownCity')
    end_time = time.time()
    
    print(f"⏱️  Response time: {end_time - start_time:.3f} seconds")
    print(f"📊 Stations found: {len(data) if data else 0}")
    
    print("\n✅ Cache test completed!")

if __name__ == "__main__":
    test_cache() 