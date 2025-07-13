import { useState } from "react";
import axios from "axios";
import { API_BASE } from '../config';

export default function DirectFetcherTest() {
  const [lat, setLat] = useState("");
  const [lon, setLon] = useState("");
  const [city, setCity] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const testDirectFetcher = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const params = new URLSearchParams();
      
      if (lat && lon) {
        params.append('lat', lat);
        params.append('lon', lon);
      }
      
      if (city) {
        params.append('city', city);
      }

      const response = await axios.get(`${API_BASE}/direct-air-quality?${params}`);
      setResult(response.data);
    } catch (err) {
      console.error("Test error:", err);
      setError(err.response?.data?.error || "Fehler beim Testen");
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setResult(null);
    setError(null);
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLat(position.coords.latitude.toString());
          setLon(position.coords.longitude.toString());
        },
        (error) => {
          console.error("Geolocation error:", error);
          setError("Standort konnte nicht ermittelt werden");
        }
      );
    } else {
      setError("Geolocation wird nicht unterstützt");
    }
  };

  return (
    <div className="card">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h5 className="mb-0">Direct Fetcher Test</h5>
        <button 
          className="btn btn-sm btn-outline-secondary"
          onClick={getCurrentLocation}
          title="Aktuelle Position verwenden"
        >
          📍
        </button>
      </div>
      <div className="card-body">
        <div className="row mb-3">
          <div className="col-md-4">
            <label className="form-label">Latitude</label>
            <input
              type="number"
              step="any"
              className="form-control"
              placeholder="52.5200"
              value={lat}
              onChange={(e) => setLat(e.target.value)}
            />
          </div>
          <div className="col-md-4">
            <label className="form-label">Longitude</label>
            <input
              type="number"
              step="any"
              className="form-control"
              placeholder="13.4050"
              value={lon}
              onChange={(e) => setLon(e.target.value)}
            />
          </div>
          <div className="col-md-4">
            <label className="form-label">Stadt (optional)</label>
            <input
              type="text"
              className="form-control"
              placeholder="Berlin"
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
          </div>
        </div>

        <div className="d-flex gap-2 mb-3">
          <button
            className="btn btn-primary"
            onClick={testDirectFetcher}
            disabled={loading || (!lat && !lon && !city)}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                Teste...
              </>
            ) : (
              "Direct Fetcher testen"
            )}
          </button>
          <button
            className="btn btn-outline-secondary"
            onClick={clearResults}
          >
            Ergebnisse löschen
          </button>
        </div>

        {error && (
          <div className="alert alert-danger">
            <strong>Fehler:</strong> {error}
          </div>
        )}

        {result && (
          <div className="alert alert-success">
            <h6>Ergebnis:</h6>
            <pre className="mb-0" style={{ fontSize: '0.9em', maxHeight: '300px', overflow: 'auto' }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
} 