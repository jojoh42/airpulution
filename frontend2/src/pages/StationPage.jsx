import { useEffect, useState } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";
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

// Registriere benötigte Chart-Komponenten
ChartJS.register(CategoryScale, LinearScale, LineElement, Title, Tooltip, Legend, PointElement, BarElement);

function StationPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const { name } = useParams();
  const decodedName = decodeURIComponent(name);

  useEffect(() => {
    axios.get("/api/daily-values")
      .then(res => setData(res.data))
      .catch(err => console.error("Fehler beim Laden:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>Lade Daten...</div>;
  if (!data) return <div>Fehler beim Laden der Daten</div>;

  const station = data.stations.find(s => s.station === decodedName);
  if (!station) return <div>Station nicht gefunden: {decodedName}</div>;

  // Beispiel-Daten für Chart
  const pm10Data = station.pm10?.slice(0, 7) || [];
  const chartData = {
    labels: pm10Data.map(entry =>
      entry.period?.datetimeFrom?.local?.slice(0, 10) ?? "?"
    ),
    datasets: [
      {
        label: "PM10 Ø µg/m³",
        data: pm10Data.map(entry => entry.summary?.mean ?? entry.value ?? 0),
        backgroundColor: "rgb(215,10,10)",
        borderColor: "rgba(10,198,215,0.2)"
      }
    ]
  };

  return (
      <div className="container py-5">
        <h1 className="display-5 mb-4">Luftqualität in {station.station}</h1>
          <div className="chart-container">
            <Line data={chartData} />
          </div>
          <div className="chart-container">
            <Bar data={chartData} />
          </div>
    </div>

  );
}

export default StationPage;
