from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import os
import re
import math

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "model")
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(
    __name__,
    template_folder=TEMPLATE_DIR,
    static_folder=STATIC_DIR
)
CORS(app)

MODEL_PATH = os.path.join(MODEL_DIR, "logistic_regression_model.joblib")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.joblib")

model = None
vectorizer = None

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"<.*?>", " ", text)
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def load_artifacts():
    global model, vectorizer
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}. "
            "Copy your trained .joblib model into the model/ folder."
        )
    if not os.path.exists(VECTORIZER_PATH):
        raise FileNotFoundError(
            f"Vectorizer not found: {VECTORIZER_PATH}. "
            "Copy your trained TF-IDF vectorizer into the model/ folder."
        )

    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)

def prediction_confidence(features):
    prediction = int(model.predict(features)[0])

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)[0]
        fake_probability = float(probabilities[1])
    elif hasattr(model, "decision_function"):
        score = float(model.decision_function(features)[0])
        fake_probability = 1.0 / (1.0 + math.exp(-max(min(score, 35), -35)))
    else:
        fake_probability = float(prediction)

    if 0.45 <= fake_probability <= 0.55:
        label = "MEDIUM / UNCERTAIN"
        prediction_class = "medium"
    elif fake_probability > 0.55:
        label = "FAKE / SUSPICIOUS"
        prediction_class = "fake"
    else:
        label = "GENUINE"
        prediction_class = "genuine"

    confidence = max(fake_probability, 1.0 - fake_probability)

    return {
    "prediction": label,
    "class": prediction_class,
    "fake_probability": round(fake_probability * 100, 2),
    "genuine_probability": round((1 - fake_probability) * 100, 2),
    "confidence": round(confidence * 100, 2)
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None
    })

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(silent=True) or {}
        review = str(data.get("review", "")).strip()

        if not review:
            return jsonify({"error": "Please enter a review."}), 400

        if len(review) > 10000:
            return jsonify({"error": "Review is too long. Maximum 10,000 characters."}), 400

        cleaned = clean_text(review)
        features = vectorizer.transform([cleaned])
        result = prediction_confidence(features)

        result["review_length"] = len(review)
        result["word_count"] = len(review.split())

        return jsonify(result)

    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

try:
    load_artifacts()
    print("Model and TF-IDF vectorizer loaded successfully.")
except Exception as exc:
    print(f"WARNING: {exc}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
