import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

function MapView({ position, stations }) {
  return (
    <MapContainer center={position} zoom={10} style={{ height: "400px", width: "100%" }}>
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Marker für eigene Position */}
      <Marker position={position}>
        <Popup>Hier ist deine Position</Popup>
      </Marker>

      {/* Marker für alle Stationen */}
      {stations.map((station, index) => {
        const coords = station.coordinates;
        if (!coords) return null;

        return (
          <Marker
            key={index}
            position={[coords.latitude, coords.longitude]}
          >
            <Popup>
              <div>
                <strong>{station.station}</strong><br />
                <a href={`/station/${encodeURIComponent(station.station)}`}>PM2.5: {station.pm25[0]?.summary?.mean ?? station.pm25[0]?.value ?? "-"} µg/m³</a><br />
                <a href={`/station/${encodeURIComponent(station.station)}`}>PM10: {station.pm10[0]?.summary?.mean ?? station.pm25[0]?.value ?? "-"} µg/m³</a>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}

export default MapView;
