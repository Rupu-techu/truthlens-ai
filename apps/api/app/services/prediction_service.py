from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import logging

import joblib
import numpy as np

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PredictionResult:
    """Normalized output from the model service."""

    prediction: str
    confidence: float


class PredictionServiceError(RuntimeError):
    """Raised when the model artifacts cannot be loaded or used safely."""


class PredictionService:
    """Load the trained TF-IDF vectorizer and logistic regression model once at startup."""

    def __init__(self, vectorizer_path: Path, model_path: Path) -> None:
        self.vectorizer_path = vectorizer_path
        self.model_path = model_path
        self._vectorizer: Any | None = None
        self._model: Any | None = None

    @property
    def ready(self) -> bool:
        """Return True when both artifacts have been loaded into memory."""
        return self._vectorizer is not None and self._model is not None

    def load_artifacts(self) -> None:
        """Load and cache the trained artifacts from disk."""
        logger.info("Loading TF-IDF vectorizer from %s", self.vectorizer_path)
        logger.info("Loading logistic regression model from %s", self.model_path)

        if not self.vectorizer_path.exists():
            raise PredictionServiceError(
                f"TF-IDF vectorizer not found at {self.vectorizer_path}. "
                "Place tfidf_vectorizer.pkl in data/models and restart the API."
            )
        if not self.model_path.exists():
            raise PredictionServiceError(
                f"Logistic regression model not found at {self.model_path}. "
                "Place logistic_regression_model.pkl in data/models and restart the API."
            )

        self._vectorizer = joblib.load(self.vectorizer_path)
        self._model = joblib.load(self.model_path)
        logger.info("Prediction artifacts loaded successfully.")

    def predict(self, text: str) -> PredictionResult:
        """Predict whether a piece of text is fake or real news."""
        if not self.ready:
            raise PredictionServiceError("Prediction service is not ready. Model artifacts were not loaded.")

        normalized_text = text.strip()
        if not normalized_text:
            raise ValueError("text must not be empty")

        # The trained vectorizer turns raw text into the feature space expected by the classifier.
        features = self._vectorizer.transform([normalized_text])
        probabilities = self._model.predict_proba(features)[0]
        classes = list(getattr(self._model, "classes_", []))

        predicted_index = int(np.argmax(probabilities))
        predicted_class = classes[predicted_index] if classes else predicted_index
        confidence = round(float(probabilities[predicted_index]) * 100, 2)

        # Normalize the model output into the API contract expected by the frontend.
        prediction = self._normalize_label(predicted_class)
        return PredictionResult(prediction=prediction, confidence=confidence)

    @staticmethod
    def _normalize_label(raw_label: Any) -> str:
        """Convert the model's native label into the public Fake/Real contract."""
        if isinstance(raw_label, str):
            lowered_label = raw_label.strip().lower()
            if lowered_label in {"fake", "real"}:
                return lowered_label.capitalize()

        if raw_label in {1, "1", True}:
            return "Real"
        if raw_label in {0, "0", False}:
            return "Fake"

        raise PredictionServiceError(f"Unsupported model label: {raw_label!r}")
