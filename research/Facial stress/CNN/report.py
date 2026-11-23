import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from tensorflow.keras.models import load_model
from sklearn.preprocessing import LabelEncoder

# Load test data
test_csv_path = "test.csv"
emotion_map = {
    0: "High Stress",
    1: "Low Stress",
    2: "High Stress",
    3: "Low Stress",
    4: "High Stress",
    5: "Low Stress",
    6: "Neutral"
}

def load_data(csv_path):
    data = pd.read_csv(csv_path)
    data["emotion"] = data["emotion"].map(emotion_map)
    X = np.array([np.fromstring(image, sep=' ') for image in data["pixels"]])
    X = X / 255.0  # Normalize pixel values
    X = X.reshape(-1, 48, 48, 1)  # Reshape for CNN input
    y = np.array(data["emotion"])
    return X, y

X_test, y_test = load_data(test_csv_path)

# Load the label encoder
encoder = LabelEncoder()
encoder.classes_ = np.load("fer_label_classes.npy", allow_pickle=True)
y_test = encoder.transform(y_test)

# Load the trained model
model = load_model("fer_stress_model.h5")

# Make predictions
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1)  # Convert to class labels

# Generate confusion matrix
conf_matrix = confusion_matrix(y_test, y_pred_classes)

# Print confusion matrix as a text table
print("\nConfusion Matrix:")
print(conf_matrix)

# Plot confusion matrix
plt.figure(figsize=(6, 5))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=encoder.classes_, yticklabels=encoder.classes_)
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.title("Confusion Matrix")
plt.show()

# Generate classification report
report = classification_report(y_test, y_pred_classes, target_names=encoder.classes_)
print("\nClassification Report:\n", report)
