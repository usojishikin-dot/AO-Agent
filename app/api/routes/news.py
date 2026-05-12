# app/api/routes/news.py
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_bearer_token
from app.db.session import get_db_session
from app.repositories.news_repository import NewsRepository
from app.schemas.news import NewsTriggerRequest, NewsItemResponse
from app.schemas.responses import IngestionResponse
from app.services.ingestion_service import IngestionService

router = APIRouter(tags=["news"])


@router.post(
    "/news-trigger",
    response_model=IngestionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(verify_bearer_token)],
)
async def news_trigger(
    payload: NewsTriggerRequest,
    session: AsyncSession = Depends(get_db_session),
) -> IngestionResponse:
    repo = NewsRepository(session)
    service = IngestionService(repo)
    result = await service.ingest(payload)
    return IngestionResponse(**result)


@router.get(
    "/news-items",
    response_model=list[NewsItemResponse],
)
async def list_news_items(
    session: AsyncSession = Depends(get_db_session),
) -> list[NewsItemResponse]:
    repo = NewsRepository(session)
    items = await repo.list_news_items()

    return [
        NewsItemResponse(
            id=item.id,
            external_id=item.external_id,
            title=item.title,
            content=item.content,
            source_url=item.source_url,
            image_url=item.image_url,
            status=item.status,
            master_outline=item.master_outline,
            trace_id=item.trace_id,
        )
        for item in items
    ]


@router.get(
    "/news-items/{news_item_id}",
    response_model=NewsItemResponse,
)
async def get_news_item(
    news_item_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> NewsItemResponse:
    repo = NewsRepository(session)
    item = await repo.get_by_id(news_item_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="News item not found")

    return NewsItemResponse(
        id=item.id,
        external_id=item.external_id,
        title=item.title,
        content=item.content,
        source_url=item.source_url,
        image_url=item.image_url,
        status=item.status,
        master_outline=item.master_outline,
        trace_id=item.trace_id,
    )