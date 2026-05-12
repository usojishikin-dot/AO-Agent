# app/core/security.py
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.organization_repository import OrganizationRepository
from app.db.models import Organization


async def verify_bearer_token(
    authorization: str | None = Header(default=None),
    session: AsyncSession = Depends(get_db_session)
) -> Organization:
    """
    Dependency that validates a per-organization API key (Bearer token).
    Returns the Organization object if valid, else raises 401.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Use 'Bearer <token>'",
        )

    token = authorization.replace("Bearer ", "")
    repo = OrganizationRepository(session)
    org = await repo.get_by_webhook_token(token)

    if not org:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or unknown API key",
        )

    return org