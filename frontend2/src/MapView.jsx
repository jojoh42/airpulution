import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

export function MapLegend({ isWorldwideView = false }) {
  return (
    <div className="map-legend">
      <h4>Legende</h4>
      {!isWorldwideView && (
        <>
          <div>
            <img src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png" alt="Du" /> Deine Position
          </div>
          <div>
            <span className="legend-circle"></span> Suchradius (20 km)
          </div>
        </>
      )}
      <div>
        <img src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png" alt="Station" /> Luftmessstation
      </div>
      <div style={{ marginTop: '10px', fontSize: '12px' }}>
        <div style={{ color: '#00e400' }}>🟢 Gut</div>
        <div style={{ color: '#ffff00' }}>🟡 Mäßig</div>
        <div style={{ color: '#ff7e00' }}>🟠 Ungesund (empfindlich)</div>
        <div style={{ color: '#ff0000' }}>🔴 Ungesund</div>
        <div style={{ color: '#8f3f97' }}>🟣 Sehr ungesund</div>
        <div style={{ color: '#7e0023' }}>🟤 Gefährlich</div>
      </div>
    </div>
  );
}

function MapView({ position, stations }) {
  const searchRadius = 20000; // Meter (z. B. 20 km)

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

  const getAQIColor = (value, parameter) => {
    if (parameter === 'pm25') {
      if (value <= 12) return '#00e400';
      if (value <= 35.4) return '#ffff00';
      if (value <= 55.4) return '#ff7e00';
      if (value <= 150.4) return '#ff0000';
      if (value <= 250.4) return '#8f3f97';
      return '#7e0023';
    } else if (parameter === 'pm10') {
      if (value <= 54) return '#00e400';
      if (value <= 154) return '#ffff00';
      if (value <= 254) return '#ff7e00';
      if (value <= 354) return '#ff0000';
      if (value <= 424) return '#8f3f97';
      return '#7e0023';
    }
    return '#cccccc';
  };

  const getLatestValue = (station, parameter) => {
    const data_array = station[parameter];
    if (data_array && data_array.length > 0) {
      const latest_entry = data_array[0];
      return latest_entry?.summary?.mean ?? latest_entry?.value ?? null;
    }
    return null;
  };

  // Check if this is a worldwide view (many stations from different countries)
  const isWorldwideView = stations.length > 50 || 
    new Set(stations.map(s => s.country).filter(Boolean)).size > 10;

  // For worldwide view, show all stations without radius limitation
  const isWithinRadius = (coords) => {
    if (isWorldwideView) return true; // Show all stations in worldwide view
    
    const userLatLng = L.latLng(position[0], position[1]);
    const stationLatLng = L.latLng(coords.latitude, coords.longitude);
    return userLatLng.distanceTo(stationLatLng) <= searchRadius;
  };

  // Determine zoom level based on view type
  const getZoomLevel = () => {
    if (isWorldwideView) return 2; // World view
    return 10; // Local view
  };

  return (
    <MapContainer 
      center={position} 
      zoom={getZoomLevel()} 
      style={{ height: "100%", width: "100%" }} 
      className="map-container"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {/* Eigene Position - only show in local view */}
      {!isWorldwideView && (
        <>
          <Marker position={position} icon={userIcon}>
            <Popup>Hier ist deine Position</Popup>
          </Marker>

          {/* Suchkreis - only show in local view */}
          <Circle
            center={position}
            radius={searchRadius}
            pathOptions={{ color: 'blue', fillColor: '#blue', fillOpacity: 0.1 }}
          />
        </>
      )}

      {/* Stationen */}
      {stations.map((station, index) => {
        const coords = station.coordinates;
        if (!coords || !isWithinRadius(coords)) return null;

        const pm25Value = getLatestValue(station, 'pm25');
        const pm10Value = getLatestValue(station, 'pm10');

        return (
          <Marker
            key={index}
            position={[coords.latitude, coords.longitude]}
            icon={stationIcon}
          >
            <Popup>
              <div style={{ minWidth: 220, maxWidth: 320, padding: 8, borderRadius: 10, background: '#fff', boxShadow: '0 2px 12px rgba(66,133,244,0.10)' }}>
                <div style={{ fontWeight: 700, fontSize: 18, color: '#2c3e50', marginBottom: 6 }}>{station.station || "Unbekannte Station"}</div>
                {station.distance && (
                  <div style={{ display: 'inline-block', background: '#e8f5e8', color: '#27ae60', borderRadius: 6, fontSize: 13, padding: '2px 8px', marginBottom: 8, marginRight: 4 }}>
                    <span style={{ fontSize: 15 }}>📍</span> {(station.distance / 1000).toFixed(1)} km entfernt
                  </div>
                )}
                <div style={{ margin: '10px 0 8px 0', display: 'flex', flexDirection: 'column', gap: 4 }}>
                  {pm25Value && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 15 }}>
                      <span style={{ color: '#888', fontWeight: 500 }}>PM2.5:</span>
                      <span style={{ color: getAQIColor(pm25Value, 'pm25'), background: '#e8f5e8', borderRadius: 4, padding: '2px 7px', fontWeight: 700 }}>{pm25Value} µg/m³</span>
                    </div>
                  )}
                  {pm10Value && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 15 }}>
                      <span style={{ color: '#888', fontWeight: 500 }}>PM10:</span>
                      <span style={{ color: getAQIColor(pm10Value, 'pm10'), background: '#e6f0fa', borderRadius: 4, padding: '2px 7px', fontWeight: 700 }}>{pm10Value} µg/m³</span>
                    </div>
                  )}
                  {(!pm25Value && !pm10Value) && (
                    <div style={{ color: '#b2bec3', fontSize: 13 }}>Keine aktuellen Messwerte</div>
                  )}
                </div>
                <a 
                  href={`/station/${encodeURIComponent(station.station)}`}
                  style={{ display: 'inline-block', marginTop: 10, padding: '9px 18px', background: '#4285f4', color: '#fff', borderRadius: 7, fontWeight: 600, fontSize: 15, textDecoration: 'none', boxShadow: '0 2px 8px rgba(66,133,244,0.10)' }}
                >
                  📊 Details anzeigen
                </a>
              </div>
            </Popup>
          </Marker>
        );
      })}
    </MapContainer>
  );
}

export default MapView;
