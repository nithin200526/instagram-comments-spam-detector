"""
Hybrid NLP Spam Detection Engine.
Combines TF-IDF lexical features with 25 NLP semantic features.
Trains on real YouTube Spam Collection + Instagram datasets.

Pipeline:
  Raw Text → [TF-IDF (lexical)] + [NLP Features (semantic)] → Logistic Regression

NLP features include:
  - VADER sentiment analysis (emotional manipulation detection)
  - Linguistic features (writing style, vocabulary richness)
  - Behavioral signals (urgency, self-promotion, incentives)
"""

import os
import glob
import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack, csr_matrix
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report

from backend.preprocessing import preprocess_text, extract_nlp_features, NLP_FEATURE_NAMES

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "spam_classifier.joblib")
VECTORIZER_PATH = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")
SCALER_PATH = os.path.join(MODELS_DIR, "nlp_scaler.joblib")
DATASET_DIR = os.path.join(PROJECT_ROOT, "youtube+spam+collection")

# ─── Singleton Model ─────────────────────────────────────────────────────────
_model = None
_vectorizer = None
_scaler = None

# ─── Spam Threshold (mutable at runtime) ─────────────────────────────────────
_threshold = 0.50


def get_threshold() -> float:
    return _threshold


def set_threshold(value: float):
    global _threshold
    _threshold = max(0.1, min(0.99, value))


# ─── Load Real Datasets ──────────────────────────────────────────────────────

def _load_datasets() -> pd.DataFrame:
    """
    Load real-world datasets:
      1. YouTube Spam Collection (5 CSV files, ~1,956 rows)
      2. Instagram Spam Dataset (500k rows — sampled for balance)
    """
    frames = []

    # YouTube Spam Collection
    yt_pattern = os.path.join(DATASET_DIR, "Youtube*.csv")
    for f in sorted(glob.glob(yt_pattern)):
        df = pd.read_csv(f, encoding="utf-8", on_bad_lines="skip")
        df = df.rename(columns={"CONTENT": "text", "CLASS": "label"})
        df = df[["text", "label"]].dropna()
        df["label"] = df["label"].astype(int)
        frames.append(df)
        print(f"   Loaded {os.path.basename(f)}: {len(df)} rows")

    # Instagram Spam Dataset (balanced sample)
    ig_path = os.path.join(DATASET_DIR, "instagram_spam_dataset_500k_unique_70_30.csv")
    if os.path.exists(ig_path):
        ig = pd.read_csv(ig_path, encoding="utf-8", on_bad_lines="skip")
        ig = ig.rename(columns={"comment": "text"})
        ig = ig[["text", "label"]].dropna()
        ig["label"] = ig["label"].astype(int)

        n = min(25000, len(ig[ig["label"] == 1]), len(ig[ig["label"] == 0]))
        ig_sampled = pd.concat([
            ig[ig["label"] == 1].sample(n=n, random_state=42),
            ig[ig["label"] == 0].sample(n=n, random_state=42),
        ], ignore_index=True)
        frames.append(ig_sampled)
        print(f"   Loaded Instagram: {len(ig_sampled)} rows (from {len(ig)})")

    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(subset=["text"]).reset_index(drop=True)
    spam_n = (combined["label"] == 1).sum()
    ham_n = (combined["label"] == 0).sum()
    print(f"\n   Combined: {len(combined)} rows | Spam: {spam_n} | Ham: {ham_n}")
    return combined


# ─── Feature Building ────────────────────────────────────────────────────────

def _build_nlp_matrix(texts: pd.Series) -> np.ndarray:
    """Extract NLP features for each text → numpy array."""
    features_list = []
    for text in texts:
        feat = extract_nlp_features(str(text))
        features_list.append([feat[k] for k in NLP_FEATURE_NAMES])
    return np.array(features_list, dtype=np.float64)


def _build_combined_features(texts_raw: pd.Series, texts_cleaned: pd.Series,
                              vectorizer: TfidfVectorizer, scaler: StandardScaler,
                              fit: bool = False):
    """
    Build hybrid feature matrix: TF-IDF (lexical) + scaled NLP (semantic).

    This gives the model BOTH:
      - What words appear (TF-IDF) → pattern matching
      - What the text means (NLP) → understanding
    """
    # TF-IDF features
    if fit:
        tfidf_matrix = vectorizer.fit_transform(texts_cleaned)
    else:
        tfidf_matrix = vectorizer.transform(texts_cleaned)

    # NLP semantic features
    nlp_matrix = _build_nlp_matrix(texts_raw)

    if fit:
        nlp_scaled = scaler.fit_transform(nlp_matrix)
    else:
        nlp_scaled = scaler.transform(nlp_matrix)

    # Combine: [TF-IDF sparse | NLP dense] → single feature matrix
    combined = hstack([tfidf_matrix, csr_matrix(nlp_scaled)])
    return combined


# ─── Training ────────────────────────────────────────────────────────────────

