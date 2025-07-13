import React, { useState, useEffect } from 'react';
import './BackgroundUpdater.css';
import { API_BASE } from '../config';

const BackgroundUpdater = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchStatus();
    // Poll status every 30 seconds
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/background/status`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Error fetching background status:', error);
      // Don't show error to user, just log it
    }
  };

  const startUpdates = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/background/start`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setMessage(data.message);
      fetchStatus();
    } catch (error) {
      console.error('Error starting background updates:', error);
      setMessage('Error starting background updates');
    } finally {
      setLoading(false);
    }
  };

  const stopUpdates = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/background/stop`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setMessage(data.message);
      fetchStatus();
    } catch (error) {
      console.error('Error stopping background updates:', error);
      setMessage('Error stopping background updates');
    } finally {
      setLoading(false);
    }
  };

  const forceUpdateCity = async (cityName, lat, lon) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/background/force-update?city_name=${cityName}&lat=${lat}&lon=${lon}`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setMessage(data.message);
      fetchStatus();
    } catch (error) {
      console.error('Error force updating city:', error);
      setMessage('Error force updating city');
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timeStr) => {
    if (!timeStr || timeStr === 'Unknown') return 'Unknown';
    try {
      return new Date(timeStr).toLocaleString();
    } catch {
      return timeStr;
    }
  };

  if (!status) {
    return (
      <div className="background-updater">
        <div className="loading-status">
          <div className="spinner"></div>
          <p>Loading background updater status...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="background-updater">
      <h3>🔄 Background Data Updater</h3>
      
      <div className="status-section">
        <div className="status-item">
          <span className="label">Status:</span>
          <span className={`value ${status.is_running ? 'running' : 'stopped'}`}>
            {status.is_running ? '🟢 Running' : '🔴 Stopped'}
          </span>
        </div>
        
        <div className="status-item">
          <span className="label">Cache Duration:</span>
          <span className="value">{status.cache_duration_hours} hours</span>
        </div>
        
        <div className="status-item">
          <span className="label">Last Update:</span>
          <span className="value">{formatTime(status.last_popular_update)}</span>
        </div>
        
        <div className="status-item">
          <span className="label">Next Update:</span>
          <span className="value">{formatTime(status.next_scheduled_update)}</span>
        </div>
      </div>

      <div className="controls-section">
        <h4>Controls</h4>
        <div className="button-group">
          <button 
            onClick={startUpdates} 
            disabled={loading || status.is_running}
            className="btn btn-start"
          >
            {loading ? 'Starting...' : 'Start Updates'}
          </button>
          
          <button 
            onClick={stopUpdates} 
            disabled={loading || !status.is_running}
            className="btn btn-stop"
          >
            {loading ? 'Stopping...' : 'Stop Updates'}
          </button>
        </div>
      </div>

      <div className="force-update-section">
        <h4>Force Update Cities</h4>
        <div className="city-buttons">
          {[
            { name: 'Berlin', lat: 52.5200, lon: 13.4050 },
            { name: 'Hamburg', lat: 53.5511, lon: 9.9937 },
            { name: 'München', lat: 48.1351, lon: 11.5820 },
            { name: 'Köln', lat: 50.9375, lon: 6.9603 },
            { name: 'Frankfurt', lat: 50.1109, lon: 8.6821 },
          ].map(city => (
            <button
              key={city.name}
              onClick={() => forceUpdateCity(city.name, city.lat, city.lon)}
              disabled={loading}
              className="btn btn-city"
            >
              {city.name}
            </button>
          ))}
        </div>
      </div>

      {message && (
        <div className="message">
          {message}
        </div>
      )}

      <div className="schedule-info">
        <h4>📅 Update Schedule</h4>
        <ul>
          <li>🕐 Popular cities: every 30 minutes</li>
          <li>🕑 All cached data: every 2 hours</li>
          <li>🌅 Full refresh: daily at 6:00 AM</li>
        </ul>
      </div>
    </div>
  );
};

export default BackgroundUpdater; 