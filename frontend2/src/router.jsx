import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import StationPage from './pages/StationPage.jsx';

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/station/:name" element={<StationPage />} />
    </Routes>
  );
}
