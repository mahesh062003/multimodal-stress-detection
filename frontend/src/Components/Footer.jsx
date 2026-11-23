import React from "react";
import "./footer.css";

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="app-footer">
      <div className="footer-content">
        <p>&copy; {currentYear} StressAware. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default Footer;
