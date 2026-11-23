import whisper
import sounddevice as sd
import numpy as np
import wave
import joblib
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download necessary NLTK resources
nltk.download("stopwords", quiet=True)
nltk.download("punkt", quiet=True)

print("✅ Necessary libraries loaded.")

# Load Whisper model for speech recognition
print("🔄 Loading Whisper model...")
whisper_model = whisper.load_model("base")
print("✅ Whisper model loaded.")

# Load saved ML model and TF-IDF vectorizer
print("🔄 Loading ML model and vectorizer...")
try:
    ml_model = joblib.load("results/bestmodel_Support Vector Machine.pkl")
    vectorizer = joblib.load("results/tfidf_vectorizer.pkl")
    print("✅ ML model and vectorizer loaded.")
except FileNotFoundError:
    print("❌ Error: ML model or vectorizer files not found. Please ensure 'results/bestmodel_Support Vector Machine.pkl' and 'results/tfidf_vectorizer.pkl' exist.")
    exit()

# Define stress level mapping
label_mapping = {0: "Low", 1: "Neutral", 2: "High"}

# Function to record audio
def record_audio(filename, duration=5, samplerate=44100):
    """Records audio from the microphone and saves it as a WAV file."""
    print(f"🎙️ Recording {duration} seconds of audio... Speak now!")
    try:
        audio_data = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype=np.int16)
        sd.wait()

        # Save recorded audio
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit PCM
            wf.setframerate(samplerate)
            wf.writeframes(audio_data.tobytes())

        print(f"✅ Recording saved as '{filename}'")
    except Exception as e:
        print(f"❌ Error during recording: {e}")
        return False
    return True

# Function to transcribe audio
def transcribe_audio(filename):
    """Transcribes audio using Whisper."""
    print(f"🔍 Transcribing '{filename}'...")
    try:
        result = whisper_model.transcribe(filename)
        transcription = result["text"]
        print("\n🎤 Transcription Output:", transcription)
        return transcription
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        return None

def preprocess_text(text):
    """Cleans and tokenizes text for ML model."""
    print("🔄 Preprocessing text...")
    text = text.lower()  # Convert to lowercase
    text = text.translate(str.maketrans("", "", string.punctuation))  # Remove punctuation
    tokens = word_tokenize(text)  # Tokenization
    custom_stop_words = ["the", "a", "an", "is", "am", "are", "was", "were"] #example list.
    tokens = [word for word in tokens if word not in custom_stop_words]
    cleaned_text = " ".join(tokens)
    print("✅ Preprocessed text:", cleaned_text)
    return cleaned_text

# Function to predict stress level
def predict_stress(text):
    """Uses the trained model to predict stress level from text."""
    try:
        processed_text = preprocess_text(text)
        text_features = vectorizer.transform([processed_text])
        prediction = ml_model.predict(text_features)[0]
        stress_level = label_mapping[prediction]
        print(f"\n🔮 Predicted Stress Level: {stress_level}")
    except Exception as e:
        print(f"❌ Error during prediction: {e}")
# Main script
if __name__ == "__main__":
    print("\n📌 Choose an option:\n1️⃣ Transcribe from a saved file\n2️⃣ Record and transcribe in real-time")
    choice = input("Enter 1 or 2: ")
    print(f"🔹 User selected: {choice}")

    if choice == "1":
        file_path = input("📂 Enter the path of the audio file: ")
        transcribed_text = transcribe_audio(file_path)
        if transcribed_text:
            predict_stress(transcribed_text)

    elif choice == "2":
        temp_file = "temp_recording.wav"
        if record_audio(temp_file, duration=5):  # Default 5 seconds
            transcribed_text = transcribe_audio(temp_file)
            if transcribed_text:
                predict_stress(transcribed_text)

    else:
        print("❌ Invalid choice. Please enter 1 or 2.")