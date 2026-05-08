from app.repositories.content_version_repository import ContentVersionRepository


class ContentVersionService:
    def __init__(self, repo: ContentVersionRepository) -> None:
        self.repo = repo

    async def create_new_version(
        self,
        *,
        news_item_id: int,
        platform: str,
        content_text: str,
    ):
        latest_version = await self.repo.get_latest_version_number(
            news_item_id=news_item_id,
            platform=platform,
        )

        next_version = latest_version + 1

        return await self.repo.create_content_version(
            news_item_id=news_item_id,
            platform=platform,
            version_number=next_version,
            content_text=content_text,
            status="GENERATED",
        )