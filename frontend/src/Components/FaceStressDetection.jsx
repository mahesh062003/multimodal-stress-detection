import React, { useRef, useState } from "react";
import Webcam from "react-webcam";
import "./FaceStressDetection.css";

const videoConstraints = {
  width: 320,
  height: 240,
  facingMode: "user",
};

function FaceStressDetection({ sessionId, onResultUpdate, goToResults }) {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [recording, setRecording] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [resultAvailable, setResultAvailable] = useState(false);

  const startRecording = async () => {
    setError(null);
    try {
      setCameraActive(true);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: videoConstraints,
        audio: false,
      });

      if (webcamRef.current) {
        webcamRef.current.video.srcObject = stream;
      }

      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: "video/webm" });
      const recordedChunks = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(recordedChunks, { type: "video/webm" });
        stopCamera();
        setRecording(false);
        submitVideo(blob);
      };

      mediaRecorderRef.current.start();
      setRecording(true);

      setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
          mediaRecorderRef.current.stop();
        }
      }, 10000);
    } catch (err) {
      setError("Error accessing webcam: " + err.message);
      setCameraActive(false);
      setRecording(false);
    }
  };

  const stopCamera = () => {
    if (webcamRef.current && webcamRef.current.video.srcObject) {
      const tracks = webcamRef.current.video.srcObject.getTracks();
      tracks.forEach((track) => track.stop());
      webcamRef.current.video.srcObject = null;
    }
    setCameraActive(false);
  };

  const submitVideo = async (blob) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("video", blob);
      formData.append("session_id", sessionId);

      const response = await fetch("http://localhost:5000/analyze/face", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      setResultAvailable(true);
      onResultUpdate();
    } catch (err) {
      setError("Error analyzing video: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetDetection = () => {
    setResultAvailable(false);
    setError(null);
    stopCamera();
  };

  return (
    <div className="face-detection-container">
      <h2>Facial Stress Detection</h2>

      <div className="detection-area">
        {cameraActive && (
          <div className="video-container">
            <Webcam
              audio={false}
              ref={webcamRef}
              videoConstraints={videoConstraints}
              className={recording ? "recording" : ""}
            />
          </div>
        )}

        <div className="controls">
          {!recording && !resultAvailable && !loading && (
            <button className="record-btn" onClick={startRecording}>
              Start Recording
            </button>
          )}

          {recording && (
            <button className="stop-btn" onClick={() => mediaRecorderRef.current?.stop()}>
              Stop Recording
            </button>
          )}

          {loading && <div className="loading">Analyzing facial expressions...</div>}

          {error && (
            <div className="error-message">
              <p>{error}</p>
              <button onClick={resetDetection}>Try Again</button>
            </div>
          )}

          {resultAvailable && (
            <div className="button-group">
              <button onClick={resetDetection} className="try-again-btn">
                Try Again
              </button>
              <button onClick={goToResults} className="view-results-btn">
                View All Results
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="instructions">
        <h3>How it works</h3>
        <p>Our AI will analyze your facial expressions to detect signs of stress.</p>
        <ol>
          <li>Click "Start Recording" to begin</li>
          <li>Ensure your face is clearly visible in the camera</li>
          <li>The recording will automatically end after 10 seconds</li>
          <li>Results will be available shortly after processing</li>
        </ol>
        <p className="note">Note: Your video data is processed locally and not stored permanently.</p>
      </div>
    </div>
  );
}

export default FaceStressDetection;
