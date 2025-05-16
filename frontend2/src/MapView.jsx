import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

function MapView({ position, stations }) {
  const searchRadius = 20000; // Meter (z. B. 5 km)

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

  const isWithinRadius = (coords) => {
    const userLatLng = L.latLng(position[0], position[1]);
    const stationLatLng = L.latLng(coords.latitude, coords.longitude);
    return userLatLng.distanceTo(stationLatLng) <= searchRadius;
  };

return (
  <>
    <MapContainer center={position} zoom={10} style={{ height: "700px", width: "100%" }} className="map-container">
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Eigene Position */}
      <Marker position={position} icon={userIcon}>
        <Popup>Hier ist deine Position</Popup>
      </Marker>

      {/* Suchkreis */}
      <Circle
        center={position}
        radius={searchRadius}
        pathOptions={{ color: 'blue', fillColor: '#blue', fillOpacity: 0.1 }}
      />

      {/* Stationen im Radius */}
      {stations.map((station, index) => {
        const coords = station.coordinates;
        if (!coords || !isWithinRadius(coords)) return null;

        return (
          <Marker
            key={index}
            position={[coords.latitude, coords.longitude]}
            icon={stationIcon}
          >
            <Popup>
              <div>
                <strong>{station.station}</strong><br />
                <a href={`/station/${encodeURIComponent(station.station)}`}>
                  PM2.5: {station.pm25[0]?.summary?.mean ?? station.pm25[0]?.value ?? "-"} µg/m³
                </a><br />
                <a href={`/station/${encodeURIComponent(station.station)}`}>
                  PM10: {station.pm10[0]?.summary?.mean ?? station.pm10[0]?.value ?? "-"} µg/m³
                </a>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>

    {/* Legende separat als Overlay */}
    <div className="map-legend">
      <h4>Legende</h4>
      <div>
        <img src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png" alt="Du" /> Deine Position
      </div>
      <div>
        <img src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png" alt="Station" /> Luftmessstation
      </div>
      <div>
        <span className="legend-circle"></span> Suchradius (20 km)
      </div>
    </div>
  </>
);
}

export default MapView;
