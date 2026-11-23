import { useState, useEffect } from 'react';
import './App.css';
import Header from './Components/Header';
import HomePage from './Components/HomeComponent';
import FaceStressDetection from './Components/FaceStressDetection';
import VoiceStressDetection from './Components/VoiceStressDetection';
import AnalyzeSmartWatchData from './Components/SmartWatchDataAnalyser';
import Footer from './Components/Footer';
import ResultsPage from './Components/ResultsPage';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';



function App() {
  const [currentComponent, setCurrentComponent] = useState("home");
  const [sessionId, setSessionId] = useState(null);
  const [combinedResult, setCombinedResult] = useState(null);

  // Initialize or get a session ID when the app starts
  useEffect(() => {
    // Generate a simple session ID if needed
    if (!sessionId) {
      const newSessionId = new Date().getTime().toString();
      setSessionId(newSessionId);
      console.log("Created new session ID:", newSessionId);
    }
  }, [sessionId]);

  // Handle setting the combined result
  const handleResultUpdate = (result) => {
    if (result && result.combined_stress) {
      setCombinedResult(result.combined_stress);
    }
  };

  // Navigate to results page
  const goToResults = () => {
    setCurrentComponent("results");
  };

  return (
    <>
      <div className="app-container">
        <Header setCurrentComponent={setCurrentComponent} />

        <main className="main-content">
          {currentComponent === "home" && (
            <HomePage setCurrentComponent={setCurrentComponent} />
          )}
          {currentComponent === "face" && (
            <FaceStressDetection 
              sessionId={sessionId}
              onResultUpdate={handleResultUpdate} 
              goToResults={goToResults}
            />
          )}
          {currentComponent === "voice" && (
            <VoiceStressDetection 
              sessionId={sessionId}
              onResultUpdate={handleResultUpdate}
              goToResults={goToResults}
            />
          )}
          {currentComponent === "watch" && (
            <AnalyzeSmartWatchData 
              sessionId={sessionId}
              onResultUpdate={handleResultUpdate}
              goToResults={goToResults}
            />
          )}
          {currentComponent === "results" && (
            <ResultsPage 
              sessionId={sessionId}
              combinedResult={combinedResult}
              setCurrentComponent={setCurrentComponent}
            />
          )}
        </main>

        <Footer />
      </div>
    </>
  );
}

export default App;