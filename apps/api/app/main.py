from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.services.prediction_service import PredictionService

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Load the trained ML artifacts once when the API starts."""
    prediction_service = PredictionService(
        vectorizer_path=settings.tfidf_vectorizer_path,
        model_path=settings.logistic_regression_model_path,
    )
    prediction_service.load_artifacts()
    application.state.prediction_service = prediction_service
    yield


app = FastAPI(title=settings.project_name, lifespan=lifespan)
app.include_router(api_router)
