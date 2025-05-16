import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

function MapView({ position, stations }) {
    const userIcon = new L.Icon({
          iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png',
          shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
          popupAnchor: [1, -34],
          shadowSize: [41, 41]
});
    const stationIcon = new L.Icon({
          iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
          shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
          iconSize: [25, 41],
          iconAnchor: [12, 41],
          popupAnchor: [1, -34],
          shadowSize: [41, 41]
});

  return (
    <MapContainer center={position} zoom={10} style={{ height: "400px", width: "100%" } } className="map-container">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Marker für eigene Position */}
      <Marker position={position} icon={userIcon}>
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
            icon={stationIcon}
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
