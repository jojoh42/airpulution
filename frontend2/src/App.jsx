import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./router.jsx";

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;
