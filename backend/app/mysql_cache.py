import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import hashlib
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Text, Float, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), "..", "db.env")
load_dotenv(dotenv_path=dotenv_path)

# Database setup (reusing your existing configuration)
DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AirQualityCache(Base):
    __tablename__ = "air_quality_cache"
    
    cache_key = Column(String(32), primary_key=True)
    data = Column(Text, nullable=False)
    lat = Column(Float)
    lon = Column(Float)
    city = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AirQualityStations(Base):
    __tablename__ = "air_quality_stations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    station_name = Column(String(255), nullable=False, index=True)
    city = Column(String(255), index=True)
    lat = Column(Float)
    lon = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class AirQualityMeasurements(Base):
    __tablename__ = "air_quality_measurements"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(Integer, nullable=False, index=True)
    parameter = Column(String(10), nullable=False)  # pm25, pm10
    value = Column(Float)
    unit = Column(String(10))
    timestamp = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MySQLAirQualityCache:
    def __init__(self):
        self.cache_duration = timedelta(hours=1)
        self._init_tables()
    
    def _init_tables(self):
        """Initialize database tables if they don't exist"""
        try:
            Base.metadata.create_all(bind=engine)
            print("[MYSQL-CACHE] Database tables initialized")
        except Exception as e:
            print(f"[MYSQL-CACHE] Error initializing tables: {e}")
    
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
            
            with engine.connect() as conn:
                # Get cached data with timestamp check
                query = text("""
                    SELECT data, updated_at FROM air_quality_cache 
                    WHERE cache_key = :cache_key AND updated_at > :expiry_time
                """)
                
                result = conn.execute(query, {
                    "cache_key": cache_key,
                    "expiry_time": datetime.utcnow() - self.cache_duration
                }).fetchone()
                
                if result:
                    data, updated_at = result
                    print(f"[MYSQL-CACHE] Hit for key: {cache_key}")
                    return json.loads(data)
                else:
                    print(f"[MYSQL-CACHE] Miss for key: {cache_key}")
                    return None
                    
        except Exception as e:
            print(f"[MYSQL-CACHE] Error reading cache: {e}")
            return None
    
    def set(self, lat: float, lon: float, city: Optional[str] = None, data: Optional[Union[Dict[str, Any], List[Any]]] = None):
        """Store data in MySQL cache"""
        try:
            cache_key = self._get_cache_key(lat, lon, city)
            
            with engine.connect() as conn:
                # Insert or update cache entry
                query = text("""
                    INSERT INTO air_quality_cache (cache_key, data, lat, lon, city, updated_at)
                    VALUES (:cache_key, :data, :lat, :lon, :city, :updated_at)
                    ON DUPLICATE KEY UPDATE 
                        data = VALUES(data),
                        lat = VALUES(lat),
                        lon = VALUES(lon),
                        city = VALUES(city),
                        updated_at = VALUES(updated_at)
                """)
                
                conn.execute(query, {
                    "cache_key": cache_key,
                    "data": json.dumps(data, ensure_ascii=False),
                    "lat": lat,
                    "lon": lon,
                    "city": city,
                    "updated_at": datetime.utcnow()
                })
                conn.commit()
                print(f"[MYSQL-CACHE] Stored data for key: {cache_key}")
                
        except Exception as e:
            print(f"[MYSQL-CACHE] Error storing cache: {e}")
    
    def store_historical_data(self, stations_data: List[Dict[str, Any]]):
        """Store detailed historical data for analysis"""
        try:
            with engine.connect() as conn:
                for station in stations_data:
                    # Insert or get station
                    station_query = text("""
                        INSERT IGNORE INTO air_quality_stations (station_name, city, lat, lon)
                        VALUES (:station_name, :city, :lat, :lon)
                    """)
                    
                    conn.execute(station_query, {
                        "station_name": station.get('station'),
                        "city": station.get('city'),
                        "lat": station.get('coordinates', {}).get('latitude'),
                        "lon": station.get('coordinates', {}).get('longitude')
                    })
                    
                    # Get station ID
                    station_id_query = text("""
                        SELECT id FROM air_quality_stations WHERE station_name = :station_name
                    """)
                    
                    station_result = conn.execute(station_id_query, {
                        "station_name": station.get('station')
                    }).fetchone()
                    
                    if station_result:
                        station_id = station_result[0]
                        
                        # Store PM2.5 measurements
                        for pm25_data in station.get('pm25', []):
                            if pm25_data.get('value'):
                                # Parse timestamp properly
                                timestamp_str = pm25_data.get('period', {}).get('datetimeFrom', {}).get('local')
                                try:
                                    if timestamp_str:
                                        # Remove timezone info and parse
                                        timestamp_str = timestamp_str.split('+')[0].split('-')[0]  # Remove timezone
                                        timestamp = datetime.fromisoformat(timestamp_str.replace('T', ' '))
                                    else:
                                        timestamp = datetime.utcnow()
                                except:
                                    timestamp = datetime.utcnow()
                                
                                measurement_query = text("""
                                    INSERT INTO air_quality_measurements 
                                    (station_id, parameter, value, unit, timestamp)
                                    VALUES (:station_id, :parameter, :value, :unit, :timestamp)
                                """)
                                
                                conn.execute(measurement_query, {
                                    "station_id": station_id,
                                    "parameter": "pm25",
                                    "value": pm25_data.get('value'),
                                    "unit": "µg/m³",
                                    "timestamp": timestamp
                                })
                        
                        # Store PM10 measurements
                        for pm10_data in station.get('pm10', []):
                            if pm10_data.get('value'):
                                # Parse timestamp properly
                                timestamp_str = pm10_data.get('period', {}).get('datetimeFrom', {}).get('local')
                                try:
                                    if timestamp_str:
                                        # Remove timezone info and parse
                                        timestamp_str = timestamp_str.split('+')[0].split('-')[0]  # Remove timezone
                                        timestamp = datetime.fromisoformat(timestamp_str.replace('T', ' '))
                                    else:
                                        timestamp = datetime.utcnow()
                                except:
                                    timestamp = datetime.utcnow()
                                
                                measurement_query = text("""
                                    INSERT INTO air_quality_measurements 
                                    (station_id, parameter, value, unit, timestamp)
                                    VALUES (:station_id, :parameter, :value, :unit, :timestamp)
                                """)
                                
                                conn.execute(measurement_query, {
                                    "station_id": station_id,
                                    "parameter": "pm10",
                                    "value": pm10_data.get('value'),
                                    "unit": "µg/m³",
                                    "timestamp": timestamp
                                })
                
                conn.commit()
                print(f"[MYSQL-CACHE] Stored historical data for {len(stations_data)} stations")
                
        except Exception as e:
            print(f"[MYSQL-CACHE] Error storing historical data: {e}")
    
    def get_historical_data(self, station_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get historical data for a specific station"""
        try:
            with engine.connect() as conn:
                query = text("""
                    SELECT m.parameter, m.value, m.unit, m.timestamp
                    FROM air_quality_measurements m
                    JOIN air_quality_stations s ON m.station_id = s.id
                    WHERE s.station_name = :station_name AND m.timestamp > :start_date
                    ORDER BY m.timestamp DESC
                """)
                
                results = conn.execute(query, {
                    "station_name": station_name,
                    "start_date": datetime.utcnow() - timedelta(days=days)
                }).fetchall()
                
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
            print(f"[MYSQL-CACHE] Error getting historical data: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with engine.connect() as conn:
                # Cache stats
                cache_query = text("SELECT COUNT(*) FROM air_quality_cache")
                cache_result = conn.execute(cache_query).fetchone()
                cache_items = cache_result[0] if cache_result and cache_result[0] is not None else 0
                
                # Station stats
                station_query = text("SELECT COUNT(*) FROM air_quality_stations")
                station_result = conn.execute(station_query).fetchone()
                total_stations = station_result[0] if station_result and station_result[0] is not None else 0
                
                # Measurement stats
                measurement_query = text("SELECT COUNT(*) FROM air_quality_measurements")
                measurement_result = conn.execute(measurement_query).fetchone()
                total_measurements = measurement_result[0] if measurement_result and measurement_result[0] is not None else 0
                
                # Database size (approximate)
                size_query = text("""
                    SELECT 
                        ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'DB Size in MB'
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() 
                    AND table_name IN ('air_quality_cache', 'air_quality_stations', 'air_quality_measurements')
                """)
                
                size_result = conn.execute(size_query).fetchone()
                db_size_mb = size_result[0] if size_result and size_result[0] is not None else 0
                
                return {
                    "cache_items": cache_items,
                    "total_stations": total_stations,
                    "total_measurements": total_measurements,
                    "db_size_mb": db_size_mb,
                    "cache_duration_hours": self.cache_duration.total_seconds() / 3600
                }
                
        except Exception as e:
            print(f"[MYSQL-CACHE] Error getting stats: {e}")
            return {"error": str(e)}
    
    def clear_cache(self):
        """Clear all cached data"""
        try:
            with engine.connect() as conn:
                conn.execute(text("DELETE FROM air_quality_cache"))
                conn.commit()
                print("[MYSQL-CACHE] Cleared all cached data")
        except Exception as e:
            print(f"[MYSQL-CACHE] Error clearing cache: {e}")
    
    def cleanup_expired(self):
        """Remove expired cache entries"""
        try:
            with engine.connect() as conn:
                query = text("DELETE FROM air_quality_cache WHERE updated_at < :expiry_time")
                result = conn.execute(query, {
                    "expiry_time": datetime.utcnow() - self.cache_duration
                })
                deleted = result.rowcount
                conn.commit()
                if deleted > 0:
                    print(f"[MYSQL-CACHE] Cleaned up {deleted} expired entries")
        except Exception as e:
            print(f"[MYSQL-CACHE] Error cleaning up expired entries: {e}")
    
    def get_top_cities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top cities by cache hits"""
        try:
            with engine.connect() as conn:
                query = text("""
                    SELECT city, COUNT(*) as hits, 
                           MAX(updated_at) as last_updated
                    FROM air_quality_cache 
                    WHERE city IS NOT NULL 
                    GROUP BY city 
                    ORDER BY hits DESC 
                    LIMIT :limit
                """)
                
                result = conn.execute(query, {"limit": limit})
                return [{"city": row[0], "hits": row[1], "last_updated": row[2]} for row in result]
                
        except Exception as e:
            print(f"[MYSQL-CACHE] Error getting top cities: {e}")
            return []

    def get_station_by_name(self, station_name: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached data for a specific station by name"""
        try:
            with engine.connect() as conn:
                # First try to find the station in recent cache entries
                query = text("""
                    SELECT data, updated_at 
                    FROM air_quality_cache 
                    WHERE data LIKE :station_pattern 
                    AND updated_at > :expiry_time
                    ORDER BY updated_at DESC 
                    LIMIT 1
                """)
                
                station_pattern = f'%"station": "{station_name}"%'
                expiry_time = datetime.utcnow() - self.cache_duration
                
                result = conn.execute(query, {
                    "station_pattern": station_pattern,
                    "expiry_time": expiry_time
                }).fetchone()
                
                if result:
                    data, updated_at = result
                    cached_data = json.loads(data)
                    
                    # Filter to only return the specific station
                    if isinstance(cached_data, list):
                        station_data = [station for station in cached_data if station.get("station") == station_name]
                        if station_data:
                            print(f"[MYSQL-CACHE] Found station '{station_name}' in cache")
                            return station_data
                
                # If not found in cache, try to get from historical data
                historical_query = text("""
                    SELECT s.station_name, s.city, s.lat, s.lon,
                           m.parameter, m.value, m.unit, m.timestamp
                    FROM air_quality_stations s
                    LEFT JOIN air_quality_measurements m ON s.id = m.station_id
                    WHERE s.station_name = :station_name
                    AND m.timestamp > :recent_time
                    ORDER BY m.timestamp DESC
                """)
                
                recent_time = datetime.utcnow() - timedelta(days=7)
                historical_result = conn.execute(historical_query, {
                    "station_name": station_name,
                    "recent_time": recent_time
                }).fetchall()
                
                if historical_result:
                    # Reconstruct station data from historical measurements
                    pm25_data = []
                    pm10_data = []
                    
                    for row in historical_result:
                        if row[4] == "pm25" and row[5] is not None:
                            pm25_data.append({
                                "value": row[5],
                                "unit": row[6],
                                "period": {
                                    "datetimeFrom": {
                                        "local": row[7].isoformat() if row[7] else None
                                    }
                                }
                            })
                        elif row[4] == "pm10" and row[5] is not None:
                            pm10_data.append({
                                "value": row[5],
                                "unit": row[6],
                                "period": {
                                    "datetimeFrom": {
                                        "local": row[7].isoformat() if row[7] else None
                                    }
                                }
                            })
                    
                    station_data = [{
                        "station": station_name,
                        "city": historical_result[0][1],
                        "coordinates": {
                            "latitude": historical_result[0][2],
                            "longitude": historical_result[0][3]
                        },
                        "pm25": pm25_data,
                        "pm10": pm10_data
                    }]
                    
                    print(f"[MYSQL-CACHE] Found station '{station_name}' in historical data")
                    return station_data
                
                print(f"[MYSQL-CACHE] Station '{station_name}' not found in cache or historical data")
                return None
                
        except Exception as e:
            print(f"[MYSQL-CACHE] Error getting station by name: {e}")
            return None

# Global MySQL cache instance
mysql_air_quality_cache = MySQLAirQualityCache() 