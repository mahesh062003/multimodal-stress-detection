# AI-Based Multimodal Stress Detection & Physiological Tracking

Stress inferred from three independent signals — **facial expression**,
**speech**, and **wearable physiology** — then fused into a single assessment.
Each modality is a separately trained model behind a Flask API, with a React
client that captures webcam, microphone and Google Fit data in one session.

Single-signal stress detection is fragile: a face is only visible while the user
looks at the camera, speech requires the user to talk, and heart-rate data lags
the moment it describes. Fusing the three means an assessment is still produced
when any one of them is missing.

📄 Published in IJIRT (International Journal of Innovative Research in
Technology), paper **177475**.

---

## Results

| Modality | Model | Test accuracy | Status |
|---|---|---|---|
| Facial | **CNN** | **87.6%** | deployed |
| Facial | Vision Transformer | 75.1% | not deployed — 97.8% train |
| Speech | BERT | 98.0% | not deployed |
| Speech | **SVM + TF-IDF** | **95.8%** | deployed |
| Wearable | **XGBoost** | **92.75%** | deployed |

**The Vision Transformer lost to the smaller CNN.** It reached 97.8% on train
but 75.1% on a 7,178-sample test set — a 23-point generalisation gap. The
dataset was not large enough to train a ViT from scratch without heavy
overfitting, so the CNN was deployed. The ViT work is kept in `research/`.

**Macro-averaged figures are the honest read on the speech models.** BERT
reports 98% weighted but 0.91 macro-F1, and the SVM 96% weighted against 0.85
macro — the class distribution is skewed, so the minority stress class is
recalled less reliably than the headline suggests.

The SVM rather than BERT is deployed: a 1.1 MB TF-IDF and SVM pair at ~96% was
the better trade against a transformer for two points of weighted accuracy, on
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
modalities that returned a result, so a session with no microphone still yields
an assessment from face and wearable alone. It returns `None` only when every
modality failed, never guessing from nothing.

**Sessions persist.** Each run gets a session id, and face, voice and watch
results are written to SQLite as they arrive, so the three captures need not
happen simultaneously.

Client-side, `@tensorflow-models/blazeface` confirms a face is framed before any
video is uploaded, so the server never receives frames with no face in them.

---

## Layout

```
backend/           Flask API (5 routes)
  fmodels/           Haar cascades for face detection
frontend/          React + Vite client (webcam, recorder, results)
research/          Training notebooks and evaluation output per modality
  Facial stress/     CNN and Vision Transformer
  speech stress/     BERT and SVM/LogReg/RandomForest
  smartwatch/        XGBoost vs RF vs SVM, Google Fit ingestion
docs/figures/      Confusion matrix, training curves, workflow diagram
```

---

## Usage

```bash
# Backend
cd backend
pip install -r requirements.txt
python app.py            # :5000

# Frontend
cd frontend
npm install
npm run dev
```

### Google Fit access

The wearable modality needs your own OAuth credentials. In Google Cloud Console
enable the Fitness API, create an OAuth client ID of type *Desktop app*,
download the JSON as `backend/credentials.json`, then run the backend once to
complete the consent flow. The refresh token caches to `token.pickle`
(gitignored).

Scopes: `fitness.heart_rate.read`, `fitness.sleep.read`.

The face and speech modalities need no Google setup.

### Not included

The trained weights are not distributed — the notebooks in `research/` train
each model from scratch, and name their dataset sources. Also excluded: Google
credentials and cached tokens, and the SQLite store of heart-rate and sleep
records.

---

## Stack

Python · Flask · TensorFlow/Keras · PyTorch · scikit-learn · XGBoost ·
OpenAI Whisper · OpenCV · NLTK · SQLite · React · Vite · TensorFlow.js ·
Google Fit API
