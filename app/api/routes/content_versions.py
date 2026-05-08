from fastapi import APIRouter, Depends, status, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.content_version_repository import ContentVersionRepository
from app.schemas.content_version import (
    ContentVersionResponse,
    CreateContentVersionRequest,
)
from app.services.content_version_service import ContentVersionService
from app.services.publishing_service import publish_content_version

router = APIRouter(tags=["content_versions"])


@router.post(
    "/content-versions/test",
    response_model=ContentVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_content_version_test(
    payload: CreateContentVersionRequest,
    session: AsyncSession = Depends(get_db_session),
) -> ContentVersionResponse:
    repo = ContentVersionRepository(session)
    service = ContentVersionService(repo)

    item = await service.create_new_version(
        news_item_id=payload.news_item_id,
        platform=payload.platform,
        content_text=payload.content_text,
    )

    return ContentVersionResponse(
        id=item.id,
        news_item_id=item.news_item_id,
        platform=item.platform,
        version_number=item.version_number,
        content_text=item.content_text,
        status=item.status,
    )


@router.post(
    "/content-versions/{cv_id}/approve",
    status_code=status.HTTP_202_ACCEPTED,
)
async def approve_and_publish_content_version(
    cv_id: int,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Marks a content version as approved by a human and triggers publishing to Ayrshare.
    """
    repo = ContentVersionRepository(session)
    cv = await repo.get_by_id(cv_id)
    
    if not cv:
        raise HTTPException(status_code=404, detail="Content version not found")
        
    if cv.approved_by_human:
        raise HTTPException(status_code=400, detail="Content already approved")
        
    success = await repo.mark_approved(cv_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to mark as approved")
        
    # Trigger publishing in background
    background_tasks.add_task(publish_content_version, cv_id)
    
    return {"status": "accepted", "message": "Content approved and publishing initiated"}


@router.get(
    "/news-items/{news_item_id}/versions",
    response_model=list[ContentVersionResponse],
)
async def list_versions_for_news_item(
    news_item_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> list[ContentVersionResponse]:
    """
    Returns all generated versions for a specific news item.
    """
    repo = ContentVersionRepository(session)
    items = await repo.list_by_news_item(news_item_id)

    return [
        ContentVersionResponse(
            id=item.id,
            news_item_id=item.news_item_id,
            platform=item.platform,
            version_number=item.version_number,
            content_text=item.content_text,
            status=item.status,
            evaluation_score=item.evaluation_score,
            brand_score=item.brand_score,
            human_likeness_score=item.human_likeness_score,
            platform_compliance_score=item.platform_compliance_score,
            evaluation_feedback=item.evaluation_feedback,
            approved_by_human=item.approved_by_human,
            ayrshare_post_id=item.ayrshare_post_id,
            published_at=item.published_at,
        )
        for item in items
    ]