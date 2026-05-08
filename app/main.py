from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.news import router as news_router
from app.api.routes.content_versions import router as content_versions_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging(settings.log_level)

app = FastAPI(title="Enterprise AI Social Media Factory")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news_router)
app.include_router(content_versions_router)
app.include_router(health_router)