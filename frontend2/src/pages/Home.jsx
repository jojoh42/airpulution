// Home.jsx
import { useEffect, useState } from "react";
import axios from "axios";
import MapView, { MapLegend } from "../MapView.jsx";
import BackgroundUpdater from "../components/BackgroundUpdater.jsx";
import "./Home.css";

export default function Home() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userLocation, setUserLocation] = useState(null);
  const [useDirectAPI, setUseDirectAPI] = useState(true); // Default to direct API for better performance
  const [showBackgroundUpdater, setShowBackgroundUpdater] = useState(false);

  useEffect(() => {
    getCurrentLocation();
  }, []);

  useEffect(() => {
    if (userLocation) {
      fetchData();
    }
  }, [userLocation, useDirectAPI]);

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          setUserLocation({ lat: latitude, lon: longitude });
          console.log("Standort erkannt:", latitude, longitude);
        },
        (error) => {
          console.error("Fehler beim Standort:", error);
          setError("Standort konnte nicht erkannt werden. Bitte erlaube den Zugriff auf deinen Standort.");
          setLoading(false);
        }
      );
    } else {
      setError("Geolocation wird von diesem Browser nicht unterstützt.");
      setLoading(false);
    }
  };

  const fetchData = async () => {
    if (!userLocation) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const endpoint = useDirectAPI ? "/api/direct-air-quality" : "/api/daily-values";
      const params = useDirectAPI 
        ? { lat: userLocation.lat, lon: userLocation.lon }
        : {};
      
      const response = await axios.get(endpoint, { params });
      setData(response.data);
    } catch (err) {
      console.error("Fehler beim Laden:", err);
      setError(err.response?.data?.error || "Keine Daten verfügbar");
    } finally {
      setLoading(false);
    }
  };

  const refreshData = () => {
    fetchData();
  };

  if (loading) {
    return (
      <div className="home-container">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Lade Luftdaten für deinen Standort...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="home-container">
        <div className="error-container">
          <h2>⚠️ Fehler beim Laden der Daten</h2>
          <p>{error}</p>
          <button onClick={getCurrentLocation} className="btn btn-primary">
            Standort erneut versuchen
          </button>
        </div>
      </div>
    );
  }

  if (!data || !data.data) {
    return (
      <div className="home-container">
        <div className="error-container">
          <h2>📊 Keine Daten verfügbar</h2>
          <p>Für deinen Standort konnten keine Luftdaten gefunden werden.</p>
          <button onClick={refreshData} className="btn btn-primary">
            Erneut versuchen
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="home-container">
      <div className="header-section compact">
        <div className="header-content">
          <h1>🌬️ Luftqualität in deiner Nähe</h1>
          <p className="subtitle">
            Live-Daten aus deiner Umgebung &bull; Standort: {userLocation?.lat?.toFixed(4)}, {userLocation?.lon?.toFixed(4)}
          </p>
        </div>
        <div className="controls-section compact">
          <div className="api-toggle">
            <label className="toggle-switch">
              <input
                type="checkbox"
                checked={useDirectAPI}
                onChange={(e) => setUseDirectAPI(e.target.checked)}
              />
              <span className="slider"></span>
            </label>
            <span className="toggle-label">
              {useDirectAPI ? "🚀 Direkte API (Schnell)" : "📡 Standard API"}
            </span>
          </div>
          <button 
            onClick={() => setShowBackgroundUpdater(!showBackgroundUpdater)}
            className="btn btn-secondary"
          >
            {showBackgroundUpdater ? '🔽 Updater ausblenden' : '🔄 Updater anzeigen'}
          </button>
          <button onClick={refreshData} className="btn btn-primary">
            🔄 Aktualisieren
          </button>
        </div>
      </div>

      {showBackgroundUpdater && (
        <div className="background-updater-section">
          <BackgroundUpdater />
        </div>
      )}

      <div className="data-info-section compact">
        <div className="info-card compact">
          <h3>📊 Datenquelle</h3>
          <div className="info-row"><span>API:</span> <span>{useDirectAPI ? "Direkte API" : "Standard API"}</span></div>
          <div className="info-row"><span>Quelle:</span> <span>{data.source || "API"}</span></div>
          <div className="info-row"><span>Antwortzeit:</span> <span>{data.response_time || "N/A"}s</span></div>
          {data.cached && <div className="info-row"><span>Status:</span> <span>✅ Gecacht</span></div>}
        </div>
        <div className="info-card compact">
          <h3>🏭 Messstationen</h3>
          <div className="info-row"><span>Gefunden:</span> <span>{data.data?.length || 0} Stationen</span></div>
          <div className="info-row"><span>Standort:</span> <span>{userLocation?.lat?.toFixed(4)}, {userLocation?.lon?.toFixed(4)}</span></div>
        </div>
      </div>

      <div className="map-card">
        <div className="map-section compact">
          <MapView 
            position={[userLocation.lat, userLocation.lon]} 
            stations={data.data || []} 
          />
        </div>
      </div>
      <div className="legend-below-map">
        <MapLegend isWorldwideView={false} />
      </div>

      {data.data && data.data.length > 0 && (
        <div className="stations-list-section compact">
          <h3>🏭 Messstationen in deiner Nähe</h3>
          <div className="stations-grid compact">
            {data.data.map((station, index) => (
              <div key={index} className="station-card compact">
                <h4>{station.station}</h4>
                <p className="distance">
                  📍 {station.distance ? `${(station.distance / 1000).toFixed(1)} km entfernt` : "Entfernung unbekannt"}
                </p>
                <div className="measurements">
                  {station.pm25 && station.pm25.length > 0 && (
                    <div className="measurement pm25">
                      <span className="label">PM2.5:</span>
                      <span className="value">
                        {station.pm25[0]?.summary?.mean ?? station.pm25[0]?.value ?? "-"} µg/m³
                      </span>
                    </div>
                  )}
                  {station.pm10 && station.pm10.length > 0 && (
                    <div className="measurement pm10">
                      <span className="label">PM10:</span>
                      <span className="value">
                        {station.pm10[0]?.summary?.mean ?? station.pm10[0]?.value ?? "-"} µg/m³
                      </span>
                    </div>
                  )}
                  {(!station.pm25 || station.pm25.length === 0) && (!station.pm10 || station.pm10.length === 0) && (
                    <div className="no-data">Keine aktuellen Messwerte</div>
                  )}
                </div>
                <button className="btn btn-primary details-btn" onClick={() => window.location.href = `/station/${encodeURIComponent(station.station)}`}>
                  📊 Details anzeigen
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
