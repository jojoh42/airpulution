import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import StationPage from './pages/StationPage.jsx';
import World from "./pages/world.jsx";

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/station/:name" element={<StationPage />} />
      <Route path="/world" element={<World />} />
    </Routes>
  );
}
