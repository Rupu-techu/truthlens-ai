from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService, PredictionServiceError

router = APIRouter(tags=["prediction"])


def get_prediction_service(request: Request) -> PredictionService:
    """Retrieve the shared prediction service that was initialized at startup."""
    service = getattr(request.app.state, "prediction_service", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction service is not available.",
        )
    return service


@router.post("/predict", response_model=PredictionResponse)
def predict_news(
    request: PredictionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    """Classify incoming news text as Fake or Real."""
    try:
        result = prediction_service.predict(request.text)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except PredictionServiceError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating the prediction.",
        ) from exc

    return PredictionResponse(prediction=result.prediction, confidence=result.confidence)
