"""
Prediction module for spam detection.
Loads the trained model and vectorizer, preprocesses input, and returns predictions.
"""

import os
import joblib
from src.preprocessing import preprocess_text

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "spam_classifier.joblib")
VECTORIZER_PATH = os.path.join(PROJECT_ROOT, "models", "tfidf_vectorizer.joblib")

# ─── Load Model (lazy singleton) ─────────────────────────────────────────────
_model = None
_vectorizer = None


def _load_model():
    """Load model and vectorizer from disk (cached after first call)."""
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {MODEL_PATH}. "
                "Run `python -m src.model` first to train the model."
            )
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VECTORIZER_PATH)
    return _model, _vectorizer


def predict(text: str) -> dict:
    """
    Predict whether a comment is spam or not.
    
    Args:
        text: Raw comment text
        
    Returns:
        dict with keys:
            - label: "Spam" or "Not Spam"
            - confidence: float between 0.0 and 1.0
            - cleaned_text: preprocessed version of input
    """
    model, vectorizer = _load_model()
    
    # Preprocess
    cleaned = preprocess_text(text)
    
    # Vectorize
    features = vectorizer.transform([cleaned])
    
    # Predict
    prediction = model.predict(features)[0]
    
    # Get probability (confidence)
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(features)[0]
        confidence = proba[1] if prediction == 1 else proba[0]
        spam_probability = proba[1]
    else:
        # Fallback for models without predict_proba
        confidence = 0.95 if prediction == 1 else 0.95
        spam_probability = float(prediction)
    
    return {
        "label": "Spam" if prediction == 1 else "Not Spam",
        "confidence": round(float(confidence), 4),
        "spam_probability": round(float(spam_probability), 4),
        "cleaned_text": cleaned,
    }


def predict_batch(texts: list) -> list:
    """
    Predict spam/not-spam for a list of comments.
    
    Args:
        texts: List of raw comment strings
        
    Returns:
        List of prediction dicts
    """
    return [predict(text) for text in texts]


if __name__ == "__main__":
    # Quick test
    test_comments = [
        "Check out this free iPhone giveaway http://scam.com",
        "Great video, very informative and well made!",
        "SUBSCRIBE TO MY CHANNEL FOR FREE GIFTS!!!",
        "I learned so much from this tutorial, thank you!",
        "Win $1000 now at http://bit.ly/freeee 💰💰💰",
        "The editing on this video is amazing",
    ]
    
    print("🔍 Spam Detection Predictions")
    print("=" * 60)
    for comment in test_comments:
        result = predict(comment)
        emoji = "🚫" if result["label"] == "Spam" else "✅"
        print(f"\n{emoji} [{result['label']}] (confidence: {result['confidence']:.1%})")
        print(f"   Input  : {comment}")
        print(f"   Cleaned: {result['cleaned_text']}")
