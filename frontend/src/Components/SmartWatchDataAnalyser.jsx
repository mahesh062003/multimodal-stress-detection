import React, { useState } from "react";
import "bootstrap/dist/css/bootstrap.min.css"; // Bootstrap added
import { Button, Alert, Container } from "react-bootstrap"; // Bootstrap Components
import "./smartwatchstyle.css"; // Your custom styles

function AnalyzeSmartWatchData({ sessionId, onResultUpdate, goToResults }) {
  const [dataFetched, setDataFetched] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [resultAvailable, setResultAvailable] = useState(false);
  const [error, setError] = useState(null);
  const [authorizationNeeded, setAuthorizationNeeded] = useState(false);

  const fetchData = async () => {
    setError(null);
    try {
      const response = await fetch(`http://localhost:5000/fetch-data?session_id=${sessionId}`);

      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          setAuthorizationNeeded(true);
          throw new Error("Authorization needed for Google Fit access");
        }
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      setDataFetched(true);
    } catch (err) {
      setError("Error fetching data: " + err.message);
    }
  };

  const analyzeData = async () => {
    setAnalyzing(true);
    try {
      const response = await fetch(`http://localhost:5000/predict-stress?session_id=${sessionId}`);

      if (!response.ok) throw new Error(`Server error: ${response.status}`);

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      setResultAvailable(true);
      onResultUpdate();
    } catch (err) {
      setError("Error analyzing data: " + err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAuthorize = () => {
    window.open("http://localhost:5000/authorize-google-fit", "_blank");
    setAuthorizationNeeded(false);
  };

  const resetAnalysis = () => {
    setDataFetched(false);
    setResultAvailable(false);
    setError(null);
  };

  return (
    <Container className="smartwatch-container">
      <h2>Smartwatch Data Analysis</h2>

      <div className="analysis-area">
        {!dataFetched && !resultAvailable && !analyzing && (
          <div className="data-fetch-info">
            <p>We'll need access to your Google Fit data to analyze your health patterns.</p>
            {authorizationNeeded ? (
              <div className="auth-needed">
                <p>Authorization is needed to access your Google Fit data.</p>
                <Button onClick={handleAuthorize} className="custom-btn">
                  Authorize Google Fit
                </Button>
              </div>
            ) : (
              <Button className="custom-btn fetch-btn" onClick={fetchData}>
                Fetch Smartwatch Data
              </Button>
            )}
          </div>
        )}

        {dataFetched && !resultAvailable && !analyzing && (
          <div className="data-ready">
            <p>Your health data has been successfully fetched!</p>
            <Button className="custom-btn analyze-btn" onClick={analyzeData}>
              Analyze Stress Levels
            </Button>
          </div>
        )}

        {analyzing && <div className="loading">Analyzing your health data...</div>}

        {error && (
          <div className="error-container">
            <Alert variant="danger" className="error-message">
              <p>{error}</p>
              <Button onClick={resetAnalysis} className="custom-btn">
                Try Again
              </Button>
            </Alert>
          </div>
        )}

        {resultAvailable && (
          <div className="button-group">
            <Button onClick={resetAnalysis} className="custom-btn try-again-btn">
              Analyze Again
            </Button>
            <Button onClick={goToResults} className="custom-btn view-results-btn">
              View All Results
            </Button>
          </div>
        )}
      </div>

      <div className="instructions">
      <h3>How it works</h3>
        <p>We analyze your heart rate and sleep data to detect stress patterns.</p>
        <ol>
          <li>Click "Fetch Smartwatch Data" to retrieve health data</li>
          <li>Ensure your Google Fit account has heart rate & sleep data</li>
          <li>Click "Analyze Stress Levels" to start AI-based analysis</li>
          <li>Once completed, you can view the results</li>
        </ol>
        <p className="note">Note: Your data is processed securely and not stored permanently.</p>
      </div>
    </Container>
  );
}

export default AnalyzeSmartWatchData;