"""
ML Prediction Service for Ticket Priority.
Loads the trained pipeline and provides priority predictions with confidence scores.
"""

import os
import joblib

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "priority_model.joblib")
_model_cache = None


def get_model():
    """
    Loads and caches the priority classification model.
    Validates model compatibility and auto-retrains if any version mismatch or error occurs.
    """
    global _model_cache
    if _model_cache is not None:
        return _model_cache

    need_train = False
    if not os.path.exists(MODEL_PATH):
        need_train = True
    else:
        try:
            loaded = joblib.load(MODEL_PATH)
            # Run test inference to ensure scikit-learn version compatibility
            loaded.predict(["test ping"])
            if hasattr(loaded, "predict_proba"):
                loaded.predict_proba(["test ping"])
            _model_cache = loaded
            return _model_cache
        except Exception as err:
            print(f"Incompatible model detected ({err}). Auto-retraining with active environment...")
            need_train = True

    if need_train:
        from train_model import train_and_save_model
        _model_cache = train_and_save_model(MODEL_PATH)

    return _model_cache


def predict_priority(text: str) -> dict:
    """
    Predict priority for a given complaint or ticket description.

    Returns:
        dict: {
            "predicted_priority": "High" | "Medium" | "Low",
            "confidence": float,
            "probabilities": {"High": float, "Medium": float, "Low": float}
        }
    """
    if not text or not text.strip():
        return {
            "predicted_priority": "Medium",
            "confidence": 0.33,
            "probabilities": {"High": 0.33, "Medium": 0.34, "Low": 0.33}
        }

    model = get_model()
    cleaned_text = text.strip()

    predicted_label = model.predict([cleaned_text])[0]

    # Get class probabilities if available
    probabilities = {}
    confidence = 1.0
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba([cleaned_text])[0]
        classes = model.classes_
        for cls, prob in zip(classes, probs):
            probabilities[str(cls)] = round(float(prob), 4)
        confidence = round(float(np_max := max(probs)), 4)

    return {
        "predicted_priority": str(predicted_label),
        "confidence": confidence,
        "probabilities": probabilities
    }
