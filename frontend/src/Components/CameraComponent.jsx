import  { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";

const videoConstraints = {
  width: 640,
  height: 480,
  facingMode: "user",
};

const CameraComponent = ({ onVideoRecorded }) => {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [recording, setRecording] = useState(false);
  const [error, setError] = useState(null);

  // Check if webcam is available on mount
  useEffect(() => {
    const checkWebcam = async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === "videoinput");
        if (videoDevices.length === 0) {
          throw new Error("No video input devices found");
        }
        console.log("Available video devices:", videoDevices);
      } catch (err) {
        console.error("Error checking webcam availability:", err);
        setError("Webcam not detected: " + err.message);
      }
    };
    checkWebcam();
  }, []);

  // Start recording and activate camera
  const startRecording = async () => {
    if (!webcamRef.current) {
      console.error("Webcam ref not set");
      setError("Webcam reference not initialized");
      return;
    }

    try {
      setCameraActive(true);
      setRecording(true);
      setError(null);
      console.log("Attempting to start recording...");

      const stream = await navigator.mediaDevices.getUserMedia({
        video: videoConstraints,
        audio: false,
      });
      webcamRef.current.video.srcObject = stream;

      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: "video/webm" });
      const recordedChunks = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.push(event.data);
          console.log("Data chunk received:", event.data.size, "bytes");
        }
      };

      mediaRecorderRef.current.onstop = () => {
        console.log("Recording stopped");
        const blob = new Blob(recordedChunks, { type: "video/webm" });
        setRecording(false);
        setCameraActive(false);
        stream.getTracks().forEach((track) => track.stop());
        if (recordedChunks.length > 0) {
          console.log("Video blob created, size:", blob.size, "bytes");
          onVideoRecorded(blob);
        } else {
          console.error("No video data recorded");
          setError("No video data recorded");
        }
      };

      mediaRecorderRef.current.onerror = (event) => {
        console.error("MediaRecorder error:", event.error);
        setError("Recording error: " + event.error.message);
        setRecording(false);
        setCameraActive(false);
      };

      mediaRecorderRef.current.start();
      console.log("MediaRecorder started");

      // Stop after 10 seconds
      setTimeout(() => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
          mediaRecorderRef.current.stop();
          console.log("Recording stopped after 10 seconds");
        } else {
          console.log("MediaRecorder already inactive");
        }
      }, 10000);
    } catch (err) {
      console.error("Error accessing webcam:", err);
      setError("Failed to access webcam: " + err.message);
      setCameraActive(false);
      setRecording(false);
    }
  };

  return (
    <div style={{ textAlign: "center" }}>
      <Webcam
        audio={false}
        ref={webcamRef}
        videoConstraints={videoConstraints}
        style={{
          marginBottom: "10px",
          display: cameraActive ? "block" : "none", // Hide until active
        }}
        onUserMediaError={(err) => {
          console.error("Webcam permission denied or error:", err);
          setError("Webcam error: " + err.message);
          setCameraActive(false);
          setRecording(false);
        }}
      />
      {!recording && (
        <button
          onClick={startRecording}
          style={{ padding: "10px 20px", fontSize: "16px" }}
        >
          Record Now
        </button>
      )}
      {recording && <p style={{ color: "blue" }}>Recording... (10 seconds)</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
};

export default CameraComponent;