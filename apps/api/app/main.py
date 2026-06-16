from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import get_settings
from app.services.prediction_service import PredictionService

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Load the trained ML artifacts once when the API starts."""
    logger.info("TruthLens AI project root: %s", settings.project_root)
    logger.info("TF-IDF vectorizer path: %s", settings.tfidf_vectorizer_path)
    logger.info("Logistic regression model path: %s", settings.logistic_regression_model_path)

    try:
        prediction_service = PredictionService(
            vectorizer_path=settings.tfidf_vectorizer_path,
            model_path=settings.logistic_regression_model_path,
        )
        prediction_service.load_artifacts()
        application.state.prediction_service = prediction_service
        logger.info("TruthLens AI prediction service started successfully.")
        yield
    except Exception:
        logger.exception("TruthLens AI prediction service failed to start.")
        raise


app = FastAPI(title=settings.project_name, lifespan=lifespan)
app.include_router(api_router)
