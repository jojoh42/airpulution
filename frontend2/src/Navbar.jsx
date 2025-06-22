import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="navbar navbar-expand-lg navbar-light bg-light shadow-sm">
      <div className="container">
        <Link className="navbar-brand fw-bold" to="/">🌍 Luftdaten</Link>
        <div className="collapse navbar-collapse">
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <Link className="nav-link" to="/direct">Direkte Luftqualität</Link>
            </li>
            <li className="nav-item">
              <Link className="nav-link" to="/about">Über</Link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

  );
}
export default Navbar;
