import React, { useState, useEffect } from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import './ResultsPage.css';

function ResultsPage({ sessionId, setCurrentComponent }) {
  const [sessionData, setSessionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showPersonalization, setShowPersonalization] = useState(false);
  const [audio, setAudio] = useState(null);

  useEffect(() => {
    const fetchSessionData = async () => {
      try {
        const response = await fetch(`http://localhost:5000/get-session-status?session_id=${sessionId}`);
        
        if (!response.ok) {
          throw new Error(`Error fetching session data: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        }

        setSessionData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSessionData();
  }, [sessionId]);

  const getStressIcon = (level) => {
    if (!level) return "❓";
    if (level.toLowerCase().includes("high")) return "🔴";
    if (level.toLowerCase().includes("neutral")) return "🟡";
    return "🟢";
  };

  const getStressClass = (level) => {
    if (!level) return "text-muted";
    if (level.toLowerCase().includes("high")) return "text-danger fw-bold";
    if (level.toLowerCase().includes("neutral")) return "text-warning fw-bold";
    return "text-success fw-bold";
  };

  const playMusic = () => {
    let audioFile = "";

    if (sessionData?.combined_stress?.toLowerCase().includes("neutral")) {
      audioFile = "src/Components/audio/sample.mp3";  
    } else if (sessionData?.combined_stress?.toLowerCase().includes("high")) {
      audioFile = "src/Components/audio/sample-3.mp3";  
    }

    if (audioFile) {
      const newAudio = new Audio(audioFile);
      newAudio.play().catch((err) => console.error("Error playing audio:", err));
      setAudio(newAudio);
    }
  };

  const stopMusic = () => {
    if (audio) {
      audio.pause();
      setAudio(null);
    }
  };

  const handlePersonalization = () => {
    if (!sessionData || !sessionData.combined_stress) {
      alert("Stress level data not available yet. Please complete all assessments.");
      return;
    }

    setShowPersonalization(true);

    if (sessionData.combined_stress.toLowerCase().includes("neutral") || 
        sessionData.combined_stress.toLowerCase().includes("high")) {
      playMusic();
    }
  };

  return (
    <div className="container results-page text-center mt-4">
      <h2 className="text-success fw-bold">Your Stress Analysis Results</h2>

      {loading && <div className="alert alert-info">Loading your results...</div>}

      {error && (
        <div className="alert alert-danger">
          <p>{error}</p>
          <button className="btn btn-primary" onClick={() => setCurrentComponent("home")}>Back to Home</button>
        </div>
      )}

      {sessionData && (
        <div className="mt-4">
          <div className="p-3 mb-4 border rounded bg-dark text-light">
            <h3 className="text-light">Combined Stress Level</h3>
            <div className={getStressClass(sessionData.combined_stress)}>
              {getStressIcon(sessionData.combined_stress)} {sessionData.combined_stress || "Not enough data"}
            </div>
          </div>

          <div className="row justify-content-center">
            {["face", "voice", "watch"].map((method) => (
              <div key={method} className="col-md-4 mb-3">
                <div className="p-3 border rounded bg-dark text-light">
                  <h4>{method.charAt(0).toUpperCase() + method.slice(1)} Analysis</h4>
                  <div className="fw-bold">
                    {sessionData[`${method}_stress`] ? (
                      <>
                        <span>{getStressIcon(sessionData[`${method}_stress`])} </span>
                        <span className={getStressClass(sessionData[`${method}_stress`])}>
                          {sessionData[`${method}_stress`]}
                        </span>
                      </>
                    ) : (
                      <span className="text-muted">Not measured</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {!sessionData.completed && (
            <div className="mt-4 p-3 border rounded bg-warning text-dark">
              <h3>Complete Your Assessment</h3>
              <p>For the most accurate results, complete all three analysis methods:</p>
              <div className="d-flex justify-content-center gap-2">
                <button className="btn btn-dark" onClick={() => setCurrentComponent("face")}>Face Test</button>
                <button className="btn btn-dark" onClick={() => setCurrentComponent("voice")}>Voice Test</button>
                <button className="btn btn-dark" onClick={() => setCurrentComponent("watch")}>Watch Test</button>
              </div>
            </div>
          )}

          {!showPersonalization && (
            <button className="btn btn-success mt-4" onClick={handlePersonalization}>
              Get Recommendations
            </button>
          )}

          {showPersonalization && sessionData?.combined_stress && (
            <div className="mt-4 p-3 border rounded bg-secondary">
              <h3>Personalized Recommendations</h3>

              {sessionData.combined_stress.toLowerCase().includes("high") ? (
                <ul className="list-unstyled">
                  <li>🧘 Take short breaks</li>
                  <li>🌬️ Try deep breathing exercises</li>
                  <li>🎶 Listen to calming music</li>
                  <li>🧠 Practice mindfulness meditation</li>
                </ul>
              ) : sessionData.combined_stress.toLowerCase().includes("neutral") ? (
                <ul className="list-unstyled">
                  <li>🚶 Continue relaxing activities</li>
                  <li>🧍 Stretch or go for a walk</li>
                  <li>🎵 Listen to soft background music</li>
                </ul>
              ) : (
                <ul className="list-unstyled">
                  <li>😃 Enjoy your day with a light, refreshing tune</li>
                  <li>🏖️ Engage in fun, enjoyable activities</li>
                </ul>
              )}

              {(sessionData.combined_stress.toLowerCase().includes("neutral") || 
                sessionData.combined_stress.toLowerCase().includes("high")) && (
                <>
                  {audio ? (
                    <button className="btn btn-danger mt-3" onClick={stopMusic}>
                      Stop Music
                    </button>
                  ) : (
                    <button className="btn btn-primary mt-3" onClick={playMusic}>
                      Play Calming Music
                    </button>
                  )}
                </>
              )}

              {audio && <p className="text-light mt-2">Take a deep breath...</p>}
            </div>
          )}
        </div>
      )}

      <div className="mt-4">
        <button className="btn btn-outline-light" onClick={() => setCurrentComponent("home")}>
          Back to Home
        </button>
      </div>
    </div>
  );
}

export default ResultsPage;