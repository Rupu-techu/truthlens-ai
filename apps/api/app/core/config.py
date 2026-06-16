from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def find_project_root(start_path: Path | None = None) -> Path:
    """Find the repository root by walking upward from this file.

    We look for the directory that contains both `apps` and `data`, which makes
    the result independent of the current working directory.
    """
    current_path = (start_path or Path(__file__)).resolve()
    for candidate in (current_path, *current_path.parents):
        if (candidate / "apps").is_dir() and (candidate / "data").is_dir():
            return candidate

    raise RuntimeError(
        f"Unable to locate the project root starting from {current_path}. "
        "Expected to find a directory containing both 'apps' and 'data'."
    )


PROJECT_ROOT = find_project_root()
MODEL_DIR = PROJECT_ROOT / "data" / "models"


class Settings(BaseSettings):
    project_name: str = "TruthLens AI API"
    project_root: Path = PROJECT_ROOT
    model_dir: Path = MODEL_DIR
    database_url: str = f"sqlite:///{(PROJECT_ROOT / 'truthlens.db').as_posix()}"
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
