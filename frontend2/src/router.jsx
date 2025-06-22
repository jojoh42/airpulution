import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import StationPage from './pages/StationPage.jsx';
import DirectAirQuality from "./pages/DirectAirQuality.jsx";
import About from "./pages/About.jsx";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/station/:name" element={<StationPage />} />
      <Route path="/direct" element={<DirectAirQuality />} />
      <Route path="/about" element={<About />} />
    </Routes>
  );
}
