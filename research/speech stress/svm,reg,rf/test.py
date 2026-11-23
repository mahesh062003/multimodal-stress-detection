import joblib
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download necessary NLTK resources
nltk.download("stopwords")
nltk.download("punkt")

# Load the saved model and vectorizer
model = joblib.load("results/bestmodel_Support Vector Machine.pkl")
vectorizer = joblib.load("results/tfidf_vectorizer.pkl")

# Define stress level mapping
label_mapping = {0: "Low", 1: "Neutral", 2: "High"}

# Text preprocessing function
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = text.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    tokens = word_tokenize(text)  # Tokenization
    tokens = [word for word in tokens if word not in stopwords.words("english")]  # Remove stopwords
    return " ".join(tokens)

# Live Testing Loop
while True:
    user_input = input("\nEnter a sentence (or type 'exit' to quit): ")
    
    if user_input.lower() == "exit":
        print("Exiting...")
        break

    # Preprocess and transform input text
    processed_text = preprocess_text(user_input)
    text_features = vectorizer.transform([processed_text])

    # Predict stress level
    prediction = model.predict(text_features)[0]
    stress_level = label_mapping[prediction]

    print(f"Predicted Stress Level: {stress_level}")
