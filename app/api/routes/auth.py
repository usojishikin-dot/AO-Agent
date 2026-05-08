from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.db.session import get_db_session
from app.db.models import User
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(tags=["auth"], prefix="/auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str | None = None

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    id: int
    email: str
    name: str | None
    status: str

@router.post("/register", response_model=AuthResponse)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db_session),
):
    stmt = select(User).where(User.email == payload.email)
    existing_user = (await session.execute(stmt)).scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(payload.password)
    
    new_user = User(
        email=payload.email,
        hashed_password=hashed_password,
        name=payload.name,
        auth_provider="email"
    )
    
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return AuthResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        status="success"
    )

@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
):
    stmt = select(User).where(User.email == payload.email)
    user = (await session.execute(stmt)).scalar_one_or_none()
    
    if not user or not user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    if not pwd_context.verify(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    return AuthResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        status="success"
    )
