import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./router.jsx";
import Navbar from './Navbar.jsx';

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <AppRoutes />
    </BrowserRouter>
  );
}


export default App;
