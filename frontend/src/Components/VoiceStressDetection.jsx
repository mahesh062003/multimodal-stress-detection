import React, { useState, useRef } from 'react';
import './VoiceStressDetection.css';

function VoiceStressDetection({ sessionId, onResultUpdate, goToResults }) {
  const [recording, setRecording] = useState(false);
  const [audioURL, setAudioURL] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  const startRecording = async () => {
    try {
      chunksRef.current = [];
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        const audioUrl = URL.createObjectURL(audioBlob);
        setAudioURL(audioUrl);
        submitAudio(audioBlob);

        // Stop all tracks
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setRecording(true);
      
      setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          stopRecording();
        }
      }, 15000);
    } catch (err) {
      setError("Error accessing microphone: " + err.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const submitAudio = async (blob) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('audio', blob);
      formData.append('session_id', sessionId);

      const response = await fetch('http://localhost:5000/analyze_voice_stress', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
      onResultUpdate(data);
      setLoading(false);
    } catch (err) {
      setError("Error analyzing audio: " + err.message);
      setLoading(false);
    }
  };

  const resetDetection = () => {
    setResult(null);
    setAudioURL(null);
    setError(null);
  };

  return (
    <div className="voice-detection-container">
      <h2>Voice Stress Detection</h2>
      
      <div className="detection-area">
        <div className="audio-container">
          {recording && (
            <div className="recording-indicator">
              <div className="recording-animation"></div>
              <p>Recording your voice...</p>
            </div>
          )}
          
          {audioURL && (
            <div className="audio-player">
              <audio src={audioURL} controls />
            </div>
          )}
        </div>

        <div className="controls">
          {!recording && !result && !loading && (
            <button 
              className="record-btn" 
              onClick={startRecording}
              disabled={loading}
            >
              Start Recording
            </button>
          )}
          
          {recording && (
            <button 
              className="stop-btn" 
              onClick={stopRecording}
            >
              Stop Recording
            </button>
          )}
          
          {loading && <div className="loading">Analyzing voice patterns...</div>}
          
          {error && (
            <div className="error-message">
              <p>{error}</p>
              <button onClick={resetDetection}>Try Again</button>
            </div>
          )}
          
          {result && (
            <div className="result-summary">
              <div className="button-group">
                <button onClick={resetDetection}>Try Again</button>
                <button onClick={goToResults}>View All Results</button>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <div className="instructions">
        <h3>How it works</h3>
        <p>Our AI will analyze your voice patterns to detect signs of stress.</p>
        <ol>
          <li>Click "Start Recording" to begin</li>
          <li>Please speak naturally about your day or how you're feeling</li>
          <li>The recording will automatically end after 15 seconds</li>
          <li>Results will be displayed once the analysis is complete</li>
        </ol>
        <p className="note">Note: Your voice data is processed locally and not stored permanently.</p>
      </div>
    </div>
  );
}

export default VoiceStressDetection;
