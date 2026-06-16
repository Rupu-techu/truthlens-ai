from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.project_name)
app.include_router(api_router)
