from __future__ import annotations

import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import streamlit as st


LOGGER = logging.getLogger("truthlens.streamlit")


def configure_logging() -> None:
    """Set up lightweight console logging for Streamlit Cloud."""
    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def find_project_root(start_path: Path | None = None) -> Path:
    """Locate the repository root by walking upward from this file."""
    current_path = (start_path or Path(__file__)).resolve()
    for candidate in (current_path, *current_path.parents):
        if (candidate / "apps").is_dir() and (candidate / "data").is_dir():
            return candidate

    raise RuntimeError(
        f"Unable to locate the project root starting from {current_path}. "
        "Expected to find a directory containing both 'apps' and 'data'."
    )


PROJECT_ROOT = find_project_root()
API_ROOT = PROJECT_ROOT / "apps" / "api"

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.core.config import get_settings  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402
from app.services.prediction_service import PredictionService  # noqa: E402


@dataclass(slots=True)
class DeploymentStatus:
    project_root: Path
    model_dir: Path
    vectorizer_path: Path
    model_path: Path
    backend_ready: bool
    health_ok: bool
    sample_prediction: str | None
    sample_confidence: float | None
    error: str | None = None


def validate_backend_app() -> bool:
    """Confirm the FastAPI app can be imported and exposes the health route."""
    routes = {getattr(route, "path", "") for route in fastapi_app.routes}
    return "/api/v1/health" in routes


@st.cache_resource(show_spinner=False)
def load_deployment_status() -> DeploymentStatus:
    """Load model artifacts and validate startup once per Streamlit session."""
    configure_logging()

    settings = get_settings()
    LOGGER.info("Starting TruthLens deployment validation.")
    LOGGER.info("Project root: %s", settings.project_root)
    LOGGER.info("Model directory: %s", settings.model_dir)
    LOGGER.info("TF-IDF vectorizer: %s", settings.tfidf_vectorizer_path)
    LOGGER.info("Logistic regression model: %s", settings.logistic_regression_model_path)

    service = PredictionService(
        vectorizer_path=settings.tfidf_vectorizer_path,
        model_path=settings.logistic_regression_model_path,
    )

    try:
        service.load_artifacts()
        sample_result = service.predict("TruthLens deployment validation sample text.")
        backend_ready = service.ready
        health_ok = validate_backend_app()

        LOGGER.info(
            "Deployment validation complete. backend_ready=%s health_ok=%s sample_prediction=%s confidence=%s",
            backend_ready,
            health_ok,
            sample_result.prediction,
            sample_result.confidence,
        )

        return DeploymentStatus(
            project_root=settings.project_root,
            model_dir=settings.model_dir,
            vectorizer_path=settings.tfidf_vectorizer_path,
            model_path=settings.logistic_regression_model_path,
            backend_ready=backend_ready,
            health_ok=health_ok,
            sample_prediction=sample_result.prediction,
            sample_confidence=sample_result.confidence,
        )
    except Exception as exc:  # noqa: BLE001
        LOGGER.exception("Deployment validation failed.")
        return DeploymentStatus(
            project_root=settings.project_root,
            model_dir=settings.model_dir,
            vectorizer_path=settings.tfidf_vectorizer_path,
            model_path=settings.logistic_regression_model_path,
            backend_ready=service.ready,
            health_ok=False,
            sample_prediction=None,
            sample_confidence=None,
            error=str(exc),
        )


def render_status(status: DeploymentStatus) -> None:
    """Render a minimal deployment-only page without interactive controls."""
    st.set_page_config(page_title="TruthLens AI Deployment", layout="centered")

    st.title("TruthLens AI Deployment")
    st.caption("Minimal Streamlit entry point for deployment validation only.")

    if status.error:
        st.error("Startup validation failed.")
        st.code(status.error)
        st.stop()

    st.success("Startup validation passed.")
    st.write(f"Project root: `{status.project_root}`")
    st.write(f"Model directory: `{status.model_dir}`")
    st.write(f"Vectorizer: `{status.vectorizer_path.name}`")
    st.write(f"Model: `{status.model_path.name}`")
    st.write(f"FastAPI health route available: `{status.health_ok}`")
    st.write(f"Prediction service ready: `{status.backend_ready}`")
    st.write(f"Smoke test prediction: `{status.sample_prediction}`")
    st.write(f"Smoke test confidence: `{status.sample_confidence}`")
    st.info("This app does not replace the React frontend or FastAPI API. It only confirms deployment readiness.")


def main() -> None:
    configure_logging()
    status = load_deployment_status()
    render_status(status)


main()
