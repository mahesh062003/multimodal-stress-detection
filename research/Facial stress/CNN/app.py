from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import time
import threading
import queue

app = Flask(__name__)

# Load the trained model
model = load_model("fer_stress_model.h5")

# Load label classes
label_classes = np.load("fer_label_classes.npy", allow_pickle=True)

# Load face cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Global variables for stress level tracking
latest_stress = {
    "level": "Waiting for detection",
    "confidence": 0,
    "timestamp": time.time()
}

# Queue for thread-safe communication
stress_queue = queue.Queue(maxsize=10)

# Recommendations for each stress level
recommendations = {
    "High Stress": [
        "Take deep breaths (4-7-8 technique)",
        "Step away from your current task for 5 minutes",
        "Practice progressive muscle relaxation",
        "Listen to calming music",
        "Limit caffeine intake"
    ],
    "Neutral": [
        "Maintain regular breaks during work",
        "Stay hydrated throughout the day",
        "Practice mindfulness for 5 minutes",
        "Stretch your body occasionally",
        "Maintain good posture"
    ],
    "Low Stress": [
        "Great job managing stress!",
        "Continue your current positive activities",
        "Share positive experiences with others",
        "Set goals for the rest of your day",
        "Consider journaling your positive state"
    ]
}

def preprocess_face(face_img):
    # Resize to 48x48 and convert to grayscale if needed
    face_img = cv2.resize(face_img, (48, 48))
    if len(face_img.shape) == 3 and face_img.shape[2] == 3:
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    # Normalize pixel values
    face_img = face_img / 255.0
    # Reshape for model input
    face_img = face_img.reshape(1, 48, 48, 1)
    return face_img

def get_emotion_stress(face_img):
    # Preprocess face image
    processed_img = preprocess_face(face_img)
    # Make prediction
    prediction = model.predict(processed_img, verbose=0)
    # Get predicted class index
    predicted_class_index = np.argmax(prediction)
    # Get class label
    predicted_class = label_classes[predicted_class_index]
    # Calculate confidence score
    confidence = float(prediction[0][predicted_class_index] * 100)
    
    # Define color based on stress level
    if predicted_class == "High Stress":
        color = (0, 0, 255)  # Red in BGR
    elif predicted_class == "Low Stress":
        color = (0, 255, 0)  # Green in BGR
    else:  # Neutral
        color = (0, 255, 255)  # Yellow in BGR
        
    return predicted_class, confidence, color

def update_latest_stress(stress_level, confidence):
    global latest_stress
    latest_stress = {
        "level": stress_level,
        "confidence": confidence,
        "timestamp": time.time()
    }
    # Add to queue for thread safety
    try:
        stress_queue.put_nowait({
            "level": stress_level,
            "confidence": confidence,
            "timestamp": time.time()
        })
    except queue.Full:
        # Queue is full, remove oldest item
        try:
            stress_queue.get_nowait()
            stress_queue.put_nowait({
                "level": stress_level,
                "confidence": confidence,
                "timestamp": time.time()
            })
        except Exception:
            pass

def generate_frames():
    camera = cv2.VideoCapture(0)  # Try with 0 for default webcam
    
    # If default camera doesn't work, try other indices
    if not camera.isOpened():
        for i in range(10):  # Try camera indices 0-9
            camera = cv2.VideoCapture(i)
            if camera.isOpened():
                break
    
    # Check if camera opened successfully
    if not camera.isOpened():
        print("Error: Could not open webcam")
        # Return a placeholder frame with error message
        while True:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "ERROR: Cannot access webcam", (50, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    # Set camera properties for better quality
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    face_detection_interval = 0  # Process every frame initially
    
    # If camera opened successfully
    while True:
        # Read camera frame
        success, frame = camera.read()
        if not success:
            print("Failed to read frame")
            continue
        
        face_detection_interval += 1
        
        # Process every 3rd frame for better performance
        if face_detection_interval >= 3:
            face_detection_interval = 0
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
            
            # Process each face
            for (x, y, w, h) in faces:
                # Extract face region
                face_img = gray[y:y+h, x:x+w]
                
                try:
                    # Get emotion and stress prediction
                    predicted_class, confidence, color = get_emotion_stress(face_img)
                    
                    # Update global stress level
                    update_latest_stress(predicted_class, confidence)
                    
                    # Draw rectangle around face
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    
                    # Add text with prediction
                    label = f"{predicted_class} ({confidence:.1f}%)"
                    
                    # Background for text
                    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                    cv2.rectangle(frame, (x, y - text_size[1] - 10), (x + text_size[0], y), color, -1)
                    
                    # Add text
                    cv2.putText(frame, label, (x, y-5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
                        
                except Exception as e:
                    print(f"Error processing face: {e}")
        
        # Add timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, frame.shape[0] - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Convert frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # Yield the frame for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stress_level')
def stress_level():
    # Get latest stress data from queue if available
    stress_data = None
    try:
        while not stress_queue.empty():
            stress_data = stress_queue.get_nowait()
    except Exception:
        stress_data = latest_stress
    
    if not stress_data:
        stress_data = latest_stress
    
    # Add recommendations to the response
    if stress_data["level"] in recommendations:
        stress_data["recommendations"] = recommendations[stress_data["level"]]
    else:
        stress_data["recommendations"] = ["Face detection in progress. Please look at the camera."]
    
    return jsonify(stress_data)

if __name__ == '__main__':
    print("Starting StressScope application...")
    print("Model loaded successfully. Access the app at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)