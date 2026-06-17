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


@dataclass(slots=True)
class PredictionDebugResult:
    """Detailed model output used by the Streamlit debug page."""

    prediction: str
    confidence: float
    raw_prediction: Any
    predicted_index: int
    probabilities: list[float]
    classes: list[Any]
    label_mapping: dict[str, str]


class PredictionServiceError(RuntimeError):
    """Raised when the model artifacts cannot be loaded or used safely."""


class PredictionService:
    """Load the trained TF-IDF vectorizer and logistic regression model once at startup."""

    def __init__(self, vectorizer_path: Path, model_path: Path) -> None:
        self.vectorizer_path = vectorizer_path
        self.model_path = model_path
        self._vectorizer: Any | None = None
        self._model: Any | None = None
        self._label_mapping: dict[str, str] | None = None

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
        self._label_mapping = self._build_label_mapping()
        logger.info("Prediction artifacts loaded successfully.")
        logger.info("Model classes: %s", list(getattr(self._model, "classes_", [])))
        logger.info("Resolved label mapping: %s", self._label_mapping)

    @property
    def label_mapping(self) -> dict[str, str]:
        """Return the current raw-class to public-label mapping."""
        if self._label_mapping is None:
            self._label_mapping = self._build_label_mapping()
        return dict(self._label_mapping)

    @property
    def model_classes(self) -> list[Any]:
        """Return the classifier classes as stored by scikit-learn."""
        if self._model is None:
            return []
        return list(getattr(self._model, "classes_", []))

    def predict(self, text: str) -> PredictionResult:
        """Predict whether a piece of text is fake or real news."""
        debug_result = self.predict_with_debug(text)
        logger.info(
            "Prediction raw_class=%r predicted_index=%s probabilities=%s confidence=%.2f prediction=%s",
            debug_result.raw_prediction,
            debug_result.predicted_index,
            debug_result.probabilities,
            debug_result.confidence,
            debug_result.prediction,
        )
        return PredictionResult(prediction=debug_result.prediction, confidence=debug_result.confidence)

    def predict_with_debug(self, text: str) -> PredictionDebugResult:
        """Return the public prediction together with raw model diagnostics."""
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
        prediction = self._normalize_label(predicted_class)
        mapping = self.label_mapping

        logger.info(
            "Detailed model output raw_prediction=%r probability_array=%s label_mapping=%s",
            predicted_class,
            np.round(probabilities, 6).tolist(),
            mapping,
        )

        return PredictionDebugResult(
            prediction=prediction,
            confidence=confidence,
            raw_prediction=predicted_class,
            predicted_index=predicted_index,
            probabilities=np.round(probabilities, 6).tolist(),
            classes=classes,
            label_mapping=mapping,
        )

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

    def _build_label_mapping(self) -> dict[str, str]:
        """Create a human-readable mapping from raw model labels to the public contract."""
        classes = list(getattr(self._model, "classes_", []))
        mapping: dict[str, str] = {}
        for raw_label in classes:
            normalized = self._normalize_label(raw_label)
            mapping[str(raw_label)] = normalized
        return mapping
