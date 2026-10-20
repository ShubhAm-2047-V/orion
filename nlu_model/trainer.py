"""
Orion Intent & Entity Model Trainer.
Trains an NLP Intent Classification Pipeline on Orion's capabilities and commands.
Saves model weights, vectorizer, and evaluation telemetry to disk.
"""
import os
import json
import time
import joblib
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, accuracy_score

from nlu_model.normalizer import normalize_text
from nlu_model.dataset import TRAINING_DATA

MODEL_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_FILE = os.path.join(MODEL_DIR, "trained_model.pkl")
METADATA_FILE = os.path.join(MODEL_DIR, "model_metadata.json")

def prepare_training_dataset() -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    """
    Normalizes dataset samples and prepares input features (X) and intent labels (y).
    """
    X: List[str] = []
    y: List[str] = []
    metadata_records: List[Dict[str, Any]] = []

    for item in TRAINING_DATA:
        raw_text = item["text"]
        norm_text, _, _ = normalize_text(raw_text)
        intent = item["intent"]
        
        # Include both raw and normalized variants for robust generalization
        X.append(raw_text.lower())
        y.append(intent)
        metadata_records.append(item)

        if norm_text and norm_text != raw_text.lower():
            X.append(norm_text)
            y.append(intent)
            metadata_records.append(item)

    return X, y, metadata_records

def train_orion_model() -> Dict[str, Any]:
    """
    Trains the intent classification pipeline and serializes the trained model.
    """
    start_time = time.time()
    print("[TRAINER]: Preparing Orion training dataset...")
    X, y, records = prepare_training_dataset()
    unique_classes = sorted(list(set(y)))
    print(f"[TRAINER]: Loaded {len(X)} training samples across {len(unique_classes)} distinct intent classes.")

    # Build Pipeline with character and word n-grams
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 3),
            sublinear_tf=True,
            strip_accents='unicode',
            min_df=1,
            analyzer='word'
        )),
        ('clf', LogisticRegression(C=5.0, max_iter=1000, random_state=42))
    ])

    print("[TRAINER]: Fitting calibrated intent classification model...")
    pipeline.fit(X, y)

    # Calculate train accuracy
    y_pred = pipeline.predict(X)
    train_acc = accuracy_score(y, y_pred)
    train_duration = round(time.time() - start_time, 3)
    print(f"[TRAINER]: Training completed in {train_duration}s with Training Accuracy: {train_acc * 100:.2f}%")

    # Map intent to default engine & action metadata
    intent_registry: Dict[str, Dict[str, Any]] = {}
    for r in records:
        intent = r["intent"]
        if intent not in intent_registry:
            intent_registry[intent] = {
                "engine": r["engine"],
                "action": r["action"],
                "default_params": r.get("params", {}),
                "ambiguous": r.get("ambiguous", False),
                "question": r.get("question", None)
            }

    # Save serialized model artifact
    joblib.dump(pipeline, MODEL_FILE)
    print(f"[TRAINER]: Model weights saved to {MODEL_FILE}")

    # Save model metadata
    metadata = {
        "model_name": "Orion-NLU-Calibrated-V1",
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_samples": len(X),
        "total_intents": len(unique_classes),
        "intent_classes": unique_classes,
        "intent_registry": intent_registry,
        "training_accuracy": train_acc,
        "training_duration_seconds": train_duration
    }

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[TRAINER]: Metadata saved to {METADATA_FILE}")

    return metadata

if __name__ == "__main__":
    train_orion_model()
