import React, { useState, useEffect } from 'react';
import axios from "axios";
import MapView from "../MapView.jsx";
import DirectFetcherTest from "../components/DirectFetcherTest.jsx";
import CacheManager from "../components/CacheManager.jsx";
import BackgroundUpdater from '../components/BackgroundUpdater';
import './DirectAirQuality.css';

const DirectAirQuality = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [location, setLocation] = useState(null);
  const [searchCity, setSearchCity] = useState('');
  const [showBackgroundUpdater, setShowBackgroundUpdater] = useState(false);

  const API_BASE = 'http://localhost:8000/api';

  useEffect(() => {
    getCurrentLocation();
  }, []);

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setLocation({ lat: latitude, lon: longitude });
          fetchAirQuality(latitude, longitude);
        },
        (error) => {
          console.error('Error getting location:', error);
          setError('Could not get your location. Please search for a city.');
        }
      );
    } else {
      setError('Geolocation is not supported by this browser.');
    }
  };

  const fetchAirQuality = async (lat, lon, city = null) => {
    setLoading(true);
    setError(null);
    
    try {
      const params = new URLSearchParams({
        lat: lat.toString(),
        lon: lon.toString()
      });
      
      if (city) {
        params.append('city', city);
      }
      
      const response = await fetch(`${API_BASE}/direct-air-quality?${params}`);
      const result = await response.json();
      
      if (response.ok) {
        setData(result);
      } else {
        setError(result.detail || 'Failed to fetch air quality data');
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCitySearch = (e) => {
    e.preventDefault();
    if (searchCity.trim()) {
      // Use approximate coordinates for the city
      const cityCoords = {
        'Berlin': { lat: 52.5200, lon: 13.4050 },
        'Hamburg': { lat: 53.5511, lon: 9.9937 },
        'München': { lat: 48.1351, lon: 11.5820 },
        'Köln': { lat: 50.9375, lon: 6.9603 },
        'Frankfurt': { lat: 50.1109, lon: 8.6821 },
        'Stuttgart': { lat: 48.7758, lon: 9.1829 },
        'Düsseldorf': { lat: 51.2277, lon: 6.7735 },
        'Dortmund': { lat: 51.5136, lon: 7.4653 },
        'Essen': { lat: 51.4556, lon: 7.0116 },
        'Leipzig': { lat: 51.3397, lon: 12.3731 },
      };
      
      const coords = cityCoords[searchCity];
      if (coords) {
        setLocation(coords);
        fetchAirQuality(coords.lat, coords.lon, searchCity);
      } else {
        setError('City not found. Please try a major German city.');
      }
    }
  };

  const getAQICategory = (value, parameter) => {
    if (parameter === 'pm25') {
      if (value <= 12) return { level: 'Good', color: '#00e400' };
      if (value <= 35.4) return { level: 'Moderate', color: '#ffff00' };
      if (value <= 55.4) return { level: 'Unhealthy for Sensitive Groups', color: '#ff7e00' };
      if (value <= 150.4) return { level: 'Unhealthy', color: '#ff0000' };
      if (value <= 250.4) return { level: 'Very Unhealthy', color: '#8f3f97' };
      return { level: 'Hazardous', color: '#7e0023' };
    } else if (parameter === 'pm10') {
      if (value <= 54) return { level: 'Good', color: '#00e400' };
      if (value <= 154) return { level: 'Moderate', color: '#ffff00' };
      if (value <= 254) return { level: 'Unhealthy for Sensitive Groups', color: '#ff7e00' };
      if (value <= 354) return { level: 'Unhealthy', color: '#ff0000' };
      if (value <= 424) return { level: 'Very Unhealthy', color: '#8f3f97' };
      return { level: 'Hazardous', color: '#7e0023' };
    }
    return { level: 'Unknown', color: '#cccccc' };
  };

  return (
    <div className="direct-air-quality">
      <div className="header">
        <h1>🌬️ Direct Air Quality Data</h1>
        <p>Get real-time air quality data with instant cache access</p>
      </div>

      <div className="controls">
        <div className="location-controls">
          <button 
            onClick={getCurrentLocation}
            className="btn btn-primary"
            disabled={loading}
          >
            📍 Use My Location
          </button>
          
          <form onSubmit={handleCitySearch} className="city-search">
            <input
              type="text"
              value={searchCity}
              onChange={(e) => setSearchCity(e.target.value)}
              placeholder="Search for a city (e.g., Berlin, Hamburg)"
              className="city-input"
            />
            <button type="submit" className="btn btn-secondary" disabled={loading}>
              🔍 Search
            </button>
          </form>
        </div>

        <button 
          onClick={() => setShowBackgroundUpdater(!showBackgroundUpdater)}
          className="btn btn-info"
        >
          {showBackgroundUpdater ? '🔽 Hide' : '🔄 Show'} Background Updater
        </button>
      </div>

      {showBackgroundUpdater && (
        <BackgroundUpdater />
      )}

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Fetching air quality data...</p>
        </div>
      )}

      {error && (
        <div className="error">
          <p>❌ {error}</p>
        </div>
      )}

      {data && (
        <div className="results">
          <div className="data-info">
            <h3>📊 Air Quality Data</h3>
            <div className="info-grid">
              <div className="info-item">
                <span className="label">Source:</span>
                <span className="value">{data.source}</span>
              </div>
              <div className="info-item">
                <span className="label">Response Time:</span>
                <span className="value">{data.response_time}s</span>
              </div>
              {data.cached && (
                <div className="info-item">
                  <span className="label">Status:</span>
                  <span className="value cached">✅ Cached</span>
                </div>
              )}
            </div>
          </div>

          <div className="stations">
            <h3>🏭 Monitoring Stations ({data.data?.length || 0})</h3>
            {data.data?.map((station, index) => (
              <div key={index} className="station-card">
                <div className="station-header">
                  <h4>{station.station}</h4>
                  <span className="distance">{station.distance}km away</span>
                </div>
                
                <div className="coordinates">
                  📍 {station.coordinates?.latitude?.toFixed(4)}, {station.coordinates?.longitude?.toFixed(4)}
                </div>

                <div className="measurements">
                  {station.pm25 && station.pm25.length > 0 && (
                    <div className="measurement">
                      <span className="parameter">PM2.5:</span>
                      {station.pm25.map((pm25, idx) => {
                        const category = getAQICategory(pm25.value, 'pm25');
                        return (
                          <span 
                            key={idx} 
                            className="value"
                            style={{ backgroundColor: category.color, color: '#000' }}
                          >
                            {pm25.value} µg/m³ ({category.level})
                          </span>
                        );
                      })}
                    </div>
                  )}

                  {station.pm10 && station.pm10.length > 0 && (
                    <div className="measurement">
                      <span className="parameter">PM10:</span>
                      {station.pm10.map((pm10, idx) => {
                        const category = getAQICategory(pm10.value, 'pm10');
                        return (
                          <span 
                            key={idx} 
                            className="value"
                            style={{ backgroundColor: category.color, color: '#000' }}
                          >
                            {pm10.value} µg/m³ ({category.level})
                          </span>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DirectAirQuality; 