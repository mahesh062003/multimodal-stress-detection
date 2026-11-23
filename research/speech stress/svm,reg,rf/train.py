import pandas as pd
import numpy as np
import nltk
import string
import seaborn as sns
import matplotlib.pyplot as plt
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure required NLTK resources are available
nltk.download("stopwords")
nltk.download("punkt")

# Load datasets
train_df = pd.read_csv("data/train.csv")
test_df = pd.read_csv("data/test.csv")
val_df = pd.read_csv("data/validation.csv")

# Combine train and validation for better training
train_df = pd.concat([train_df, val_df])

# Mapping emotions to stress levels
stress_mapping = {
    0: "High",    # Sadness → High Stress
    1: "Low",     # Joy → Low Stress
    2: "Low",     # Love → Low Stress
    3: "High",    # Anger → High Stress
    4: "High",    # Fear → High Stress
    5: "Neutral"  # Surprise → Neutral Stress
}

# Apply mapping to datasets
train_df["stress_level"] = train_df["label"].map(stress_mapping)
test_df["stress_level"] = test_df["label"].map(stress_mapping)

# Text preprocessing function
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = text.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    tokens = word_tokenize(text)  # Tokenization
    tokens = [word for word in tokens if word not in stopwords.words("english")]  # Remove stopwords
    return " ".join(tokens)

# Apply preprocessing
train_df["text"] = train_df["text"].apply(preprocess_text)
test_df["text"] = test_df["text"].apply(preprocess_text)

# Convert text to TF-IDF features
vectorizer = TfidfVectorizer(max_features=5000)
X_train = vectorizer.fit_transform(train_df["text"])
X_test = vectorizer.transform(test_df["text"])

# Encode stress levels as numerical values
label_mapping = {"Low": 0, "Neutral": 1, "High": 2}
y_train = train_df["stress_level"].map(label_mapping)
y_test = test_df["stress_level"].map(label_mapping)

# Define models
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "Support Vector Machine": SVC(kernel="linear"),
    "Random Forest": RandomForestClassifier(n_estimators=100)
}

# Track the best model
best_model = None
best_accuracy = 0
best_model_name = ""

# Train and evaluate each model
for name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    train_accuracy = model.score(X_train, y_train)
    test_accuracy = accuracy_score(y_test, y_pred)

    print(f"\n{name} Results:")
    print(f"Training Accuracy: {train_accuracy:.4f}")
    print(f"Test Accuracy: {test_accuracy:.4f}")
    print("Classification Report:\n", classification_report(y_test, y_pred, target_names=["Low", "Neutral", "High"]))

    # Save classification report
    with open(f"results/{name}_report.txt", "w") as f:
        f.write(f"{name} Classification Report:\n")
        f.write(classification_report(y_test, y_pred, target_names=["Low", "Neutral", "High"]))

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Low", "Neutral", "High"], yticklabels=["Low", "Neutral", "High"])
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.title(f"Confusion Matrix - {name}")
    plt.savefig(f"results/{name}_confusion_matrix.png")  # Save confusion matrix image
    plt.close()

    # Save the best model
    if test_accuracy > best_accuracy:
        best_accuracy = test_accuracy
        best_model = model
        best_model_name = name

# Save the best model
if best_model:
    joblib.dump(best_model, f"results/bestmodel_{best_model_name}.pkl")
    print(f"\nBest Model: {best_model_name} (Accuracy: {best_accuracy:.4f})")

# Save the TF-IDF vectorizer
joblib.dump(vectorizer, "results/tfidf_vectorizer.pkl")
