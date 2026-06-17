from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================================
# PROJECT PATHS
# ============================================================================

# Move up from:
# apps/api/app/core/config.py
# to project root
PROJECT_ROOT = Path(__file__).resolve().parents[4]

DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = DATA_DIR / "models"


class Settings(BaseSettings):
    project_name: str = "TruthLens AI API"

    project_root: Path = PROJECT_ROOT
    data_dir: Path = DATA_DIR
    model_dir: Path = MODEL_DIR

    database_url: str = (
        f"sqlite:///{(PROJECT_ROOT / 'truthlens.db').as_posix()}"
    )

    tfidf_vectorizer_path: Path = (
        MODEL_DIR / "tfidf_vectorizer.pkl"
    )

    logistic_regression_model_path: Path = (
        MODEL_DIR / "logistic_regression_model.pkl"
    )

    cors_allow_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()