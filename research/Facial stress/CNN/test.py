import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder
import time
import os
from collections import Counter

# Load trained model
model = load_model("fer_stress_model.h5")

# Load label encoder classes
label_encoder = LabelEncoder()
label_encoder.classes_ = np.load("fer_label_classes.npy", allow_pickle=True)

# Display model parameters
total_params = model.count_params()
print(f"Model Loaded - Total Parameters: {total_params}")

# Load Haar cascades for face and facial features
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
mouth_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

# Function to preprocess a face for the model
def preprocess_face(face_img):
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    face_img = cv2.resize(face_img, (48, 48))  # Resize to match model input
    face_img = face_img / 255.0  # Normalize
    face_img = face_img.reshape(1, 48, 48, 1)  # Reshape for CNN
    return face_img

# Open webcam
cap = cv2.VideoCapture(0)

# Define output path and create the directory if it does not exist
output_dir = "output_video"
os.makedirs(output_dir, exist_ok=True)  # Ensure the directory exists
output_path = os.path.join(output_dir, "output.avi")

# Video writer setup
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
video_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"XVID"), 10, (frame_width, frame_height))

# Store detected emotions over 10 seconds
emotion_list = []
start_time = time.time()
record_duration = 10  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        face = frame[y:y+h, x:x+w]  # Extract face ROI
        processed_face = preprocess_face(face)

        # Predict emotion
        prediction = model.predict(processed_face)
        predicted_label = np.argmax(prediction)
        emotion = label_encoder.inverse_transform([predicted_label])[0]
        
        # Store detected emotion
        emotion_list.append(emotion)

        # Set color based on emotion
        color = (0, 255, 0) if emotion == "Low Stress" else (0, 0, 255) if emotion == "High Stress" else (255, 255, 0)
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, f"Emotion: {emotion}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Detect eyes inside the detected face
        face_gray = gray_frame[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(face_gray, scaleFactor=1.1, minNeighbors=10)
        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (255, 0, 0), 2)
            cv2.putText(frame, "Eye", (x+ex, y+ey-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

        # Detect mouth inside the detected face
        mouths = mouth_cascade.detectMultiScale(face_gray, scaleFactor=1.3, minNeighbors=20)
        for (mx, my, mw, mh) in mouths:
            if my > h / 2:  # Ensure it's in the lower half of the face
                cv2.rectangle(frame, (x+mx, y+my), (x+mx+mw, y+my+mh), (0, 255, 255), 2)
                cv2.putText(frame, "Mouth", (x+mx, y+my-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    # Display model parameters on screen
    cv2.putText(frame, f"Model Params: {total_params}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Write frame to video file
    video_writer.write(frame)
    
    cv2.imshow("Live Stress Detection", frame)

    # Stop recording after 10 seconds
    if time.time() - start_time > record_duration:
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
video_writer.release()
cv2.destroyAllWindows()

# Find the most frequent emotion in 10 seconds
if emotion_list:
    most_common_emotion = Counter(emotion_list).most_common(1)[0][0]
    print(f"Most Frequent Emotion in 10 sec: {most_common_emotion}")
    print(f"Video saved at: {output_path}")
