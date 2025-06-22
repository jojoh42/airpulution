import { Link } from "react-router-dom";
import "./About.css";

export default function About() {
  return (
    <div className="about-page">
      <div className="header-section">
        <div className="header-content">
          <h1>🌍 Über AirQuality Monitor</h1>
          <p className="subtitle">
            Eine moderne App zur Überwachung der Luftqualität weltweit
          </p>
        </div>
        
        <div className="controls-section">
          <Link to="/" className="btn btn-primary">
            🏠 Zurück zur Hauptseite
          </Link>
        </div>
      </div>

      <div className="content-section">
        <div className="about-card">
          <h2>📊 Was ist AirQuality Monitor?</h2>
          <p>
            AirQuality Monitor ist eine moderne Webanwendung, die Echtzeit-Daten zur Luftqualität 
            aus der ganzen Welt sammelt und präsentiert. Die App nutzt Daten von OpenAQ, 
            einer globalen Plattform für Luftqualitätsdaten, um Nutzern aktuelle Informationen 
            über PM2.5 und PM10 Werte zu liefern.
          </p>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🌍</div>
            <h3>Weltweite Abdeckung</h3>
            <p>
              Zugriff auf Luftqualitätsdaten aus über 100 Ländern mit tausenden von Messstationen.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Echtzeit-Daten</h3>
            <p>
              Aktuelle Messwerte mit automatischen Updates alle 30 Minuten für optimale Genauigkeit.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🗺️</div>
            <h3>Interaktive Karten</h3>
            <p>
              Moderne Kartenansicht mit detaillierten Stationen und Messwerten weltweit.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">📱</div>
            <h3>Responsive Design</h3>
            <p>
              Optimiert für alle Geräte - Desktop, Tablet und Smartphone.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">💾</div>
            <h3>Intelligentes Caching</h3>
            <p>
              MySQL-basiertes Caching für blitzschnelle Ladezeiten und reduzierte API-Aufrufe.
            </p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🔄</div>
            <h3>Background Updates</h3>
            <p>
              Automatische Datenaktualisierung im Hintergrund für immer frische Informationen.
            </p>
          </div>
        </div>

        <div className="about-card">
          <h2>🔬 Technische Details</h2>
          <div className="tech-stack">
            <div className="tech-section">
              <h3>Frontend</h3>
              <ul>
                <li><strong>React 18</strong> - Moderne UI-Bibliothek</li>
                <li><strong>Vite</strong> - Schneller Build-Tool</li>
                <li><strong>React Router</strong> - Navigation</li>
                <li><strong>Chart.js</strong> - Interaktive Diagramme</li>
                <li><strong>Leaflet</strong> - Interaktive Karten</li>
                <li><strong>Axios</strong> - HTTP-Client</li>
              </ul>
            </div>

            <div className="tech-section">
              <h3>Backend</h3>
              <ul>
                <li><strong>FastAPI</strong> - Moderne Python API</li>
                <li><strong>MySQL</strong> - Datenbank für Caching</li>
                <li><strong>SQLAlchemy</strong> - ORM</li>
                <li><strong>Uvicorn</strong> - ASGI Server</li>
                <li><strong>Schedule</strong> - Background Tasks</li>
                <li><strong>Requests</strong> - HTTP-Client</li>
              </ul>
            </div>

            <div className="tech-section">
              <h3>APIs & Services</h3>
              <ul>
                <li><strong>OpenAQ API</strong> - Luftqualitätsdaten</li>
                <li><strong>IPinfo.io</strong> - Standortbestimmung</li>
                <li><strong>OpenStreetMap</strong> - Karten</li>
                <li><strong>MySQL Server</strong> - Datenpersistierung</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="about-card">
          <h2>📈 Luftqualitätskategorien</h2>
          <div className="aqi-categories">
            <div className="aqi-category good">
              <div className="aqi-color"></div>
              <div className="aqi-info">
                <h4>Gut (0-12 µg/m³ PM2.5)</h4>
                <p>Luftqualität ist zufriedenstellend und Luftverschmutzung stellt wenig oder kein Risiko dar.</p>
              </div>
            </div>

            <div className="aqi-category moderate">
              <div className="aqi-color"></div>
              <div className="aqi-info">
                <h4>Mäßig (12.1-35.4 µg/m³ PM2.5)</h4>
                <p>Luftqualität ist akzeptabel; bei einigen Schadstoffen können moderate Gesundheitsbedenken bestehen.</p>
              </div>
            </div>

            <div className="aqi-category unhealthy-sensitive">
              <div className="aqi-color"></div>
              <div className="aqi-info">
                <h4>Ungesund für empfindliche Gruppen (35.5-55.4 µg/m³ PM2.5)</h4>
                <p>Empfindliche Personengruppen können gesundheitliche Auswirkungen verspüren.</p>
              </div>
            </div>

            <div className="aqi-category unhealthy">
              <div className="aqi-color"></div>
              <div className="aqi-info">
                <h4>Ungesund (55.5-150.4 µg/m³ PM2.5)</h4>
                <p>Jeder kann gesundheitliche Auswirkungen verspüren; empfindliche Gruppen können schwerwiegendere Auswirkungen haben.</p>
              </div>
            </div>

            <div className="aqi-category very-unhealthy">
              <div className="aqi-color"></div>
              <div className="aqi-info">
                <h4>Sehr ungesund (150.5-250.4 µg/m³ PM2.5)</h4>
                <p>Gesundheitswarnung: Jeder kann schwerwiegendere gesundheitliche Auswirkungen verspüren.</p>
              </div>
            </div>

            <div className="aqi-category hazardous">
              <div className="aqi-color"></div>
              <div className="aqi-info">
                <h4>Gefährlich (250.5+ µg/m³ PM2.5)</h4>
                <p>Gesundheitswarnung: Notfallbedingungen. Die gesamte Bevölkerung ist wahrscheinlich betroffen.</p>
              </div>
            </div>
          </div>
        </div>

        <div className="about-card">
          <h2>🚀 Features im Detail</h2>
          <div className="features-detail">
            <div className="feature-detail">
              <h3>🏠 Hauptseite</h3>
              <p>
                Zeigt Luftqualitätsdaten für deinen aktuellen Standort mit interaktiver Karte, 
                aktuellen Messwerten und Background-Updater-Status.
              </p>
            </div>

            <div className="feature-detail">
              <h3>🌍 Weltweite Übersicht</h3>
              <p>
                Karten- und Listenansicht aller verfügbaren Stationen weltweit mit 
                erweiterten Filtern und Suchfunktionen.
              </p>
            </div>

            <div className="feature-detail">
              <h3>🏭 Stationsdetails</h3>
              <p>
                Detaillierte Informationen zu einzelnen Stationen mit historischen Daten, 
                Trends und interaktiven Charts.
              </p>
            </div>

            <div className="feature-detail">
              <h3>📡 Direkte API</h3>
              <p>
                Schnelle Datenabfrage mit MySQL-Caching für optimale Performance 
                und reduzierte Ladezeiten.
              </p>
            </div>

            <div className="feature-detail">
              <h3>🔄 Background Updates</h3>
              <p>
                Automatische Datenaktualisierung im Hintergrund: beliebte Städte alle 30 Minuten, 
                alle Daten alle 2 Stunden, vollständige Aktualisierung täglich um 6:00 Uhr.
              </p>
            </div>

            <div className="feature-detail">
              <h3>💾 Cache-Management</h3>
              <p>
                Intelligentes MySQL-Caching mit 1-Stunden-Dauer, Statistiken und 
                historischen Daten für Analyse.
              </p>
            </div>
          </div>
        </div>

        <div className="about-card">
          <h2>📊 Datenquellen</h2>
          <p>
            <strong>OpenAQ:</strong> Die App nutzt die OpenAQ API, eine globale Plattform, 
            die Luftqualitätsdaten aus der ganzen Welt sammelt und bereitstellt. 
            OpenAQ aggregiert Daten von tausenden von Messstationen und macht sie 
            über eine einheitliche API verfügbar.
          </p>
          <p>
            <strong>Datenqualität:</strong> Alle Daten werden von offiziellen Messstationen 
            bereitgestellt und regelmäßig validiert. Die App zeigt sowohl PM2.5 als auch 
            PM10 Werte an, die wichtigsten Indikatoren für Luftqualität.
          </p>
        </div>

        <div className="about-card">
          <h2>🔮 Zukünftige Features</h2>
          <div className="future-features">
            <div className="future-feature">
              <h4>📈 Prognose-Funktion</h4>
              <p>KI-basierte Vorhersage der Luftqualität für die kommenden Tage</p>
            </div>
            <div className="future-feature">
              <h4>🔔 Benachrichtigungen</h4>
              <p>Push-Benachrichtigungen bei schlechter Luftqualität</p>
            </div>
            <div className="future-feature">
              <h4>📱 Mobile App</h4>
              <p>Native iOS und Android Apps für bessere Nutzererfahrung</p>
            </div>
            <div className="future-feature">
              <h4>📊 Erweiterte Analysen</h4>
              <p>Detaillierte Statistiken und Trendanalysen</p>
            </div>
          </div>
        </div>

        <div className="about-card">
          <h2>📞 Kontakt & Support</h2>
          <p>
            Bei Fragen, Problemen oder Anregungen kannst du gerne Kontakt aufnehmen. 
            Die App wird kontinuierlich weiterentwickelt und verbessert.
          </p>
          <div className="contact-info">
            <p><strong>Version:</strong> 1.0.0</p>
            <p><strong>Letzte Aktualisierung:</strong> {new Date().toLocaleDateString('de-DE')}</p>
            <p><strong>Status:</strong> 🟢 Online und funktionsfähig</p>
          </div>
        </div>
      </div>
    </div>
  );
} 