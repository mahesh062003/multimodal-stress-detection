import torch
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datasets import Dataset
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, Trainer
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load saved model and tokenizer
model_path = "./trained_model"
tokenizer = DistilBertTokenizer.from_pretrained(model_path)
model = DistilBertForSequenceClassification.from_pretrained(model_path).to(device)

# Load and prepare dataset
df = pd.read_csv("data/train.csv")  # Adjust path as needed

# Map emotions to stress categories
emotion_to_stress = {
    0: "High", 1: "Low", 2: "Low", 3: "High", 4: "High", 5: "Neutral"
}
df["label"] = df["label"].map(emotion_to_stress)

# Encode labels
label_to_int = {"Low": 0, "Neutral": 1, "High": 2}
int_to_label = {v: k for k, v in label_to_int.items()}

# Split into test set
_, temp_texts, _, temp_labels = train_test_split(df["text"], df["label"], test_size=0.2, stratify=df["label"], random_state=42)
_, test_texts, _, test_labels = train_test_split(temp_texts, temp_labels, test_size=0.5, stratify=temp_labels, random_state=42)
test_labels_encoded = test_labels.map(label_to_int)

# Tokenize
encodings = tokenizer(list(test_texts), padding="max_length", truncation=True, return_tensors="pt")
test_dataset = Dataset.from_dict({
    "input_ids": encodings["input_ids"],
    "attention_mask": encodings["attention_mask"],
    "labels": list(test_labels_encoded)
})

# Evaluate model
trainer = Trainer(model=model, tokenizer=tokenizer)
preds = trainer.predict(test_dataset)

# Convert predictions
y_pred = np.argmax(preds.predictions, axis=1)
y_true = np.array(test_labels_encoded)

# Map to label names
y_true_labels = [int_to_label[i] for i in y_true]
y_pred_labels = [int_to_label[i] for i in y_pred]

# Confusion matrix
cm = confusion_matrix(y_true_labels, y_pred_labels, labels=["Low", "Neutral", "High"])
cm_df = pd.DataFrame(cm, index=["Low", "Neutral", "High"], columns=["Low", "Neutral", "High"])
print("\n📋 Confusion Matrix (Tabular):\n", cm_df)

# Classification report
print("\n📈 Classification Report:\n", classification_report(y_true_labels, y_pred_labels))

# Confusion matrix with percentages
cm_percent = cm / cm.sum(axis=1, keepdims=True)
annot = np.empty_like(cm).astype(str)
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        count = cm[i, j]
        percent = cm_percent[i, j] * 100
        annot[i, j] = f"{count}\n({percent:.1f}%)" if count != 0 else "0\n(0.0%)"

# Plot heatmap
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=annot, fmt="", cmap="Blues", cbar=True,
            xticklabels=["Low", "Neutral", "High"],
            yticklabels=["Low", "Neutral", "High"])
plt.title("Confusion Matrix Heatmap")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")
plt.tight_layout()
plt.show()
