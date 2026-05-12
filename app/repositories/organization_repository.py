from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Organization

class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_webhook_token(self, token: str) -> Organization | None:
        stmt = select(Organization).where(Organization.webhook_token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, org_id: int) -> Organization | None:
        stmt = select(Organization).where(Organization.id == org_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_organization(self, name: str, webhook_token: str, website_url: str | None = None) -> Organization:
        org = Organization(
            name=name,
            webhook_token=webhook_token,
            website_url=website_url
        )
        self.session.add(org)
        await self.session.commit()
        await self.session.refresh(org)
        return org
