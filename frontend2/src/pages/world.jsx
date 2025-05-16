// world.jsx
import { useEffect, useState } from "react";
import axios from "axios";
import MapView from "../MapView.jsx";

export default function World() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get("/api/world")
      .then(res => setData(res.data))
      .catch(err => console.error("Fehler beim Laden:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-4">Lade Luftdaten...</div>;
  if (!data || data.error) return <div className="p-4 text-red-500">{data?.error || "Keine Daten verfügbar"}</div>;

  return (
      <div className="container py-5">
          <h1 className="display-4 mb-3">Luftdaten-Karte</h1>
         <MapView position={[data.location.latitude, data.location.longitude]} stations={data.stations} />
      </div>
  );
}
