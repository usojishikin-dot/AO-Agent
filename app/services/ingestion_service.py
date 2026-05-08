# app/services/ingestion_service.py
from uuid import uuid4

from app.core.logging import get_logger
from app.repositories.news_repository import NewsRepository
from app.schemas.news import NewsTriggerRequest
from app.services.pipeline_service import start_pipeline_task

logger = get_logger(__name__)


class IngestionService:
    def __init__(self, repo: NewsRepository) -> None:
        self.repo = repo

    async def ingest(self, payload: NewsTriggerRequest) -> dict:
        existing = await self.repo.get_by_external_id(payload.external_id)

        if existing:
            logger.info(
                "Duplicate external_id received",
                extra={
                    "trace_id": existing.trace_id,
                    "stage": "ingestion",
                    "external_id": payload.external_id,
                    "decision": "IDEMPOTENT_SKIP",
                },
            )
            return {
                "status": "duplicate",
                "external_id": existing.external_id,
                "trace_id": existing.trace_id,
                "message": "News item already exists; duplicate ignored",
            }

        trace_id = str(uuid4())

        news_item = await self.repo.create_news_item(
            external_id=payload.external_id,
            title=payload.title,
            content=payload.content,
            source_url=str(payload.source_url) if payload.source_url else None,
            image_url=str(payload.image_url) if payload.image_url else None,
            trace_id=trace_id,
            status="RECEIVED",
        )

        logger.info(
            "News item accepted",
            extra={
                "trace_id": trace_id,
                "stage": "ingestion",
                "external_id": payload.external_id,
            },
        )

        start_pipeline_task(
            news_item_id=news_item.id,
            trace_id=trace_id,
            external_id=payload.external_id,
        )

        return {
            "status": "accepted",
            "external_id": payload.external_id,
            "trace_id": trace_id,
            "message": "News item accepted for processing",
        }