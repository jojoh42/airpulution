#!/usr/bin/env python3
"""
Test script for background updater functionality
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000/api"

def test_background_updater():
    print("🧪 Testing Background Updater...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/background/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Server is running")
            print(f"   Background updater status: {'🟢 Running' if status.get('is_running') else '🔴 Stopped'}")
            print(f"   Cache duration: {status.get('cache_duration_hours', 'Unknown')} hours")
            print(f"   Last update: {status.get('last_popular_update', 'Unknown')}")
        else:
            print(f"❌ Server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Test cache stats
    try:
        response = requests.get(f"{BASE_URL}/cache/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Cache stats retrieved")
            print(f"   Total entries: {stats.get('total_entries', 0)}")
            print(f"   Cache size: {stats.get('cache_size_mb', 0):.2f} MB")
        else:
            print(f"❌ Cache stats error: {response.status_code}")
    except Exception as e:
        print(f"❌ Cache stats error: {e}")
    
    # Test 3: Test direct air quality endpoint
    try:
        response = requests.get(f"{BASE_URL}/direct-air-quality?lat=52.5200&lon=13.4050&city=Berlin")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Direct air quality endpoint working")
            print(f"   Source: {data.get('source', 'Unknown')}")
            print(f"   Response time: {data.get('response_time', 'Unknown')}s")
            print(f"   Stations found: {len(data.get('data', []))}")
        else:
            print(f"❌ Direct air quality error: {response.status_code}")
    except Exception as e:
        print(f"❌ Direct air quality error: {e}")
    
    # Test 4: Test force update
    try:
        response = requests.post(f"{BASE_URL}/background/force-update?city_name=Berlin&lat=52.5200&lon=13.4050")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Force update working: {result.get('message', 'Unknown')}")
        else:
            print(f"❌ Force update error: {response.status_code}")
    except Exception as e:
        print(f"❌ Force update error: {e}")
    
    print("\n🎯 Background Updater Test Complete!")
    print("📱 You can now:")
    print("   1. Visit http://localhost:5173/direct")
    print("   2. Click 'Show Background Updater'")
    print("   3. Monitor and control background updates")
    print("   4. Experience instant data access!")
    
    return True

if __name__ == "__main__":
    test_background_updater() 