def train_model():
    """Train hybrid NLP spam classifier on real datasets."""
    print("\n===== Training Hybrid NLP Spam Classifier =====\n")

    df = _load_datasets()

    print("\n[1/4] Preprocessing text...")
    df["cleaned"] = df["text"].astype(str).apply(preprocess_text)
    df = df[df["cleaned"].str.strip().astype(bool)].reset_index(drop=True)
    print(f"      {len(df)} rows after cleaning")

    X_train_raw, X_test_raw, y_train, y_test = train_test_split(
        df[["text", "cleaned"]], df["label"],
        test_size=0.2, random_state=42, stratify=df["label"]
    )

    print(f"\n[2/4] Building hybrid features (TF-IDF + 25 NLP features)...")
    print(f"      Train: {len(X_train_raw)} | Test: {len(X_test_raw)}")

    vectorizer = TfidfVectorizer(
        max_features=10000,
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.95,
        sublinear_tf=True,
    )
    scaler = StandardScaler()

    X_train_combined = _build_combined_features(
        X_train_raw["text"], X_train_raw["cleaned"],
        vectorizer, scaler, fit=True
    )
    X_test_combined = _build_combined_features(
        X_test_raw["text"], X_test_raw["cleaned"],
        vectorizer, scaler, fit=False
    )

    total_features = X_train_combined.shape[1]
    print(f"      Feature matrix: {X_train_combined.shape}")
    print(f"      TF-IDF features: {total_features - len(NLP_FEATURE_NAMES)}")
    print(f"      NLP features: {len(NLP_FEATURE_NAMES)}")

    print(f"\n[3/4] Training Logistic Regression on hybrid features...")
    model = LogisticRegression(max_iter=1000, C=1.0, random_state=42, solver="lbfgs")
    model.fit(X_train_combined, y_train)

    y_pred = model.predict(X_test_combined)
    print(f"\n[4/4] Evaluation:\n")
    print(classification_report(y_test, y_pred, target_names=["Ham", "Spam"]))

    # Show top NLP feature importances
    coefs = model.coef_[0]
    nlp_coefs = coefs[-len(NLP_FEATURE_NAMES):]
    sorted_idx = np.argsort(np.abs(nlp_coefs))[::-1]
    print("      Top NLP features by importance:")
    for i in sorted_idx[:10]:
        direction = "SPAM" if nlp_coefs[i] > 0 else "HAM"
        print(f"        {NLP_FEATURE_NAMES[i]:<25s}  coef={nlp_coefs[i]:+.4f}  ({direction})")

    # Save artifacts
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"\n   Model saved to {MODELS_DIR}")

    return model, vectorizer, scaler


# ─── Loading ──────────────────────────────────────────────────────────────────

def load_model():
    """Load model from disk, or train if not found."""
    global _model, _vectorizer, _scaler

    if all(os.path.exists(p) for p in [MODEL_PATH, VECTORIZER_PATH, SCALER_PATH]):
        print("   Loading existing NLP model...")
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VECTORIZER_PATH)
        _scaler = joblib.load(SCALER_PATH)
    else:
        _model, _vectorizer, _scaler = train_model()

    print("   Model ready")


def retrain_model():
    """Force retrain (deletes old artifacts first)."""
    global _model, _vectorizer, _scaler
    for path in [MODEL_PATH, VECTORIZER_PATH, SCALER_PATH]:
        if os.path.exists(path):
            os.remove(path)
    _model, _vectorizer, _scaler = train_model()


# ─── Prediction ───────────────────────────────────────────────────────────────

def predict_spam(text: str) -> dict:
    """
    Predict whether text is spam using hybrid NLP understanding.

    The model considers BOTH:
      - Lexical patterns (what words/phrases appear)
      - Semantic features (sentiment, intent, writing style)

    Returns:
        dict with label, confidence, spam_probability, is_spam, should_hide
    """
    if _model is None or _vectorizer is None or _scaler is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")

    # Build same hybrid features used during training
    cleaned = preprocess_text(text)
    tfidf = _vectorizer.transform([cleaned])

    nlp_feat = extract_nlp_features(text)
    nlp_array = np.array([[nlp_feat[k] for k in NLP_FEATURE_NAMES]], dtype=np.float64)
    nlp_scaled = _scaler.transform(nlp_array)

    combined = hstack([tfidf, csr_matrix(nlp_scaled)])

    proba = _model.predict_proba(combined)[0]
    spam_prob = float(proba[1])
    is_spam = spam_prob >= _threshold
    confidence = spam_prob if is_spam else (1 - spam_prob)

    return {
        "label": "Spam" if is_spam else "Not Spam",
        "confidence": round(confidence, 4),
        "spam_probability": round(spam_prob, 4),
        "is_spam": is_spam,
        "should_hide": is_spam,
        "cleaned_text": cleaned,
        "nlp_features": {
            "sentiment": nlp_feat["sentiment_compound"],
            "promo_score": nlp_feat["promo_score"],
            "urgency_score": nlp_feat["urgency_score"],
            "incentive_score": nlp_feat["incentive_score"],
        },
    }
