import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import hashlib

class AirQualityCache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "air_quality_cache.json")
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
    
    def _get_cache_key(self, lat: float, lon: float, city: Optional[str] = None) -> str:
        """Generate a unique cache key for the request"""
        if city:
            key_data = f"city:{city.lower().strip()}"
        else:
            # Round coordinates to reduce cache fragmentation
            key_data = f"coords:{round(lat, 3)},{round(lon, 3)}"
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, lat: float, lon: float, city: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get cached data if it exists and is not expired"""
        try:
            if not os.path.exists(self.cache_file):
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            cache_key = self._get_cache_key(lat, lon, city)
            
            if cache_key not in cache_data:
                return None
            
            cached_item = cache_data[cache_key]
            cached_time = datetime.fromisoformat(cached_item['timestamp'])
            
            # Check if cache is still valid
            if datetime.now() - cached_time < self.cache_duration:
                print(f"[CACHE] Hit for key: {cache_key}")
                return cached_item['data']
            else:
                print(f"[CACHE] Expired for key: {cache_key}")
                # Remove expired item
                del cache_data[cache_key]
                self._save_cache(cache_data)
                return None
                
        except Exception as e:
            print(f"[CACHE] Error reading cache: {e}")
            return None
    
    def set(self, lat: float, lon: float, city: Optional[str] = None, data: Optional[Union[Dict[str, Any], List[Any]]] = None):
        """Store data in cache"""
        try:
            cache_data = {}
            
            # Load existing cache
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
            
            cache_key = self._get_cache_key(lat, lon, city)
            
            # Store new data
            cache_data[cache_key] = {
                'timestamp': datetime.now().isoformat(),
                'data': data,
                'lat': lat,
                'lon': lon,
                'city': city
            }
            
            self._save_cache(cache_data)
            print(f"[CACHE] Stored data for key: {cache_key}")
            
        except Exception as e:
            print(f"[CACHE] Error storing cache: {e}")
    
    def _save_cache(self, cache_data: Dict[str, Any]):
        """Save cache data to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[CACHE] Error saving cache: {e}")
    
    def clear(self):
        """Clear all cached data"""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                print("[CACHE] Cleared all cached data")
        except Exception as e:
            print(f"[CACHE] Error clearing cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if not os.path.exists(self.cache_file):
                return {"total_items": 0, "cache_size": 0}
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            cache_size = os.path.getsize(self.cache_file)
            
            return {
                "total_items": len(cache_data),
                "cache_size": cache_size,
                "cache_size_mb": round(cache_size / (1024 * 1024), 2)
            }
        except Exception as e:
            print(f"[CACHE] Error getting stats: {e}")
            return {"error": str(e)}

# Global cache instance
air_quality_cache = AirQualityCache() 