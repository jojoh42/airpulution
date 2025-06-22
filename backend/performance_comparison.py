#!/usr/bin/env python3
"""
Performance comparison between different caching approaches
"""

import time
import sys
import os
import statistics

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.fetcher import fetch_air_quality_direct
from app.cache import air_quality_cache
from app.database_cache import air_quality_db

def test_file_cache():
    """Test file-based cache performance"""
    print("📁 Testing File-Based Cache...")
    times = []
    
    for i in range(5):
        start_time = time.time()
        data = fetch_air_quality_direct(52.5200, 13.4050, 'Berlin')
        end_time = time.time()
        times.append(end_time - start_time)
        print(f"  Run {i+1}: {times[-1]:.3f}s")
    
    return {
        'avg_time': statistics.mean(times),
        'min_time': min(times),
        'max_time': max(times),
        'times': times
    }

def test_database_cache():
    """Test database cache performance"""
    print("🗄️ Testing Database Cache...")
    times = []
    
    for i in range(5):
        start_time = time.time()
        data = air_quality_db.get(52.5200, 13.4050, 'Berlin')
        end_time = time.time()
        times.append(end_time - start_time)
        print(f"  Run {i+1}: {times[-1]:.3f}s")
    
    return {
        'avg_time': statistics.mean(times),
        'min_time': min(times),
        'max_time': max(times),
        'times': times
    }

def test_no_cache():
    """Test performance without cache (API calls)"""
    print("🌐 Testing No Cache (API Calls)...")
    times = []
    
    # Clear cache first
    air_quality_cache.clear()
    air_quality_db.clear_cache()
    
    for i in range(3):  # Fewer runs due to API rate limits
        start_time = time.time()
        data = fetch_air_quality_direct(52.5200, 13.4050, 'Berlin')
        end_time = time.time()
        times.append(end_time - start_time)
        print(f"  Run {i+1}: {times[-1]:.3f}s")
    
    return {
        'avg_time': statistics.mean(times),
        'min_time': min(times),
        'max_time': max(times),
        'times': times
    }

def compare_approaches():
    """Compare all caching approaches"""
    print("🚀 Performance Comparison: Caching Approaches")
    print("=" * 50)
    
    # Test each approach
    file_cache_results = test_file_cache()
    print()
    
    db_cache_results = test_database_cache()
    print()
    
    no_cache_results = test_no_cache()
    print()
    
    # Display comparison
    print("📊 Performance Comparison Results:")
    print("-" * 50)
    print(f"{'Approach':<20} {'Avg (s)':<10} {'Min (s)':<10} {'Max (s)':<10}")
    print("-" * 50)
    print(f"{'File Cache':<20} {file_cache_results['avg_time']:<10.3f} {file_cache_results['min_time']:<10.3f} {file_cache_results['max_time']:<10.3f}")
    print(f"{'Database Cache':<20} {db_cache_results['avg_time']:<10.3f} {db_cache_results['min_time']:<10.3f} {db_cache_results['max_time']:<10.3f}")
    print(f"{'No Cache (API)':<20} {no_cache_results['avg_time']:<10.3f} {no_cache_results['min_time']:<10.3f} {no_cache_results['max_time']:<10.3f}")
    
    print("\n🎯 Recommendations:")
    print("-" * 30)
    
    if file_cache_results['avg_time'] < db_cache_results['avg_time']:
        print("✅ File cache is faster for simple caching")
    else:
        print("✅ Database cache is faster and more robust")
    
    speedup_vs_api = no_cache_results['avg_time'] / min(file_cache_results['avg_time'], db_cache_results['avg_time'])
    print(f"🚀 Cache provides {speedup_vs_api:.1f}x speedup vs API calls")
    
    print("\n💡 Best choice depends on your needs:")
    print("   • File Cache: Simple, fast, no setup")
    print("   • Database Cache: Persistent, queryable, scalable")
    print("   • No Cache: Always fresh data (but slow)")

def show_database_features():
    """Show database-specific features"""
    print("\n🗄️ Database Cache Features:")
    print("-" * 30)
    
    # Get stats
    stats = air_quality_db.get_stats()
    print(f"📊 Cache items: {stats.get('cache_items', 0)}")
    print(f"📊 Total stations: {stats.get('total_stations', 0)}")
    print(f"📊 Total measurements: {stats.get('total_measurements', 0)}")
    print(f"📊 Database size: {stats.get('db_size_mb', 0)} MB")
    
    # Show historical data capability
    print("\n📈 Historical Data Capability:")
    print("   • Store detailed measurement history")
    print("   • Query trends over time")
    print("   • Analyze station performance")
    print("   • Generate reports and analytics")

if __name__ == "__main__":
    compare_approaches()
    show_database_features() 