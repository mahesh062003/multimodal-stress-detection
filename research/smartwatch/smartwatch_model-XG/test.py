import numpy as np
import joblib
import ast

# 🔹 Load the trained model (Change based on the model you want to use)
model_filename = "XGBoost_0.9275.pkl"  # Change as needed
model = joblib.load(model_filename)

# 🔹 Load the label encoder
label_encoder = joblib.load("label_encoder.pkl")

# 🔹 Load the scaler
scaler = joblib.load("scaler.pkl")

# 🔹 Function to predict stress level
def predict_stress(sleep_duration, last_6_hours_hr, avg_hr, min_hr, max_hr, hr_std_dev):
    if isinstance(last_6_hours_hr, str):
        last_6_hours_hr = ast.literal_eval(last_6_hours_hr)  # Convert string list to actual list

    # 🔹 Ensure exactly 24 HR values are provided
    if len(last_6_hours_hr) != 24:
        raise ValueError(f"Expected 24 HR values, but got {len(last_6_hours_hr)}")

    # 🔹 Construct full feature set (Sleep Duration + 24 HR values + Other Features)
    input_data = np.array([sleep_duration] + last_6_hours_hr + [avg_hr, min_hr, max_hr, hr_std_dev]).reshape(1, -1)

    # 🔹 Debugging: Print feature count to verify shape
    print(f"🔍 Input Shape: {input_data.shape}, Expected: (1, 29)")

    # 🔹 Normalize input using the saved scaler
    input_scaled = scaler.transform(input_data)

    # 🔹 Make prediction
    prediction = model.predict(input_scaled)[0]

    # 🔹 Decode prediction (0 → Low, 1 → Neutral, 2 → High)
    predicted_class = label_encoder.inverse_transform([prediction])[0]
    
    return predicted_class

# 🔹 Example Test Data (Make sure exactly 24 HR values are given)
sleep_duration = 240  # 7 hours (in minutes)
last_6_hours_hr = [90, 98, 91, 92, 94, 89, 88, 83, 78, 87, 85, 86, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99]  # 24 HR values
avg_hr = 90
min_hr = 78
max_hr = 99
hr_std_dev = 5.4  # Example values

# 🔹 Predict Stress Level
predicted_stress = predict_stress(sleep_duration, last_6_hours_hr, avg_hr, min_hr, max_hr, hr_std_dev)
print(f"✅ Predicted Stress Level: {predicted_stress}")
