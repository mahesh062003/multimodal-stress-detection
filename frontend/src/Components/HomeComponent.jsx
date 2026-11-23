import React from "react";
import "./HomeComponent.css";

function HomePage({ setCurrentComponent }) {
  return (
    <div className="home-container">
      <div className="welcome-section">
        <h2>StressAware</h2>
        <p>Your comprehensive stress detection and analysis tool</p>

        <div className="description">
          <p>StressAware uses multiple methods to detect and analyze your stress levels:</p>
          <p>Our advanced AI models combine these sources to provide accurate insights.</p>
        </div>
      </div>

      <div className="detection-options">
        {[
          { name: "Face", text: "Analyze facial expressions to detect stress indicators", component: "face" },
          { name: "Voice", text: "Analyze voice patterns to identify stress markers", component: "voice" },
          { name: "Watch", text: "Use heart rate and sleep data to evaluate stress levels", component: "watch" },
        ].map((option) => (
          <div key={option.name} className="option-card" onClick={() => setCurrentComponent(option.component)}>
            <h3>{option.name} Stress Detection</h3>
            <p>{option.text}</p>
            <button className="start-btn">Start {option.name} Analysis</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HomePage;
