from __future__ import annotations

import hashlib
import logging
import os
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import altair as alt
import pandas as pd
import requests
import streamlit as st
from fastapi.testclient import TestClient


LOGGER = logging.getLogger("truthlens.streamlit")
FRONTEND_URL_ENV = "TRUTHLENS_FRONTEND_URL"
MODEL_VERSION_ENV = "TRUTHLENS_MODEL_VERSION"
DEFAULT_FRONTEND_URL = "http://localhost:5173"
SMOKE_TEST_TEXT = "TruthLens deployment validation sample text."
PAGE_HOME = "Home"
PAGE_ANALYZER = "News Analyzer"
PAGE_DASHBOARD = "Dashboard"
PAGE_ABOUT = "About"
PAGES = [PAGE_HOME, PAGE_ANALYZER, PAGE_DASHBOARD, PAGE_ABOUT]
DATASET_REAL_COUNT = 21211
DATASET_FAKE_COUNT = 23478
DATASET_TOTAL = DATASET_REAL_COUNT + DATASET_FAKE_COUNT
MAX_INPUT_CHARS = 5000


@dataclass(slots=True)
class ArtifactStatus:
    """Deployment metadata for a model artifact."""

    path: Path
    exists: bool
    size_bytes: int | None
    modified_utc: str | None
    fingerprint: str | None


@dataclass(slots=True)
class FrontendStatus:
    """Deployment metadata for the React frontend URL."""

    url: str
    configured: bool
    reachable: bool | None
    details: str | None = None
    error: str | None = None


@dataclass(slots=True)
class BackendStatus:
    """Backend startup and health endpoint diagnostics."""

    app_started: bool
    health_ok: bool
    health_route: str | None
    health_payload: dict[str, Any] | None
    error: str | None = None


@dataclass(slots=True)
class DeploymentStatus:
    """Snapshot of the launcher, backend, model, and frontend state."""

    project_root: Path
    api_root: Path
    model_dir: Path
    vectorizer: ArtifactStatus
    model: ArtifactStatus
    frontend: FrontendStatus
    backend: BackendStatus
    prediction_service_ready: bool
    sample_prediction: str | None
    sample_confidence: float | None
    model_version: str
    bundle_fingerprint: str
    error: str | None = None


@dataclass(slots=True)
class RuntimeSettings:
    """Resolved project paths used by the launcher when backend imports fail."""

    project_root: Path
    model_dir: Path
    tfidf_vectorizer_path: Path
    logistic_regression_model_path: Path


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


def file_sha256(path: Path) -> str:
    """Compute a stable fingerprint for deployment diagnostics."""
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def format_timestamp(path: Path) -> str:
    """Render a file modification time in a human-friendly UTC format."""
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return modified.strftime("%Y-%m-%d %H:%M:%S UTC")


def inspect_artifact(path: Path) -> ArtifactStatus:
    """Collect size, timestamp, and fingerprint information for a model artifact."""
    if not path.exists():
        return ArtifactStatus(
            path=path,
            exists=False,
            size_bytes=None,
            modified_utc=None,
            fingerprint=None,
        )

    return ArtifactStatus(
        path=path,
        exists=True,
        size_bytes=path.stat().st_size,
        modified_utc=format_timestamp(path),
        fingerprint=file_sha256(path),
    )


def build_model_version(vectorizer: ArtifactStatus, model: ArtifactStatus) -> tuple[str, str]:
    """Return a user-facing model version and the underlying bundle fingerprint."""
    if vectorizer.fingerprint is None or model.fingerprint is None:
        return "unavailable", "unavailable"

    bundle_fingerprint = f"{vectorizer.fingerprint[:12]}-{model.fingerprint[:12]}"
    override = os.getenv(MODEL_VERSION_ENV, "").strip()
    if override:
        return override, bundle_fingerprint

    return f"artifact-bundle:{bundle_fingerprint}", bundle_fingerprint


def validate_frontend_url(frontend_url: str) -> FrontendStatus:
    """Validate the React frontend URL configuration and perform a reachability probe."""
    parsed = urlparse(frontend_url)
    configured = parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    if not configured:
        return FrontendStatus(
            url=frontend_url,
            configured=False,
            reachable=None,
            error=(
                f"{FRONTEND_URL_ENV} must be a fully qualified http:// or https:// URL. "
                f"Received: {frontend_url!r}"
            ),
        )

    try:
        response = requests.get(frontend_url, timeout=4, allow_redirects=True)
        details = f"HTTP {response.status_code}"
        response.close()
        return FrontendStatus(
            url=frontend_url,
            configured=True,
            reachable=True,
            details=details,
        )
    except requests.RequestException as exc:
        return FrontendStatus(
            url=frontend_url,
            configured=True,
            reachable=False,
            error=str(exc),
        )


def validate_backend_app() -> BackendStatus:
    """Confirm the FastAPI app starts cleanly and serves the health endpoint."""
    if fastapi_app is None:
        return BackendStatus(
            app_started=False,
            health_ok=False,
            health_route=None,
            health_payload=None,
            error=BACKEND_IMPORT_ERROR or "FastAPI backend import is not available.",
        )

    candidate_routes = ["/api/v1/health", "/health"]

    try:
        with TestClient(fastapi_app) as client:
            for health_route in candidate_routes:
                response = client.get(health_route)
                if response.status_code == 404:
                    continue

                try:
                    response.raise_for_status()
                    payload = response.json()
                except Exception as exc:  # noqa: BLE001
                    return BackendStatus(
                        app_started=True,
                        health_ok=False,
                        health_route=health_route,
                        health_payload=None,
                        error=str(exc),
                    )

                health_ok = isinstance(payload, dict) and payload.get("status") == "ok"
                return BackendStatus(
                    app_started=True,
                    health_ok=health_ok,
                    health_route=health_route,
                    health_payload=payload if isinstance(payload, dict) else None,
                    error=None if health_ok else "Health endpoint returned an unexpected payload.",
                )

        return BackendStatus(
            app_started=True,
            health_ok=False,
            health_route=None,
            health_payload=None,
            error="Unable to locate a reachable health route on the FastAPI application.",
        )
    except Exception as exc:  # noqa: BLE001
        return BackendStatus(
            app_started=False,
            health_ok=False,
            health_route=None,
            health_payload=None,
            error=str(exc),
        )


