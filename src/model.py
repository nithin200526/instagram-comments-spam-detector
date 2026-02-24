"""
Model training pipeline for spam detection.
Trains Logistic Regression, Naive Bayes, and SVM on TF-IDF features.
Compares models and saves the best performer.
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.preprocessing import preprocess_dataframe

# ─── Paths ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "comments.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")


def load_and_preprocess():
    """Load dataset and apply text preprocessing."""
    print("📂 Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    print(f"   Loaded {len(df)} records ({df['CLASS'].sum()} spam, {(df['CLASS'] == 0).sum()} ham)")
    
    print("🔧 Preprocessing text...")
    df = preprocess_dataframe(df)
    
    # Remove empty rows after preprocessing
    df = df[df["cleaned_text"].str.strip().astype(bool)]
    print(f"   {len(df)} records after cleaning")
    
    return df


def train_and_evaluate():
    """Train all models, compare, and save the best one."""
    df = load_and_preprocess()
    
    # Split data
    X = df["cleaned_text"]
    y = df["CLASS"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\n📊 Train: {len(X_train)} | Test: {len(X_test)}")
    
    # TF-IDF Vectorization (unigrams + bigrams)
    print("\n🔤 Vectorizing with TF-IDF (unigrams + bigrams)...")
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
    )
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)
    print(f"   Feature matrix shape: {X_train_tfidf.shape}")
    
    # ─── Define Models ────────────────────────────────────────────────────────
    models = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000, C=1.0, random_state=42
        ),
        "Naive Bayes": MultinomialNB(alpha=0.1),
        "SVM": CalibratedClassifierCV(
            LinearSVC(max_iter=2000, random_state=42), cv=3
        ),
    }
    
    # ─── Train & Evaluate ─────────────────────────────────────────────────────
    results = {}
    best_model_name = None
    best_f1 = 0
    
    print("\n" + "=" * 65)
    print("📈 MODEL COMPARISON")
    print("=" * 65)
    
    for name, model in models.items():
        print(f"\n{'─' * 50}")
        print(f"🤖 Training: {name}")
        print(f"{'─' * 50}")
        
        model.fit(X_train_tfidf, y_train)
        y_pred = model.predict(X_test_tfidf)
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        cm = confusion_matrix(y_test, y_pred)
        
        results[name] = {
            "accuracy": acc,
            "precision": prec,
            "recall": rec,
            "f1": f1,
            "confusion_matrix": cm,
            "model": model,
        }
        
        print(f"   Accuracy  : {acc:.4f}")
        print(f"   Precision : {prec:.4f}")
        print(f"   Recall    : {rec:.4f}")
        print(f"   F1 Score  : {f1:.4f}")
        print(f"   Confusion Matrix:")
        print(f"     TN={cm[0][0]:4d}  FP={cm[0][1]:4d}")
        print(f"     FN={cm[1][0]:4d}  TP={cm[1][1]:4d}")
        
        if f1 > best_f1:
            best_f1 = f1
            best_model_name = name
    
    # ─── Full Report for Best Model ──────────────────────────────────────────
    print("\n" + "=" * 65)
    print(f"🏆 BEST MODEL: {best_model_name} (F1={best_f1:.4f})")
    print("=" * 65)
    
    best_model = results[best_model_name]["model"]
    y_pred_best = best_model.predict(X_test_tfidf)
    print("\n📋 Full Classification Report:")
    print(classification_report(y_test, y_pred_best, target_names=["Ham", "Spam"]))
    
    # ─── Save Best Model + Vectorizer ─────────────────────────────────────────
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    model_path = os.path.join(MODELS_DIR, "spam_classifier.joblib")
    vectorizer_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")
    
    joblib.dump(best_model, model_path)
    joblib.dump(tfidf, vectorizer_path)
    
    print(f"\n💾 Saved model     → {model_path}")
    print(f"💾 Saved vectorizer → {vectorizer_path}")
    
    # Save a summary of results
    summary = {
        "best_model": best_model_name,
        "metrics": {
            name: {k: v for k, v in r.items() if k != "model" and k != "confusion_matrix"}
            for name, r in results.items()
        },
    }
    summary_path = os.path.join(MODELS_DIR, "training_summary.joblib")
    joblib.dump(summary, summary_path)
    print(f"💾 Saved summary   → {summary_path}")
    
    return best_model, tfidf, results


if __name__ == "__main__":
    train_and_evaluate()
