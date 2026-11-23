# AI-Based Multimodal Stress Detection & Physiological Tracking

Stress inferred from three independent signals — **facial expression**, **speech**,
and **wearable physiology** — then fused into a single assessment. Each modality
is a separately trained model behind a Flask API, with a React client that
captures webcam, microphone and Google Fit data in one session.

Single-signal stress detection is fragile: a face is only visible while the user
looks at the camera, speech requires the user to talk, and heart-rate data lags
the moment it describes. Fusing the three means the system still produces an
assessment when any one of them is missing.

📄 Published in IJIRT — [`docs/IJIRT177475-...pdf`](docs/IJIRT177475-facial-and-speech-emotion-detection.pdf)

---

## Results

| Modality | Model | Test accuracy | Notes |
|---|---|---|---|
| Facial | **CNN** | **87.6%** | Deployed. 87.6% validation at epoch 18 |
| Facial | Vision Transformer | 75.1% | 97.8% train — **overfit**, not deployed |
| Speech | BERT | 98.0% | Best score, but macro-F1 0.91 vs weighted 0.98 |
| Speech | **SVM + TF-IDF** | **95.8%** | Deployed — far cheaper at inference |
| Wearable | **XGBoost** | **92.75%** | Deployed. Beat Random Forest and SVM |

Two findings worth stating plainly rather than burying:

**The Vision Transformer lost to the much smaller CNN.** It reached 97.8% on
train but only 75.1% on a 7,178-sample test set — a 23-point generalisation gap.
The dataset was not large enough to train a ViT from scratch without heavy
overfitting, so the CNN was deployed instead. The ViT work is kept in
`research/Facial stress/VisionTransformers/` because the negative result is the
useful part.

**The speech models' headline accuracy flatters them.** BERT reports 98%
weighted but 0.91 macro-F1, and the SVM 96% weighted against 0.85 macro — the
class distribution is skewed, so the minority stress class is recalled less
reliably than the top-line number suggests. Macro-averaged figures are the
honest ones to read.

The SVM rather than BERT is deployed: a 1.1 MB TF-IDF + SVM pair at ~96% was
the better trade against a transformer for two points of weighted accuracy on
a machine also running Whisper and a CNN.

---

## How it works

```
                   ┌─────────────────────────────────────────┐
  webcam  ─────────►  /analyze/face                          │
                   │    Haar cascade → crop → CNN            │
                   ├─────────────────────────────────────────┤
  microphone ──────►  /analyze_voice_stress                  │
                   │    Whisper → NLTK → TF-IDF → SVM        │
                   ├─────────────────────────────────────────┤
  Google Fit ──────►  /fetch-data                            │
                   │    heart rate + sleep → scaler → XGBoost│
                   └──────────────────┬──────────────────────┘
                                      ▼
                              /predict-stress
                        majority vote over available
                         modalities → High / Low
```

**Fusion degrades gracefully.** `calculate_combined_stress` votes only over the
modalities that actually returned a result, so a session with no microphone
still yields an assessment from face and wearable alone. It returns `None` only
when every modality failed — it never guesses from nothing.

**Sessions are persistent.** Each run gets a session id, and face, voice and
watch results are written to SQLite as they arrive, so the three captures need
not happen simultaneously.

Client-side, `@tensorflow-models/blazeface` runs in the browser to confirm a
face is framed before any video is uploaded — the server never receives frames
with no face in them.

---

## Layout

```
backend/           Flask API (app.py, 5 routes) + the three deployed models
  fmodels/           facial CNN + Haar cascades
  smodels/           speech SVM + TF-IDF vectoriser
  wmodels/           wearable XGBoost + scaler + label encoder
frontend/          React + Vite client (webcam, recorder, results)
research/          Training notebooks and evaluation output per modality
  Facial stress/     CNN and Vision Transformer
  speech stress/     BERT and SVM/LogReg/RandomForest
  smartwatch/        XGBoost vs RF vs SVM, Google Fit ingestion
docs/              Published paper, project report, result figures
```

---

## Running it

```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py            # serves on :5000

# Frontend
cd frontend
npm install
npm run dev
```

### Google Fit access

The wearable modality needs **your own** OAuth credentials — mine are not in
this repository and should not be. In Google Cloud Console enable the Fitness
API, create an OAuth client ID of type *Desktop app*, download the JSON as
`backend/credentials.json`, then run the backend once to complete the consent
flow. The refresh token is cached to `token.pickle` (gitignored).

Scopes used: `fitness.heart_rate.read`, `fitness.sleep.read`.

The face and speech modalities work with no Google setup at all.

### What is not in this repository

- `credentials.json`, `service_account.json`, `token.pickle` — live Google
  credentials and an active refresh token
- `updated.db` — real heart-rate, sleep and stress-session records
- Training datasets — see the notebooks in `research/` for sources

---

## Publication

**"Facial and Speech Emotion Detection"** — IJIRT, paper 177475.
A further paper was prepared for COMNET 2025.

This was a **team project**, co-authored with Arul, Dharaneesh and Jansi Rani.
Work was collaborative across the modalities rather than split into separate
ownership. Only my own IJIRT certificate is included in `docs/` — the others
are not mine to publish.

---

## Stack

Python · Flask · TensorFlow/Keras · PyTorch (ViT) · scikit-learn · XGBoost ·
OpenAI Whisper · OpenCV · NLTK · SQLite · React · Vite · TensorFlow.js ·
Google Fit API
