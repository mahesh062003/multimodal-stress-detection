import pandas as pd
import numpy as np
import ast
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, classification_report

# 🔹 Load dataset
df = pd.read_csv("perfectly_balanced_dataset.csv")

# 🔹 Convert 'Last 6 Hours HR Data' from string to list safely
def safe_convert(x):
    try:
        return ast.literal_eval(x) if isinstance(x, str) else x
    except:
        return np.nan  # Assign NaN if conversion fails

df['Last 6 Hours HR Data'] = df['Last 6 Hours HR Data'].apply(safe_convert)

# 🔹 Drop rows where HR data is still NaN
df = df.dropna(subset=['Last 6 Hours HR Data'])

# 🔹 Expand HR Data into separate columns
hr_features = pd.DataFrame(df['Last 6 Hours HR Data'].tolist(), index=df.index)
hr_features.columns = [f"HR_{i+1}" for i in range(hr_features.shape[1])]

# 🔹 Drop original column and merge new HR columns
df = df.drop(columns=['Last 6 Hours HR Data']).join(hr_features)

# 🔹 Encode target labels ('Low', 'Neutral', 'High') into numeric values
label_encoder = LabelEncoder()
df['Stress Class'] = label_encoder.fit_transform(df['Stress Class'])  # 0=Low, 1=Neutral, 2=High

# 🔹 Define features (X) and target (y)
X = df.drop(columns=['Stress Class'])
y = df['Stress Class']

# 🔹 Handle missing values (replace NaNs with column median)
X.fillna(X.median(), inplace=True)

# 🔹 Split data (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 🔹 Normalize features using StandardScaler
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# 🔹 Save the Scaler (so it can be used in prediction)
joblib.dump(scaler, "scaler.pkl")

# 🔹 Train and evaluate models
models = {
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42),
    "SVM": SVC(kernel='rbf', probability=True, random_state=42)
}

for name, model in models.items():
    # Train the model
    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    model_filename = f"{name}_{accuracy:.4f}.pkl"
    
    # Save the trained model
    joblib.dump(model, model_filename)
    print(f"{name} Model Accuracy: {accuracy:.4f} - Saved as {model_filename}")
    
    # 🔹 Predict on the test set
    y_pred = model.predict(X_test)
    
    # 🔹 Generate Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    
    # 🔹 Plot and save Confusion Matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
    plt.title(f"Confusion Matrix for {name} Model")
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    cm_filename = f"{name}_confusion_matrix.png"
    plt.savefig(cm_filename)
    plt.close()

    # 🔹 Generate and save Classification Report
    cr = classification_report(y_test, y_pred, target_names=label_encoder.classes_)
    
    plt.figure(figsize=(10, 6))
    plt.text(0.1, 0.5, cr, {'fontsize': 12}, fontproperties='monospace')
    plt.axis('off')
    cr_filename = f"{name}_classification_report.png"
    plt.savefig(cr_filename)
    plt.close()

    print(f"Confusion Matrix and Classification Report for {name} model saved as images.")

# 🔹 Save Label Encoder (for later decoding)
with open("label_encoder.pkl", "wb") as f:
    joblib.dump(label_encoder, f)

print("\n✅ Training Completed Successfully! All models, confusion matrices, and classification reports saved.")
