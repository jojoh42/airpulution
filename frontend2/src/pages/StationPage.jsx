import { useEffect, useState } from "react";
import axios from "axios";
import { useParams, Link } from "react-router-dom";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement
} from 'chart.js';
import { Line, Bar } from "react-chartjs-2";
import "./StationPage.css";

// Registriere benötigte Chart-Komponenten
ChartJS.register(CategoryScale, LinearScale, LineElement, Title, Tooltip, Legend, PointElement, BarElement);

function StationPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [useDirectAPI, setUseDirectAPI] = useState(true);
  const { name } = useParams();
  const decodedName = decodeURIComponent(name);

  useEffect(() => {
    fetchStationData();
  }, [useDirectAPI]);

  const fetchStationData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const endpoint = useDirectAPI 
        ? `/api/station/${encodeURIComponent(decodedName)}`
        : "/api/daily-values";
      
      const response = await axios.get(endpoint);
      setData(response.data);
    } catch (err) {
      console.error("Fehler beim Laden:", err);
      setError(err.response?.data?.detail || err.response?.data?.error || "Keine Daten verfügbar");
    } finally {
      setLoading(false);
    }
  };

  const refreshData = () => {
    fetchStationData();
  };

  if (loading) {
    return (
      <div className="station-page">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Lade Daten für {decodedName}...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="station-page">
        <div className="error-container">
          <h2>⚠️ Fehler beim Laden der Daten</h2>
          <p>{error}</p>
          <button onClick={refreshData} className="btn btn-primary">
            Erneut versuchen
          </button>
          <Link to="/" className="btn btn-secondary">
            ← Zurück zur Hauptseite
          </Link>
        </div>
      </div>
    );
  }

  if (!data || !data.data) {
    return (
      <div className="station-page">
        <div className="error-container">
          <h2>📊 Keine Daten verfügbar</h2>
          <p>Für die Station "{decodedName}" konnten keine Daten gefunden werden.</p>
          <button onClick={refreshData} className="btn btn-primary">
            Erneut versuchen
          </button>
          <Link to="/" className="btn btn-secondary">
            ← Zurück zur Hauptseite
          </Link>
        </div>
      </div>
    );
  }

  // Handle both new station API format and old format
  const stationData = Array.isArray(data.data) ? data.data : [data.data];
  const station = stationData.find(s => s.station === decodedName);
  
  if (!station) {
    return (
      <div className="station-page">
        <div className="error-container">
          <h2>🏭 Station nicht gefunden</h2>
          <p>Die Station "{decodedName}" wurde nicht in den Daten gefunden.</p>
          <p>Verfügbare Stationen: {stationData.map(s => s.station).join(", ")}</p>
          <Link to="/" className="btn btn-primary">
            ← Zurück zur Hauptseite
          </Link>
        </div>
      </div>
    );
  }

  // Chart-Daten vorbereiten
  const pm10Data = station.pm10?.slice(0, 7) || [];
  const pm25Data = station.pm25?.slice(0, 7) || [];

  const pm10ChartData = {
    labels: pm10Data.map(entry =>
      entry.period?.datetimeFrom?.local?.slice(0, 10) ?? "?"
    ),
    datasets: [
      {
        label: "PM10 µg/m³",
        data: pm10Data.map(entry => entry.summary?.mean ?? entry.value ?? 0),
        backgroundColor: "rgba(255, 99, 132, 0.2)",
        borderColor: "rgba(255, 99, 132, 1)",
        borderWidth: 2,
        tension: 0.1
      }
    ]
  };

  const pm25ChartData = {
    labels: pm25Data.map(entry =>
      entry.period?.datetimeFrom?.local?.slice(0, 10) ?? "?"
    ),
    datasets: [
      {
        label: "PM2.5 µg/m³",
        data: pm25Data.map(entry => entry.summary?.mean ?? entry.value ?? 0),
        backgroundColor: "rgba(54, 162, 235, 0.2)",
        borderColor: "rgba(54, 162, 235, 1)",
        borderWidth: 2,
        tension: 0.1
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'Luftqualitätsdaten der letzten 7 Tage'
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'µg/m³'
        }
      }
    }
  };

  const getAQICategory = (value, parameter) => {
    if (parameter === 'pm25') {
      if (value <= 12) return { level: 'Gut', color: '#00e400', bgColor: '#e8f5e8' };
      if (value <= 35.4) return { level: 'Mäßig', color: '#ffff00', bgColor: '#fffbe6' };
      if (value <= 55.4) return { level: 'Ungesund für empfindliche Gruppen', color: '#ff7e00', bgColor: '#fff4e6' };
      if (value <= 150.4) return { level: 'Ungesund', color: '#ff0000', bgColor: '#ffe6e6' };
      if (value <= 250.4) return { level: 'Sehr ungesund', color: '#8f3f97', bgColor: '#f4e6f4' };
      return { level: 'Gefährlich', color: '#7e0023', bgColor: '#f4e6e6' };
    } else if (parameter === 'pm10') {
      if (value <= 54) return { level: 'Gut', color: '#00e400', bgColor: '#e8f5e8' };
      if (value <= 154) return { level: 'Mäßig', color: '#ffff00', bgColor: '#fffbe6' };
      if (value <= 254) return { level: 'Ungesund für empfindliche Gruppen', color: '#ff7e00', bgColor: '#fff4e6' };
      if (value <= 354) return { level: 'Ungesund', color: '#ff0000', bgColor: '#ffe6e6' };
      if (value <= 424) return { level: 'Sehr ungesund', color: '#8f3f97', bgColor: '#f4e6f4' };
      return { level: 'Gefährlich', color: '#7e0023', bgColor: '#f4e6e6' };
    }
    return { level: 'Unbekannt', color: '#cccccc', bgColor: '#f8f9fa' };
  };

  const latestPM10 = pm10Data[0]?.summary?.mean ?? pm10Data[0]?.value ?? null;
  const latestPM25 = pm25Data[0]?.summary?.mean ?? pm25Data[0]?.value ?? null;

  return (
    <div className="station-page">
      <div className="header-section">
        <div className="header-content">
          <h1>🏭 {station.station}</h1>
          <p className="subtitle">
            Detaillierte Luftqualitätsdaten • {data.source || "API"} • {data.response_time || "N/A"}s
            {data.cached && <span className="cache-badge">✅ Gecacht</span>}
          </p>
        </div>
        
        <div className="controls-section">
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
          
          <button onClick={refreshData} className="btn btn-primary">
            🔄 Aktualisieren
          </button>
          
          <Link to="/" className="btn btn-secondary">
            ← Zurück zur Hauptseite
          </Link>
        </div>
      </div>

      <div className="station-info-section">
        <div className="info-card">
          <h3>📍 Standort</h3>
          <p><strong>Station:</strong> {station.station}</p>
          <p><strong>Koordinaten:</strong> {station.coordinates?.latitude?.toFixed(4)}, {station.coordinates?.longitude?.toFixed(4)}</p>
          {station.distance && <p><strong>Entfernung:</strong> {(station.distance / 1000).toFixed(1)} km</p>}
        </div>
        
        <div className="info-card">
          <h3>📊 Aktuelle Werte</h3>
          {latestPM10 && (
            <div className="measurement-display" style={{ backgroundColor: getAQICategory(latestPM10, 'pm10').bgColor }}>
              <span className="label">PM10:</span>
              <span className="value" style={{ color: getAQICategory(latestPM10, 'pm10').color }}>
                {latestPM10} µg/m³
              </span>
              <span className="category">({getAQICategory(latestPM10, 'pm10').level})</span>
            </div>
          )}
          {latestPM25 && (
            <div className="measurement-display" style={{ backgroundColor: getAQICategory(latestPM25, 'pm25').bgColor }}>
              <span className="label">PM2.5:</span>
              <span className="value" style={{ color: getAQICategory(latestPM25, 'pm25').color }}>
                {latestPM25} µg/m³
              </span>
              <span className="category">({getAQICategory(latestPM25, 'pm25').level})</span>
            </div>
          )}
        </div>
      </div>

      <div className="charts-section">
        {pm10Data.length > 0 && (
          <div className="chart-container">
            <h3>📈 PM10 Verlauf (7 Tage)</h3>
            <Line data={pm10ChartData} options={chartOptions} />
          </div>
        )}
        
        {pm25Data.length > 0 && (
          <div className="chart-container">
            <h3>📈 PM2.5 Verlauf (7 Tage)</h3>
            <Line data={pm25ChartData} options={chartOptions} />
          </div>
        )}
        
        {pm10Data.length === 0 && pm25Data.length === 0 && (
          <div className="no-data-container">
            <h3>📊 Keine Messdaten verfügbar</h3>
            <p>Für diese Station sind aktuell keine Messdaten vorhanden.</p>
          </div>
        )}
      </div>

      <div className="data-table-section">
        <h3>📋 Detaillierte Messwerte</h3>
        <div className="data-tables">
          {pm10Data.length > 0 && (
            <div className="data-table">
              <h4>PM10 Werte</h4>
              <table>
                <thead>
                  <tr>
                    <th>Datum</th>
                    <th>Mittelwert (µg/m³)</th>
                    <th>Kategorie</th>
                  </tr>
                </thead>
                <tbody>
                  {pm10Data.map((entry, index) => {
                    const value = entry.summary?.mean ?? entry.value ?? 0;
                    const category = getAQICategory(value, 'pm10');
                    return (
                      <tr key={index}>
                        <td>{entry.period?.datetimeFrom?.local?.slice(0, 10) ?? "Unbekannt"}</td>
                        <td style={{ color: category.color, fontWeight: 'bold' }}>{value}</td>
                        <td>{category.level}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
          
          {pm25Data.length > 0 && (
            <div className="data-table">
              <h4>PM2.5 Werte</h4>
              <table>
                <thead>
                  <tr>
                    <th>Datum</th>
                    <th>Mittelwert (µg/m³)</th>
                    <th>Kategorie</th>
                  </tr>
                </thead>
                <tbody>
                  {pm25Data.map((entry, index) => {
                    const value = entry.summary?.mean ?? entry.value ?? 0;
                    const category = getAQICategory(value, 'pm25');
                    return (
                      <tr key={index}>
                        <td>{entry.period?.datetimeFrom?.local?.slice(0, 10) ?? "Unbekannt"}</td>
                        <td style={{ color: category.color, fontWeight: 'bold' }}>{value}</td>
                        <td>{category.level}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default StationPage;
