# app/db/models.py
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    website_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    webhook_token: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    
    # Identity Map (stored as JSON/Text)
    mission_statement: Mapped[str | None] = mapped_column(Text, nullable=True)
    core_pillars: Mapped[str | None] = mapped_column(Text, nullable=True) # JSON list of pillars
    voice_parameters: Mapped[str | None] = mapped_column(Text, nullable=True) # JSON object
    gatekeeper_rules: Mapped[str | None] = mapped_column(Text, nullable=True) # JSON instructions
    
    # Branding
    brand_bible: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    
    users: Mapped[list["User"]] = relationship(back_populates="organization")
    news_items: Mapped[list["NewsItem"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="editor", nullable=False) # admin, editor, viewer
    auth_provider: Mapped[str] = mapped_column(String(50), default="email", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    organization: Mapped["Organization | None"] = relationship(back_populates="users")


class NewsItem(Base):
    __tablename__ = "news_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int | None] = mapped_column(ForeignKey("organizations.id"), nullable=True)
    
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="RECEIVED")
    master_outline: Mapped[str | None] = mapped_column(Text, nullable=True)
    trace_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    organization: Mapped["Organization | None"] = relationship(back_populates="news_items")
    content_versions: Mapped[list["ContentVersion"]] = relationship(
        back_populates="news_item",
        cascade="all, delete-orphan"
    )


class ContentVersion(Base):
    __tablename__ = "content_versions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    news_item_id: Mapped[int] = mapped_column(ForeignKey("news_items.id"), nullable=False, index=True)

    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="GENERATED")

    evaluation_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    brand_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    human_likeness_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    platform_compliance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    evaluation_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    approved_by_human: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    ayrshare_post_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    news_item: Mapped["NewsItem"] = relationship(back_populates="content_versions")