def normalize_label(value: str) -> str:
    """Convert a prediction string into a predictable display label."""
    return value.strip().lower()


def render_bool(value: bool | None) -> str:
    """Convert a boolean status into a concise human-readable label."""
    if value is True:
        return "Ready"
    if value is False:
        return "Blocked"
    return "Unknown"


def friendly_bytes(value: int | None) -> str:
    """Format file sizes for the deployment dashboard."""
    if value is None:
        return "n/a"
    if value < 1024:
        return f"{value} B"
    if value < 1024 * 1024:
        return f"{value / 1024:.1f} KB"
    return f"{value / (1024 * 1024):.1f} MB"


def format_datetime(value: str) -> str:
    """Render an ISO timestamp into a compact human-readable label."""
    return datetime.fromisoformat(value).strftime("%b %d, %Y %I:%M %p")


def truncate_text(value: str, limit: int = 120) -> str:
    """Trim article text for table and history previews."""
    compact = " ".join(value.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


PROJECT_ROOT = find_project_root()
API_ROOT = PROJECT_ROOT / "apps" / "api"
MODEL_DIR = PROJECT_ROOT / "data" / "models"

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

BACKEND_IMPORT_ERROR: str | None = None
fastapi_app: Any | None = None
get_settings: Any | None = None
PredictionService: Any | None = None

try:  # noqa: SIM105
    from app.core.config import get_settings as _get_settings  # noqa: E402
    from app.main import app as _fastapi_app  # noqa: E402
    from app.services.prediction_service import PredictionService as _PredictionService  # noqa: E402

    get_settings = _get_settings
    fastapi_app = _fastapi_app
    PredictionService = _PredictionService
except Exception as exc:  # noqa: BLE001
    BACKEND_IMPORT_ERROR = f"Unable to import the FastAPI backend from {API_ROOT}: {exc}"


def resolve_runtime_settings() -> RuntimeSettings:
    """Return backend settings if available, otherwise fall back to repository defaults."""
    if callable(get_settings):
        settings = get_settings()
        return RuntimeSettings(
            project_root=settings.project_root,
            model_dir=settings.model_dir,
            tfidf_vectorizer_path=settings.tfidf_vectorizer_path,
            logistic_regression_model_path=settings.logistic_regression_model_path,
        )

    return RuntimeSettings(
        project_root=PROJECT_ROOT,
        model_dir=MODEL_DIR,
        tfidf_vectorizer_path=MODEL_DIR / "tfidf_vectorizer.pkl",
        logistic_regression_model_path=MODEL_DIR / "logistic_regression_model.pkl",
    )


@st.cache_resource(show_spinner=False)
def load_prediction_service() -> Any:
    """Load the trained artifacts once and return the ready prediction service."""
    if PredictionService is None:
        raise RuntimeError(BACKEND_IMPORT_ERROR or "Prediction service import is not available.")

    settings = resolve_runtime_settings()
    service = PredictionService(
        vectorizer_path=settings.tfidf_vectorizer_path,
        model_path=settings.logistic_regression_model_path,
    )
    service.load_artifacts()
    return service


@st.cache_resource(show_spinner=False)
def load_deployment_status() -> DeploymentStatus:
    """Load model artifacts and validate startup once per Streamlit session."""
    configure_logging()

    settings = resolve_runtime_settings()
    frontend_url = os.getenv(FRONTEND_URL_ENV, DEFAULT_FRONTEND_URL).strip()

    LOGGER.info("Starting TruthLens deployment validation.")
    LOGGER.info("Project root: %s", settings.project_root)
    LOGGER.info("API root: %s", API_ROOT)
    LOGGER.info("Model directory: %s", settings.model_dir)
    LOGGER.info("TF-IDF vectorizer: %s", settings.tfidf_vectorizer_path)
    LOGGER.info("Logistic regression model: %s", settings.logistic_regression_model_path)
    LOGGER.info("Frontend URL: %s", frontend_url)

    vectorizer_status = inspect_artifact(settings.tfidf_vectorizer_path)
    model_status = inspect_artifact(settings.logistic_regression_model_path)
    frontend_status = validate_frontend_url(frontend_url)
    model_version, bundle_fingerprint = build_model_version(vectorizer_status, model_status)
    backend_status = validate_backend_app()

    prediction_service_ready = False
    sample_prediction: str | None = None
    sample_confidence: float | None = None
    service_error: str | None = None

    try:
        service = load_prediction_service()
        prediction_service_ready = service.ready
        sample_result = service.predict(SMOKE_TEST_TEXT)
        sample_prediction = sample_result.prediction
        sample_confidence = sample_result.confidence
    except Exception as exc:  # noqa: BLE001
        service_error = str(exc)
        LOGGER.exception("Deployment validation failed.")

    return DeploymentStatus(
        project_root=settings.project_root,
        api_root=API_ROOT,
        model_dir=settings.model_dir,
        vectorizer=vectorizer_status,
        model=model_status,
        frontend=frontend_status,
        backend=backend_status,
        prediction_service_ready=prediction_service_ready,
        sample_prediction=sample_prediction,
        sample_confidence=sample_confidence,
        model_version=model_version,
        bundle_fingerprint=bundle_fingerprint,
        error=service_error or backend_status.error or frontend_status.error,
    )


def initialize_session_state() -> None:
    """Seed all session state keys used by the UI."""
    st.session_state.setdefault("truthlens_page", PAGE_HOME)
    st.session_state.setdefault("truthlens_history", [])
    st.session_state.setdefault("truthlens_latest_result", None)
    st.session_state.setdefault("truthlens_article_input", "")
    st.session_state.setdefault("truthlens_last_error", None)


def set_active_page(page: str) -> None:
    """Update the visible page without changing any prediction state."""
    st.session_state.truthlens_page = page


def get_active_page() -> str:
    """Return the current page selection."""
    page = st.session_state.get("truthlens_page", PAGE_HOME)
    return page if page in PAGES else PAGE_HOME


def create_history_id() -> str:
    """Create a stable session-local prediction identifier."""
    return str(uuid.uuid4())


def add_prediction_to_history(text: str, result: Any) -> None:
    """Store a prediction in session history for dashboard analytics."""
    history = list(st.session_state.truthlens_history)
    history.insert(
        0,
        {
            "id": create_history_id(),
            "text": text,
            "prediction": result.prediction,
            "confidence": float(result.confidence),
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    )
    st.session_state.truthlens_history = history[:25]
    st.session_state.truthlens_latest_result = {
        "prediction": result.prediction,
        "confidence": float(result.confidence),
    }


def history_to_frame(history: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert stored history entries into a DataFrame for charts and tables."""
    if not history:
        return pd.DataFrame(columns=["Created", "Prediction", "Confidence", "Text"])

    frame = pd.DataFrame(history)
    frame = frame.assign(
        Created=frame["created_at"].map(format_datetime),
        Prediction=frame["prediction"].map(lambda value: value.capitalize()),
        Confidence=frame["confidence"].astype(float),
        Text=frame["text"].map(lambda value: truncate_text(value, 110)),
    )
    return frame[["Created", "Prediction", "Confidence", "Text", "created_at", "id"]]


def apply_custom_styles() -> None:
    """Inject a restrained visual system for the light-theme product UI."""
    st.markdown(
        """
        <style>
        :root {
            --tl-bg: #fbfbff;
            --tl-panel: rgba(255, 255, 255, 0.94);
            --tl-panel-strong: #ffffff;
            --tl-border: rgba(148, 163, 184, 0.18);
            --tl-border-strong: rgba(165, 180, 252, 0.42);
            --tl-text: #0f172a;
            --tl-muted: #5b6475;
            --tl-shadow: 0 20px 60px rgba(15, 23, 42, 0.06);
        }

        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at top left, rgba(224, 231, 255, 0.7), transparent 30%),
                radial-gradient(circle at top right, rgba(220, 252, 231, 0.45), transparent 28%),
                var(--tl-bg);
            color: var(--tl-text);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        #MainMenu, footer {
            visibility: hidden;
        }

        [data-testid="stSidebar"] {
            display: none;
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2.5rem;
            max-width: 1240px;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 24px;
            border: 1px solid var(--tl-border);
            background: var(--tl-panel);
            box-shadow: 0 14px 40px rgba(15, 23, 42, 0.04);
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-2px);
            border-color: var(--tl-border-strong);
            box-shadow: 0 20px 48px rgba(15, 23, 42, 0.08);
        }

        div[data-testid="stButton"] > button {
            border-radius: 14px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
        }

        div[data-testid="stButton"] > button:hover {
            transform: translateY(-1px);
            border-color: rgba(139, 130, 246, 0.28);
            box-shadow: 0 10px 24px rgba(129, 140, 248, 0.14);
        }

        div[data-testid="stButton"] > button[kind="primary"] {
            background: linear-gradient(135deg, #8b82f6, #a5b4fc);
            color: white;
            border-color: rgba(139, 130, 246, 0.38);
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.86);
            border-radius: 20px;
            border: 1px solid rgba(148, 163, 184, 0.14);
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.04);
        }

        .truthlens-shell {
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.7);
            background: rgba(255, 255, 255, 0.78);
            box-shadow: var(--tl-shadow);
            backdrop-filter: blur(18px);
            padding: 1rem;
        }

        .truthlens-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            width: fit-content;
            padding: 0.35rem 0.8rem;
            border-radius: 999px;
            background: linear-gradient(135deg, rgba(139, 130, 246, 0.12), rgba(219, 234, 254, 0.95));
            color: #4f46e5;
            border: 1px solid rgba(139, 130, 246, 0.16);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .truthlens-title {
            margin: 0;
            font-size: 2.05rem;
            line-height: 1.05;
            letter-spacing: -0.04em;
        }

        .truthlens-subtitle {
            margin: 0.45rem 0 0;
            color: var(--tl-muted);
            font-size: 0.98rem;
            line-height: 1.65;
        }

        .truthlens-section {
            margin-top: 1.2rem;
        }

        .truthlens-section-title {
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
            margin-bottom: 1rem;
        }

        .truthlens-eyebrow {
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #6d7ee7;
        }

        .truthlens-heading {
            margin: 0;
            font-size: 1.6rem;
            letter-spacing: -0.03em;
        }

        .truthlens-copy {
            margin: 0;
            color: var(--tl-muted);
            line-height: 1.75;
        }

        .truthlens-card {
            border-radius: 24px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: var(--tl-panel-strong);
            box-shadow: 0 14px 34px rgba(15, 23, 42, 0.05);
            padding: 1.15rem;
        }

        .truthlens-card.soft-lavender { background: linear-gradient(180deg, rgba(237, 233, 254, 0.75), rgba(255,255,255,0.98)); }
        .truthlens-card.soft-blue { background: linear-gradient(180deg, rgba(219, 234, 254, 0.7), rgba(255,255,255,0.98)); }
        .truthlens-card.soft-teal { background: linear-gradient(180deg, rgba(217, 243, 239, 0.72), rgba(255,255,255,0.98)); }
        .truthlens-card.soft-red { background: linear-gradient(180deg, rgba(253, 232, 232, 0.7), rgba(255,255,255,0.98)); }
        .truthlens-card.soft-green { background: linear-gradient(180deg, rgba(230, 247, 234, 0.75), rgba(255,255,255,0.98)); }

        .truthlens-card-label {
            margin: 0;
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #64748b;
        }

        .truthlens-card-title {
            margin: 0.4rem 0 0;
            font-size: 1.1rem;
            letter-spacing: -0.02em;
        }

        .truthlens-card-copy {
            margin: 0.55rem 0 0;
            color: var(--tl-muted);
            line-height: 1.7;
            font-size: 0.95rem;
        }

        .truthlens-chip-soft {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            border-radius: 999px;
            padding: 0.34rem 0.72rem;
            border: 1px solid rgba(148, 163, 184, 0.16);
            background: rgba(255, 255, 255, 0.9);
            color: #475569;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .truthlens-step {
            position: relative;
            padding-top: 2.3rem;
        }

        .truthlens-step::before {
            counter-increment: step;
            content: counter(step);
            position: absolute;
            top: 0;
            left: 0;
            width: 2rem;
            height: 2rem;
            border-radius: 999px;
            display: grid;
            place-items: center;
            background: linear-gradient(135deg, rgba(139, 130, 246, 0.16), rgba(219, 234, 254, 0.95));
            color: #4f46e5;
            font-weight: 800;
        }

        .truthlens-result {
            border-radius: 28px;
            border: 1px solid rgba(148, 163, 184, 0.16);
            padding: 1.35rem;
            box-shadow: 0 16px 42px rgba(15, 23, 42, 0.06);
        }

        .truthlens-result.fake {
            background: linear-gradient(180deg, rgba(253, 232, 232, 0.9), rgba(255,255,255,0.98));
        }

        .truthlens-result.real {
            background: linear-gradient(180deg, rgba(230, 247, 234, 0.92), rgba(255,255,255,0.98));
        }

        .truthlens-result-header {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            align-items: start;
        }

        .truthlens-result-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.34rem 0.72rem;
            border-radius: 999px;
            font-size: 0.77rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .truthlens-result-badge.fake {
            background: rgba(252, 165, 165, 0.22);
            color: #b91c1c;
        }

        .truthlens-result-badge.real {
            background: rgba(167, 243, 208, 0.3);
            color: #047857;
        }

        .truthlens-result-title {
            margin: 0.55rem 0 0;
            font-size: 1.65rem;
            letter-spacing: -0.03em;
        }

        .truthlens-progress {
            margin-top: 1rem;
            height: 0.7rem;
            border-radius: 999px;
            overflow: hidden;
            background: rgba(148, 163, 184, 0.16);
        }

        .truthlens-progress > span {
            display: block;
            height: 100%;
            border-radius: inherit;
            transition: width 700ms ease;
        }

        .truthlens-progress.fake > span {
            background: linear-gradient(90deg, rgba(248, 113, 113, 0.78), rgba(251, 146, 60, 0.72));
        }

        .truthlens-progress.real > span {
            background: linear-gradient(90deg, rgba(52, 211, 153, 0.84), rgba(110, 231, 183, 0.72));
        }

        .truthlens-footer {
            margin-top: 2rem;
            padding: 1.2rem 1.4rem;
            border-radius: 24px;
            border: 1px solid rgba(148, 163, 184, 0.14);
            background: rgba(255, 255, 255, 0.82);
            color: var(--tl-muted);
            box-shadow: 0 12px 34px rgba(15, 23, 42, 0.04);
        }

        .truthlens-workflow {
            display: grid;
            gap: 0.55rem;
            font-weight: 600;
            color: #334155;
        }

        .truthlens-workflow .arrow {
            color: #a5b4fc;
            font-weight: 900;
        }

        .truthlens-scroll-note {
            color: var(--tl-muted);
            font-size: 0.9rem;
        }

        @media (max-width: 1100px) {
            .truthlens-grid-2,
            .truthlens-grid-3,
            .truthlens-grid-4 {
                grid-template-columns: 1fr 1fr !important;
            }
        }

        @media (max-width: 700px) {
            .truthlens-title {
                font-size: 1.75rem;
            }

            .truthlens-grid-2,
            .truthlens-grid-3,
            .truthlens-grid-4 {
                grid-template-columns: 1fr !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header(status: DeploymentStatus) -> None:
    """Render the branded top section and page navigation."""
    with st.container(border=True):
        left, right = st.columns([1.15, 1.85], vertical_alignment="center")
        with left:
            st.markdown(
                """
                <div>
                    <div class="truthlens-badge">TruthLens AI</div>
                    <h1 class="truthlens-title">Fake News Detection</h1>
                    <p class="truthlens-subtitle">
                        A clean Streamlit experience for testing articles, viewing predictions, and
                        presenting the project like a polished AI product.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with right:
            nav_columns = st.columns(4)
            current_page = get_active_page()
            for column, page in zip(nav_columns, PAGES, strict=True):
                with column:
                    st.button(
                        page,
                        type="primary" if page == current_page else "secondary",
                        use_container_width=True,
                        on_click=set_active_page,
                        args=(page,),
                    )

        readiness = "All systems ready" if status.prediction_service_ready and status.backend.health_ok else "Needs attention"
        st.markdown(
            f'<div style="display:flex;justify-content:flex-end;margin-top:0.7rem;"><span class="truthlens-chip-soft">{readiness}</span></div>',
            unsafe_allow_html=True,
        )

    if status.error:
        st.warning("Some deployment checks reported a warning. The app remains usable.")

    st.write("")


def render_footer() -> None:
    """Render the shared project footer."""
    st.markdown(
        """
        <div class="truthlens-footer">
            <strong>TruthLens AI</strong> is an internship-style fake news detection project built
            as a polished AI product demo. It is intended for educational presentation, portfolio
            use, and lightweight deployment showcases.
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_dataset_frame() -> pd.DataFrame:
    """Build the static dataset distribution frame."""
    return pd.DataFrame(
        {
            "Label": ["Real News", "Fake News"],
            "Count": [DATASET_REAL_COUNT, DATASET_FAKE_COUNT],
        }
    )


def make_prediction_distribution_frame(history: list[dict[str, Any]]) -> pd.DataFrame:
    """Build the session history distribution frame."""
    real_count = sum(1 for item in history if normalize_label(item["prediction"]) == "real")
    fake_count = sum(1 for item in history if normalize_label(item["prediction"]) == "fake")
    return pd.DataFrame(
        {
            "Label": ["Real Predictions", "Fake Predictions"],
            "Count": [real_count, fake_count],
        }
    )


def render_chart_card(title: str, chart: alt.Chart, description: str) -> None:
    """Render a chart inside a clean card wrapper."""
    with st.container(border=True):
        st.markdown(
            f"""
            <p class="truthlens-card-label">Chart</p>
            <h4 class="truthlens-card-title">{title}</h4>
            <p class="truthlens-card-copy">{description}</p>
            """,
            unsafe_allow_html=True,
        )
        st.altair_chart(chart, use_container_width=True)


def render_home_page(status: DeploymentStatus) -> None:
    """Render the landing page with hero, feature cards, workflow, FAQ, and footer note."""
    st.markdown(
        """
        <div class="truthlens-hero" style="border-radius:30px;border:1px solid rgba(148,163,184,0.16);background:linear-gradient(180deg, rgba(255,255,255,0.95), rgba(250,250,255,0.96));box-shadow:0 24px 70px rgba(15, 23, 42, 0.06);padding:2rem;">
            <div style="display:grid;grid-template-columns:1.15fr 0.85fr;gap:1.4rem;align-items:stretch;">
                <div>
                    <span class="truthlens-badge">TruthLens AI</span>
                    <h2 style="margin:0.9rem 0 0.55rem;font-size:clamp(2.2rem,5vw,4.2rem);letter-spacing:-0.05em;line-height:1.02;color:#0f172a;">
                        Detect fake news with a clean, modern AI experience.
                    </h2>
                    <p class="truthlens-subtitle" style="max-width:44rem;font-size:1.03rem;">
                        TruthLens AI helps users paste an article, analyze the content, and review a
                        clear Fake or Real prediction with confidence feedback. The interface is
                        intentionally minimal, professional, and presentation-ready.
                    </p>
                    <div style="display:flex;gap:0.75rem;flex-wrap:wrap;margin-top:1.4rem;">
                        <div class="truthlens-chip-soft">Light theme only</div>
                        <div class="truthlens-chip-soft">Student portfolio friendly</div>
                        <div class="truthlens-chip-soft">ML-powered classification</div>
                    </div>
                    <div style="display:flex;gap:0.75rem;flex-wrap:wrap;margin-top:1.4rem;">
                        <!-- Buttons rendered below -->
                    </div>
                </div>
                <div class="truthlens-card soft-lavender" style="padding:1.2rem;">
                    <p class="truthlens-card-label">Preview</p>
                    <h3 class="truthlens-card-title" style="font-size:1.45rem;">What the product feels like</h3>
                    <p class="truthlens-card-copy">
                        A polished article analysis flow with a soft prediction card, confidence bar,
                        and session history that feels like a real AI product instead of a notebook demo.
                    </p>
                    <div style="margin-top:1rem;border-radius:22px;background:#fff;padding:1rem;border:1px solid rgba(148,163,184,0.14);">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;">
                            <div>
                                <div class="truthlens-result-badge fake">Fake News</div>
                                <h4 style="margin:0.75rem 0 0;font-size:1.35rem;letter-spacing:-0.03em;">Confidence-based prediction</h4>
                            </div>
                            <div style="font-size:0.88rem;color:#64748b;font-weight:700;">Soft visual design</div>
                        </div>
                        <div class="truthlens-progress fake" style="margin-top:1rem;"><span style="width:88%;"></span></div>
                        <p style="margin:0.7rem 0 0;color:#475569;font-size:0.95rem;">Prediction confidence shown in a calm, readable format.</p>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cta1, cta2, spacer = st.columns([0.22, 0.22, 0.56])
    with cta1:
        st.button("Start Analyzing", type="primary", use_container_width=True, on_click=set_active_page, args=(PAGE_ANALYZER,))
    with cta2:
        st.button("View Dashboard", use_container_width=True, on_click=set_active_page, args=(PAGE_DASHBOARD,))

    st.write("")
    st.markdown(
        """
        <div class="truthlens-section">
            <div class="truthlens-section-title">
                <span class="truthlens-eyebrow">Features</span>
                <h3 class="truthlens-heading">A focused product experience</h3>
                <p class="truthlens-copy">The UI is built to feel clean, credible, and internship-presentable while keeping the core experience simple.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    feature_data = [
        ("Instant News Analysis", "Paste an article and receive a fast Fake or Real verdict with a polished result card.", "soft-lavender"),
        ("Machine Learning Powered", "Uses the existing TF-IDF and Logistic Regression pipeline without retraining or changing model logic.", "soft-blue"),
        ("Confidence-Based Predictions", "The result emphasizes confidence percentages so the output feels clear and readable.", "soft-teal"),
        ("Real-Time Results", "The interface updates immediately after analysis and stores the outcome in session history.", "soft-green"),
    ]
    feature_columns = st.columns(4)
    for column, (title, copy, accent) in zip(feature_columns, feature_data, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="truthlens-card {accent}">
                    <p class="truthlens-card-label">Feature</p>
                    <h4 class="truthlens-card-title">{title}</h4>
                    <p class="truthlens-card-copy">{copy}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown(
        """
        <div class="truthlens-section">
            <div class="truthlens-section-title">
                <span class="truthlens-eyebrow">How It Works</span>
                <h3 class="truthlens-heading">Three simple steps</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    steps = [
        ("Paste Article", "Copy or write a news story into the analyzer."),
        ("Analyze News", "The trained text classifier processes the content."),
        ("View Prediction", "Review the label, confidence, and status message."),
    ]
    st.markdown('<div style="counter-reset: step;"></div>', unsafe_allow_html=True)
    step_columns = st.columns(3)
    for column, (title, copy) in zip(step_columns, steps, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="truthlens-card">
                    <div class="truthlens-step">
                        <h4 class="truthlens-card-title" style="margin-top:0;">{title}</h4>
                        <p class="truthlens-card-copy">{copy}</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.markdown(
        """
        <div class="truthlens-section">
            <div class="truthlens-section-title">
                <span class="truthlens-eyebrow">FAQ</span>
                <h3 class="truthlens-heading">Common questions</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    faq_items = [
        ("What is TruthLens AI?", "A fake news detection platform that lets users analyze articles and view a machine-learning-based prediction in a clean interface."),
        ("How does it work?", "The app converts news text into TF-IDF features and passes them through the existing Logistic Regression classifier."),
        ("Can predictions be fully trusted?", "No model is perfect, so the output should be treated as a helpful signal rather than an absolute truth."),
        ("What technologies are used?", "Python, Streamlit, FastAPI, Scikit-Learn, Pandas, and NumPy power the product experience."),
    ]
    faq_cols = st.columns(2)
    for index, (question, answer) in enumerate(faq_items):
        with faq_cols[index % 2]:
            with st.container(border=True):
                st.markdown(
                    f"""
                    <p class="truthlens-card-label">FAQ</p>
                    <h4 class="truthlens-card-title">{question}</h4>
                    <p class="truthlens-card-copy">{answer}</p>
                    """,
                    unsafe_allow_html=True,
                )

    st.write("")
    footer_cols = st.columns([1.4, 0.6])
    with footer_cols[0]:
        st.markdown(
            """
            <div class="truthlens-footer">
                <strong>Project information</strong><br>
                TruthLens AI is a fake news detection platform built for an internship portfolio and
                polished to look and feel like a real AI product.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with footer_cols[1]:
        st.markdown(
            """
            <div class="truthlens-footer">
                <strong>Internship note</strong><br>
                Designed to demonstrate product thinking, UI polish, and practical ML deployment.
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_prediction_result_card(prediction: str, confidence: float) -> None:
    """Render the colored prediction card for the analyzer page."""
    normalized = normalize_label(prediction)
    label = "Fake News" if normalized == "fake" else "Real News"
    status_text = (
        "The article looks likely to be misleading based on the current model."
        if normalized == "fake"
        else "The article appears credible based on the current model."
    )
    card_class = "fake" if normalized == "fake" else "real"
    progress_value = max(0.0, min(float(confidence), 100.0))

    st.markdown(
        f"""
        <div class="truthlens-result {card_class}">
            <div class="truthlens-result-header">
                <div>
                    <div class="truthlens-result-badge {card_class}">{label}</div>
                    <h3 class="truthlens-result-title">{label}</h3>
                </div>
                <div style="text-align:right;">
                    <div class="truthlens-card-label">Confidence</div>
                    <div style="font-size:1.6rem;font-weight:800;letter-spacing:-0.03em;color:#0f172a;">
                        {progress_value:.2f}%
                    </div>
                </div>
            </div>
            <p class="truthlens-card-copy" style="margin-top:0.9rem;">{status_text}</p>
            <div class="truthlens-progress {card_class}">
                <span style="width:{progress_value:.2f}%;"></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_analyzer_page(status: DeploymentStatus) -> None:
    """Render the main prediction surface."""
    left_column, right_column = st.columns([1.15, 0.85], vertical_alignment="top")

    with left_column:
        st.markdown(
            """
            <div class="truthlens-section">
                <div class="truthlens-section-title">
                    <span class="truthlens-eyebrow">News Analyzer</span>
                    <h3 class="truthlens-heading">Paste an article and analyze it instantly</h3>
                    <p class="truthlens-copy">
                        The analyzer keeps the interface spacious and calm so the result feels like a
                        real product interaction instead of a technical demo.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            text_value = st.text_area(
                "Article text",
                placeholder="Paste a news article, social post, headline thread, or article excerpt here...",
                height=280,
                label_visibility="collapsed",
                max_chars=MAX_INPUT_CHARS,
                key="truthlens_article_input",
            )
            st.caption(f"{len(text_value or ''):,}/{MAX_INPUT_CHARS:,} characters")

            analyze_pressed = st.button("Analyze News", type="primary", use_container_width=True)
            if analyze_pressed:
                if not text_value.strip():
                    st.error("Please paste some news text before analyzing.")
                elif not status.prediction_service_ready:
                    st.error(status.error or "Prediction service is not ready yet.")
                else:
                    try:
                        with st.spinner("Analyzing news article..."):
                            service = load_prediction_service()
                            result = service.predict(text_value)
                        add_prediction_to_history(text_value, result)
                        st.session_state.truthlens_last_error = None
                        st.success("Prediction complete.")
                    except Exception as exc:  # noqa: BLE001
                        st.session_state.truthlens_last_error = str(exc)
                        st.error(f"Unable to analyze the text: {exc}")

        latest_result = st.session_state.truthlens_latest_result
        if latest_result is not None:
            st.write("")
            render_prediction_result_card(
                prediction=latest_result["prediction"],
                confidence=float(latest_result["confidence"]),
            )
        else:
            st.write("")
            with st.container(border=True):
                st.markdown(
                    """
                    <p class="truthlens-card-label">Prediction</p>
                    <h4 class="truthlens-card-title">Your result will appear here</h4>
                    <p class="truthlens-card-copy">
                        After you press Analyze News, the app will display a prediction card with
                        the model label, confidence percentage, and a short status message.
                    </p>
                    """,
                    unsafe_allow_html=True,
                )

    with right_column:
        st.markdown(
            """
            <div class="truthlens-section">
                <div class="truthlens-section-title">
                    <span class="truthlens-eyebrow">Live View</span>
                    <h3 class="truthlens-heading">Response summary</h3>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            st.markdown(
                """
                <p class="truthlens-card-label">Input guidance</p>
                <h4 class="truthlens-card-title">What works best</h4>
                <p class="truthlens-card-copy">
                    Longer article excerpts, body text, or multi-sentence news content usually give
                    the classifier a more useful signal than a single headline.
                </p>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        with st.container(border=True):
            st.markdown(
                """
                <p class="truthlens-card-label">Status Message</p>
                <h4 class="truthlens-card-title">Model is ready to respond</h4>
                <p class="truthlens-card-copy">
                    The current runtime uses the existing prediction service and reads the trained
                    vectorizer and classifier from the repository artifacts.
                </p>
                """,
                unsafe_allow_html=True,
            )

        st.write("")
        with st.container(border=True):
            st.markdown(
                """
                <p class="truthlens-card-label">Current Runtime</p>
                <h4 class="truthlens-card-title">Deployment notes</h4>
                <p class="truthlens-card-copy">
                    The app is designed to feel product-like while still showing the essential
                    runtime checks for the model, backend, and frontend.
                </p>
                """,
                unsafe_allow_html=True,
            )

        if st.session_state.truthlens_last_error:
            st.write("")
            st.error(st.session_state.truthlens_last_error)


def render_dashboard_page(status: DeploymentStatus) -> None:
    """Render dataset analytics and session prediction history."""
    history = list(st.session_state.truthlens_history)
    frame = history_to_frame(history)
    total_predictions = len(history)
    real_predictions = sum(1 for item in history if normalize_label(item["prediction"]) == "real")
    fake_predictions = sum(1 for item in history if normalize_label(item["prediction"]) == "fake")
    average_confidence = (
        sum(float(item["confidence"]) for item in history) / total_predictions if total_predictions else 0.0
    )

    st.markdown(
        """
        <div class="truthlens-section">
            <div class="truthlens-section-title">
                <span class="truthlens-eyebrow">Dashboard</span>
                <h3 class="truthlens-heading">Project insights and session analytics</h3>
                <p class="truthlens-copy">
                    This dashboard combines the static dataset story with local prediction history so
                    the app feels more like a real product than a one-off demo.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stat_columns = st.columns(4)
    dashboard_cards = [
        ("Total Predictions", str(total_predictions)),
        ("Real Predictions", str(real_predictions)),
        ("Fake Predictions", str(fake_predictions)),
        ("Average Confidence", f"{average_confidence:.2f}%"),
    ]
    for column, (label, value) in zip(stat_columns, dashboard_cards, strict=True):
        with column:
            st.metric(label, value)

    st.write("")
    section_a, section_b = st.columns([1.05, 0.95], vertical_alignment="top")

    with section_a:
        st.markdown(
            """
            <div class="truthlens-section">
                <div class="truthlens-section-title">
                    <span class="truthlens-eyebrow">Section A</span>
                    <h3 class="truthlens-heading">Dataset distribution</h3>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        dataset_frame = make_dataset_frame()
        pie_chart = (
            alt.Chart(dataset_frame)
            .mark_arc(innerRadius=62, cornerRadius=6)
            .encode(
                theta=alt.Theta("Count:Q"),
                color=alt.Color(
                    "Label:N",
                    scale=alt.Scale(range=["#8b82f6", "#a7f3d0"]),
                    legend=alt.Legend(title=""),
                ),
                tooltip=["Label:N", "Count:Q"],
            )
            .properties(height=260)
        )
        bar_chart = (
            alt.Chart(dataset_frame)
            .mark_bar(cornerRadiusTopLeft=8, cornerRadiusTopRight=8)
            .encode(
                x=alt.X("Label:N", axis=alt.Axis(title="")),
                y=alt.Y("Count:Q", axis=alt.Axis(title="Articles")),
                color=alt.Color(
                    "Label:N",
                    scale=alt.Scale(range=["#c4b5fd", "#bae6fd"]),
                    legend=None,
                ),
                tooltip=["Label:N", "Count:Q"],
            )
            .properties(height=260)
        )
        render_chart_card(
            "Interactive Pie Chart",
            pie_chart,
            "Hover the slices to inspect the static dataset distribution used to train the classifier.",
        )
        st.write("")
        render_chart_card(
            "Interactive Bar Chart",
            bar_chart,
            "A simple bar chart gives a clean visual comparison between real and fake article counts.",
        )

    with section_b:
        st.markdown(
            """
            <div class="truthlens-section">
                <div class="truthlens-section-title">
                    <span class="truthlens-eyebrow">Section B</span>
                    <h3 class="truthlens-heading">Prediction history</h3>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        distribution_frame = make_prediction_distribution_frame(history)
        doughnut_chart = (
            alt.Chart(distribution_frame)
            .mark_arc(innerRadius=72, cornerRadius=5)
            .encode(
                theta=alt.Theta("Count:Q"),
                color=alt.Color(
                    "Label:N",
                    scale=alt.Scale(range=["#86efac", "#fda4af"]),
                    legend=alt.Legend(title=""),
                ),
                tooltip=["Label:N", "Count:Q"],
            )
            .properties(height=220)
        )
        render_chart_card(
            "Doughnut Chart",
            doughnut_chart,
            "Session history is stored locally for the current browser session only.",
        )

        if frame.empty:
            trend_source = pd.DataFrame({"Index": [1], "Confidence": [0.0], "Prediction": ["None"]})
        else:
            trend_source = frame.reset_index(drop=True).reset_index(names="Index")
        trend_chart = (
            alt.Chart(trend_source)
            .mark_line(point=True)
            .encode(
                x=alt.X("Index:Q", axis=alt.Axis(title="")),
                y=alt.Y("Confidence:Q", axis=alt.Axis(title="Confidence %")),
                color=alt.Color("Prediction:N", scale=alt.Scale(range=["#8b82f6", "#6ee7b7"]), legend=None),
                tooltip=["Created:N", "Prediction:N", "Confidence:Q"],
            )
            .properties(height=180)
        )
        st.write("")
        render_chart_card(
            "Small Trend Chart",
            trend_chart,
            "A compact view of recent confidence values keeps the dashboard feeling alive without adding research metrics.",
        )

        st.write("")
        with st.container(border=True):
            st.markdown(
                """
                <p class="truthlens-card-label">Recent Predictions</p>
                <h4 class="truthlens-card-title">Latest local history</h4>
                """,
                unsafe_allow_html=True,
            )
            if frame.empty:
                st.info("No predictions yet. Use the News Analyzer page to add the first entry.")
            else:
                table_frame = frame[["Created", "Prediction", "Confidence", "Text"]].copy()
                table_frame["Confidence"] = table_frame["Confidence"].map(lambda value: f"{value:.2f}%")
                st.dataframe(table_frame.head(6), use_container_width=True, hide_index=True)

    st.write("")
    st.markdown(
        """
        <div class="truthlens-section">
            <div class="truthlens-section-title">
                <span class="truthlens-eyebrow">Section C</span>
                <h3 class="truthlens-heading">Project information cards</h3>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    info_data = [
        ("Dataset Size", f"{DATASET_TOTAL:,} labeled articles"),
        ("Model Type", "TF-IDF + Logistic Regression"),
        ("Vectorizer", "Scikit-Learn TF-IDF"),
        ("Deployment Platform", "Streamlit Community Cloud"),
    ]
    info_columns = st.columns(4)
    for column, (title, value) in zip(info_columns, info_data, strict=True):
        with column:
            st.markdown(
                f"""
                <div class="truthlens-card soft-blue">
                    <p class="truthlens-card-label">Project Info</p>
                    <h4 class="truthlens-card-title">{title}</h4>
                    <p class="truthlens-card-copy">{value}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    with st.container(border=True):
        st.markdown(
            """
            <p class="truthlens-card-label">Session Notes</p>
            <h4 class="truthlens-card-title">Prediction history is stored in memory for this browser session</h4>
            <p class="truthlens-card-copy">
                If you want to present the project, use the analyzer a few times and then return
                here to show the charts and recent results table.
            </p>
            """,
            unsafe_allow_html=True,
        )
        if status.backend.error:
            st.warning(status.backend.error)


def render_about_page(status: DeploymentStatus) -> None:
    """Render the project overview and workflow explanation."""
    st.markdown(
        """
        <div class="truthlens-section">
            <div class="truthlens-section-title">
                <span class="truthlens-eyebrow">About</span>
                <h3 class="truthlens-heading">A polished fake news detection product</h3>
                <p class="truthlens-copy">
                    TruthLens AI combines a practical binary classification pipeline with a refined
                    user interface that feels credible during internship presentations and demos.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left_column, right_column = st.columns([1.2, 0.8], vertical_alignment="top")
    with left_column:
        with st.container(border=True):
            st.markdown(
                """
                <p class="truthlens-card-label">Project Overview</p>
                <h4 class="truthlens-card-title">Why this project exists</h4>
                <p class="truthlens-card-copy">
                    Fake news spreads quickly and can influence public opinion, so a lightweight
                    detection tool helps demonstrate how machine learning can support credibility
                    checking in a practical and approachable way.
                </p>
                """,
                unsafe_allow_html=True,
            )

    with right_column:
        with st.container(border=True):
            st.markdown(
                """
                <p class="truthlens-card-label">Project Owner</p>
                <h4 class="truthlens-card-title">Internship presentation project</h4>
                <p class="truthlens-card-copy">
                    Built as a student-friendly showcase for full-stack AI delivery, UI polish, and
                    responsible deployment.
                </p>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    tech_column, workflow_column = st.columns([0.95, 1.05], vertical_alignment="top")
    with tech_column:
        with st.container(border=True):
            st.markdown(
                """
                <p class="truthlens-card-label">Technology Stack</p>
                <h4 class="truthlens-card-title">Core tools used in the app</h4>
                """,
                unsafe_allow_html=True,
            )
            tech_stack = ["Python", "Streamlit", "Scikit-Learn", "Pandas", "NumPy"]
            st.markdown(
                "".join(
                    f'<span class="truthlens-chip-soft" style="margin:0.35rem 0.35rem 0 0;display:inline-flex;">{item}</span>'
                    for item in tech_stack
                ),
                unsafe_allow_html=True,
            )

    with workflow_column:
        with st.container(border=True):
            st.markdown(
                """
                <p class="truthlens-card-label">Workflow Visualization</p>
                <h4 class="truthlens-card-title">How the prediction pipeline flows</h4>
                <div class="truthlens-workflow" style="margin-top:0.8rem;">
                    <span>News Text</span>
                    <span class="arrow">&darr;</span>
                    <span>Text Cleaning</span>
                    <span class="arrow">&darr;</span>
                    <span>TF-IDF Vectorization</span>
                    <span class="arrow">&darr;</span>
                    <span>Logistic Regression</span>
                    <span class="arrow">&darr;</span>
                    <span>Prediction</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    with st.container(border=True):
        st.markdown(
            """
            <p class="truthlens-card-label">Project Motivation</p>
            <h4 class="truthlens-card-title">Why fake news detection matters</h4>
            <p class="truthlens-card-copy">
                Misinformation can influence decisions, reduce trust, and spread quickly across
                platforms. A clear, easy-to-demo detection interface helps explain how machine
                learning can support better content screening and responsible information sharing.
            </p>
            """,
            unsafe_allow_html=True,
        )
        st.info(
            "This Streamlit app uses the existing PredictionService and cached model artifacts. It does not retrain the model or change the ML pipeline."
        )

    st.write("")
    with st.container(border=True):
        st.markdown(
            """
            <p class="truthlens-card-label">Deployment Snapshot</p>
            <h4 class="truthlens-card-title">Runtime checks</h4>
            """,
            unsafe_allow_html=True,
        )
        cols = st.columns(3)
        items = [
            ("Model Version", status.model_version),
            ("Backend Health", render_bool(status.backend.health_ok)),
            ("Frontend Reachability", render_bool(status.frontend.reachable)),
        ]
        for column, (label, value) in zip(cols, items, strict=True):
            with column:
                st.metric(label, value)


def render_page(status: DeploymentStatus) -> None:
    """Dispatch to the selected page."""
    current_page = get_active_page()
    if current_page == PAGE_HOME:
        render_home_page(status)
    elif current_page == PAGE_ANALYZER:
        render_analyzer_page(status)
    elif current_page == PAGE_DASHBOARD:
        render_dashboard_page(status)
    else:
        render_about_page(status)


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(page_title="TruthLens AI", page_icon="TL", layout="wide")
    configure_logging()
    initialize_session_state()
    apply_custom_styles()
    status = load_deployment_status()
    render_header(status)
    render_page(status)
    render_footer()


if __name__ == "__main__":
    main()
