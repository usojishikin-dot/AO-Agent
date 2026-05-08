# app/core/security.py
from fastapi import Header, HTTPException, status

from app.core.config import settings


async def verify_bearer_token(authorization: str | None = Header(default=None)) -> None:
    print("AUTH HEADER RECEIVED:", repr(authorization))
    print("EXPECTED TOKEN:", repr(f"Bearer {settings.webhook_bearer_token}"))

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    expected = f"Bearer {settings.webhook_bearer_token}"
    if authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bearer token",
        )