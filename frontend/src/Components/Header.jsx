import React, { useState } from "react";
import "./header.css";

function Header({ setCurrentComponent }) {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="app-header">
      <div className="header-content">
        <div className="logo" onClick={() => setCurrentComponent("home")}>
          <h1>StressAware</h1>
        </div>

        {/* Mobile Menu Toggle */}
        <button 
          className={`menu-toggle ${menuOpen ? "active" : ""}`} 
          onClick={() => setMenuOpen(!menuOpen)}
        >
          ☰
        </button>
      </div>

      <nav className={`main-nav ${menuOpen ? "open" : ""}`}>
        <ul>
          <li onClick={() => { setCurrentComponent("home"); setMenuOpen(false); }}>Home</li>
          <li onClick={() => { setCurrentComponent("face"); setMenuOpen(false); }}>Face Analysis</li>
          <li onClick={() => { setCurrentComponent("voice"); setMenuOpen(false); }}>Voice Analysis</li>
          <li onClick={() => { setCurrentComponent("watch"); setMenuOpen(false); }}>Smartwatch Data</li>
          <li onClick={() => { setCurrentComponent("results"); setMenuOpen(false); }}>Results</li>
        </ul>
      </nav>
    </header>
  );
}

export default Header;
