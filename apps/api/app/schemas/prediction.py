from typing import Literal

from pydantic import BaseModel, Field, field_validator


PredictionLabel = Literal["Fake", "Real"]


class PredictionRequest(BaseModel):
    """Request payload for fake news prediction."""

    text: str = Field(..., min_length=1, description="News article text to classify.")

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        """Reject blank or whitespace-only input before hitting the model."""
        cleaned_text = value.strip()
        if not cleaned_text:
            raise ValueError("text must not be empty")
        return cleaned_text


class PredictionResponse(BaseModel):
    """Response payload returned by the prediction API."""

    prediction: PredictionLabel
    confidence: float = Field(..., ge=0, le=100, description="Prediction confidence as a percentage.")
