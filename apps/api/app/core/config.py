from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BASE_DIR / "app" / "ml" / "models"


class Settings(BaseSettings):
    project_name: str = "TruthLens AI API"
    database_url: str = f"sqlite:///{(BASE_DIR / 'truthlens.db').as_posix()}"
    tfidf_vectorizer_path: Path = MODEL_DIR / "tfidf_vectorizer.pkl"
    logistic_regression_model_path: Path = MODEL_DIR / "logistic_regression_model.pkl"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
