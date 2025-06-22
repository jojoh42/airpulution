import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import hashlib

class AirQualityDatabase:
    def __init__(self, db_path: str = "cache/air_quality.db"):
        self.db_path = db_path
        self.cache_duration = timedelta(hours=1)
        
        # Create cache directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize the database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS air_quality_cache (
                    cache_key TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    lat REAL,
                    lon REAL,
                    city TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create stations table for historical data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_name TEXT NOT NULL,
                    city TEXT,
                    lat REAL,
                    lon REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create measurements table for historical data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS measurements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    station_id INTEGER,
                    parameter TEXT NOT NULL,
                    value REAL,
                    unit TEXT,
                    timestamp TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (station_id) REFERENCES stations (id)
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_key ON air_quality_cache(cache_key)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cache_updated ON air_quality_cache(updated_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_station_name ON stations(station_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_measurements_station ON measurements(station_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_measurements_timestamp ON measurements(timestamp)')
            
            conn.commit()
    
    def _get_cache_key(self, lat: float, lon: float, city: Optional[str] = None) -> str:
        """Generate a unique cache key for the request"""
        if city:
            key_data = f"city:{city.lower().strip()}"
        else:
            # Round coordinates to reduce cache fragmentation
            key_data = f"coords:{round(lat, 3)},{round(lon, 3)}"
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, lat: float, lon: float, city: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """Get cached data if it exists and is not expired"""
        try:
            cache_key = self._get_cache_key(lat, lon, city)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get cached data with timestamp check
                cursor.execute('''
                    SELECT data, updated_at FROM air_quality_cache 
                    WHERE cache_key = ? AND updated_at > ?
                ''', (cache_key, datetime.now() - self.cache_duration))
                
                result = cursor.fetchone()
                
                if result:
                    data, updated_at = result
                    print(f"[DB-CACHE] Hit for key: {cache_key}")
                    return json.loads(data)
                else:
                    print(f"[DB-CACHE] Miss for key: {cache_key}")
                    return None
                    
        except Exception as e:
            print(f"[DB-CACHE] Error reading cache: {e}")
            return None
    
    def set(self, lat: float, lon: float, city: Optional[str] = None, data: Optional[Union[Dict[str, Any], List[Any]]] = None):
        """Store data in database cache"""
        try:
            cache_key = self._get_cache_key(lat, lon, city)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert or update cache entry
                cursor.execute('''
                    INSERT OR REPLACE INTO air_quality_cache 
                    (cache_key, data, lat, lon, city, updated_at) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    cache_key,
                    json.dumps(data, ensure_ascii=False),
                    lat,
                    lon,
                    city,
                    datetime.now()
                ))
                
                conn.commit()
                print(f"[DB-CACHE] Stored data for key: {cache_key}")
                
        except Exception as e:
            print(f"[DB-CACHE] Error storing cache: {e}")
    
    def store_historical_data(self, stations_data: List[Dict[str, Any]]):
        """Store detailed historical data for analysis"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                for station in stations_data:
                    # Insert or get station
                    cursor.execute('''
                        INSERT OR IGNORE INTO stations (station_name, city, lat, lon)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        station.get('station'),
                        station.get('city'),
                        station.get('coordinates', {}).get('latitude'),
                        station.get('coordinates', {}).get('longitude')
                    ))
                    
                    station_id = cursor.lastrowid or cursor.execute(
                        'SELECT id FROM stations WHERE station_name = ?', 
                        (station.get('station'),)
                    ).fetchone()[0]
                    
                    # Store PM2.5 measurements
                    for pm25_data in station.get('pm25', []):
                        if pm25_data.get('value'):
                            cursor.execute('''
                                INSERT INTO measurements (station_id, parameter, value, unit, timestamp)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (
                                station_id,
                                'pm25',
                                pm25_data.get('value'),
                                'µg/m³',
                                pm25_data.get('period', {}).get('datetimeFrom', {}).get('local')
                            ))
                    
                    # Store PM10 measurements
                    for pm10_data in station.get('pm10', []):
                        if pm10_data.get('value'):
                            cursor.execute('''
                                INSERT INTO measurements (station_id, parameter, value, unit, timestamp)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (
                                station_id,
                                'pm10',
                                pm10_data.get('value'),
                                'µg/m³',
                                pm10_data.get('period', {}).get('datetimeFrom', {}).get('local')
                            ))
                
                conn.commit()
                print(f"[DB-CACHE] Stored historical data for {len(stations_data)} stations")
                
        except Exception as e:
            print(f"[DB-CACHE] Error storing historical data: {e}")
    
    def get_historical_data(self, station_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get historical data for a specific station"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT m.parameter, m.value, m.unit, m.timestamp
                    FROM measurements m
                    JOIN stations s ON m.station_id = s.id
                    WHERE s.station_name = ? AND m.timestamp > ?
                    ORDER BY m.timestamp DESC
                ''', (station_name, datetime.now() - timedelta(days=days)))
                
                results = cursor.fetchall()
                return [
                    {
                        'parameter': row[0],
                        'value': row[1],
                        'unit': row[2],
                        'timestamp': row[3]
                    }
                    for row in results
                ]
                
        except Exception as e:
            print(f"[DB-CACHE] Error getting historical data: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Cache stats
                cursor.execute('SELECT COUNT(*) FROM air_quality_cache')
                cache_items = cursor.fetchone()[0]
                
                # Station stats
                cursor.execute('SELECT COUNT(*) FROM stations')
                total_stations = cursor.fetchone()[0]
                
                # Measurement stats
                cursor.execute('SELECT COUNT(*) FROM measurements')
                total_measurements = cursor.fetchone()[0]
                
                # Database size
                db_size = os.path.getsize(self.db_path)
                
                return {
                    "cache_items": cache_items,
                    "total_stations": total_stations,
                    "total_measurements": total_measurements,
                    "db_size_mb": round(db_size / (1024 * 1024), 2),
                    "cache_duration_hours": self.cache_duration.total_seconds() / 3600
                }
                
        except Exception as e:
            print(f"[DB-CACHE] Error getting stats: {e}")
            return {"error": str(e)}
    
    def clear_cache(self):
        """Clear all cached data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM air_quality_cache')
                conn.commit()
                print("[DB-CACHE] Cleared all cached data")
        except Exception as e:
            print(f"[DB-CACHE] Error clearing cache: {e}")
    
    def cleanup_expired(self):
        """Remove expired cache entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM air_quality_cache WHERE updated_at < ?', 
                             (datetime.now() - self.cache_duration,))
                deleted = cursor.rowcount
                conn.commit()
                if deleted > 0:
                    print(f"[DB-CACHE] Cleaned up {deleted} expired entries")
        except Exception as e:
            print(f"[DB-CACHE] Error cleaning up expired entries: {e}")

# Global database instance
air_quality_db = AirQualityDatabase() 