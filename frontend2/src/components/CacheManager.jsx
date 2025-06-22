import { useState, useEffect } from "react";
import axios from "axios";

export default function CacheManager() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/cache/stats');
      setStats(response.data);
    } catch (err) {
      console.error("Error fetching cache stats:", err);
      setError("Fehler beim Laden der Cache-Statistiken");
    }
  };

  const clearCache = async () => {
    if (!confirm("Möchten Sie wirklich den gesamten Cache löschen?")) {
      return;
    }

    setLoading(true);
    try {
      await axios.delete('/api/cache/clear');
      setStats(null);
      alert("Cache erfolgreich gelöscht!");
    } catch (err) {
      console.error("Error clearing cache:", err);
      setError("Fehler beim Löschen des Caches");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  return (
    <div className="card">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h5 className="mb-0">Cache Management</h5>
        <div>
          <button 
            className="btn btn-sm btn-outline-primary me-2"
            onClick={fetchStats}
            disabled={loading}
          >
            🔄 Aktualisieren
          </button>
          <button 
            className="btn btn-sm btn-outline-danger"
            onClick={clearCache}
            disabled={loading}
          >
            🗑️ Cache löschen
          </button>
        </div>
      </div>
      <div className="card-body">
        {error && (
          <div className="alert alert-danger">
            {error}
          </div>
        )}
        
        {stats ? (
          <div className="row">
            <div className="col-md-4">
              <div className="text-center">
                <h4 className="text-primary">{stats.total_items}</h4>
                <small className="text-muted">Gecachte Anfragen</small>
              </div>
            </div>
            <div className="col-md-4">
              <div className="text-center">
                <h4 className="text-success">{stats.cache_size_mb} MB</h4>
                <small className="text-muted">Cache-Größe</small>
              </div>
            </div>
            <div className="col-md-4">
              <div className="text-center">
                <h4 className="text-info">1h</h4>
                <small className="text-muted">Cache-Dauer</small>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center text-muted">
            Lade Cache-Statistiken...
          </div>
        )}
        
        <div className="mt-3">
          <small className="text-muted">
            💡 Cache-Daten werden 1 Stunde gespeichert. Nach dem ersten Aufruf werden Anfragen sofort beantwortet.
          </small>
        </div>
      </div>
    </div>
  );
} 