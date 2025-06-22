import time
import threading
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
from sqlalchemy import text

from .fetcher import fetch_air_quality_direct
from .mysql_cache import engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundDataUpdater:
    def __init__(self):
        self.is_running = False
        self.update_thread = None
        self.cache_duration = timedelta(hours=1)  # How long to keep cache fresh
        
    def start_background_updates(self):
        """Start the background update service"""
        if self.is_running:
            logger.info("Background updater is already running")
            return
            
        self.is_running = True
        self.update_thread = threading.Thread(target=self._run_background_updates, daemon=True)
        self.update_thread.start()
        logger.info("Background data updater started")
    
    def stop_background_updates(self):
        """Stop the background update service"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join()
        logger.info("Background data updater stopped")
    
    def _run_background_updates(self):
        """Main background update loop"""
        # Schedule updates
        schedule.every(30).minutes.do(self._update_popular_cities)  # Update popular cities every 30 min
        schedule.every(2).hours.do(self._update_all_cached_data)    # Update all cached data every 2 hours
        schedule.every().day.at("06:00").do(self._full_refresh)     # Full refresh at 6 AM
        
        logger.info("Background update schedule set:")
        logger.info("  - Popular cities: every 30 minutes")
        logger.info("  - All cached data: every 2 hours")
        logger.info("  - Full refresh: daily at 6:00 AM")
        
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in background updater: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _update_popular_cities(self):
        """Update data for popular cities (frequently accessed)"""
        logger.info("Updating popular cities...")
        
        popular_cities = [
            {"name": "Berlin", "lat": 52.5200, "lon": 13.4050},
            {"name": "Hamburg", "lat": 53.5511, "lon": 9.9937},
            {"name": "München", "lat": 48.1351, "lon": 11.5820},
            {"name": "Köln", "lat": 50.9375, "lon": 6.9603},
            {"name": "Frankfurt", "lat": 50.1109, "lon": 8.6821},
        ]
        
        for city in popular_cities:
            try:
                logger.info(f"Updating {city['name']}...")
                data = fetch_air_quality_direct(city['lat'], city['lon'], city['name'])
                if data:
                    logger.info(f"✅ Updated {city['name']} with {len(data)} stations")
                else:
                    logger.warning(f"⚠️ No data for {city['name']}")
                time.sleep(10)  # Rate limiting
            except Exception as e:
                logger.error(f"❌ Error updating {city['name']}: {e}")
    
    def _update_all_cached_data(self):
        """Update all cached data that's getting stale"""
        logger.info("Updating all cached data...")
        
        try:
            # Get all cached entries
            with engine.connect() as conn:
                query = text("""
                    SELECT lat, lon, city, updated_at 
                    FROM air_quality_cache 
                    WHERE updated_at < :stale_time
                """)
                stale_time = datetime.utcnow() - self.cache_duration
                result = conn.execute(query, {"stale_time": stale_time})
                
                for row in result:
                    lat, lon, city, updated_at = row
                    try:
                        logger.info(f"Updating stale data for {city or f'({lat}, {lon})'}...")
                        data = fetch_air_quality_direct(lat, lon, city)
                        if data:
                            logger.info(f"✅ Updated stale data with {len(data)} stations")
                        time.sleep(5)  # Rate limiting
                    except Exception as e:
                        logger.error(f"❌ Error updating stale data: {e}")
                        
        except Exception as e:
            logger.error(f"❌ Error getting stale data: {e}")
    
    def _full_refresh(self):
        """Perform a full refresh of all data"""
        logger.info("Starting full data refresh...")
        
        all_cities = [
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
        
        for city in all_cities:
            try:
                logger.info(f"Full refresh: {city['name']}...")
                data = fetch_air_quality_direct(city['lat'], city['lon'], city['name'])
                if data:
                    logger.info(f"✅ Full refresh: {city['name']} with {len(data)} stations")
                time.sleep(15)  # More conservative rate limiting for full refresh
            except Exception as e:
                logger.error(f"❌ Error in full refresh for {city['name']}: {e}")
        
        logger.info("Full data refresh completed")
    
    def force_update_city(self, city_name: str, lat: float, lon: float):
        """Force update a specific city (for manual updates)"""
        try:
            logger.info(f"Force updating {city_name}...")
            data = fetch_air_quality_direct(lat, lon, city_name)
            if data:
                logger.info(f"✅ Force updated {city_name} with {len(data)} stations")
                return True
            else:
                logger.warning(f"⚠️ No data for {city_name}")
                return False
        except Exception as e:
            logger.error(f"❌ Error force updating {city_name}: {e}")
            return False
    
    def get_update_status(self) -> Dict[str, Any]:
        """Get the status of background updates"""
        return {
            "is_running": self.is_running,
            "last_popular_update": self._get_last_update_time("popular"),
            "last_full_update": self._get_last_update_time("full"),
            "next_scheduled_update": self._get_next_scheduled_update(),
            "cache_duration_hours": self.cache_duration.total_seconds() / 3600
        }
    
    def _get_last_update_time(self, update_type: str) -> str:
        """Get the last update time for a specific type"""
        try:
            with engine.connect() as conn:
                query = text("SELECT MAX(updated_at) FROM air_quality_cache")
                result = conn.execute(query).fetchone()
                if result and result[0]:
                    return result[0].isoformat()
        except Exception as e:
            logger.error(f"Error getting last update time: {e}")
        return "Unknown"
    
    def _get_next_scheduled_update(self) -> str:
        """Get the next scheduled update time"""
        try:
            next_job = schedule.next_run()
            if next_job:
                return next_job.isoformat()
        except Exception as e:
            logger.error(f"Error getting next scheduled update: {e}")
        return "Unknown"

# Global background updater instance
background_updater = BackgroundDataUpdater() 