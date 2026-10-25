from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Title(Base):
    __tablename__ = "titles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    kind: Mapped[str] = mapped_column(String(16), default="movie")

    episodes: Mapped[list["Episode"]] = relationship(back_populates="title")


class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title_id: Mapped[int] = mapped_column(
        ForeignKey("titles.id", ondelete="CASCADE"), index=True
    )
    season: Mapped[int | None]
    number: Mapped[int | None]
    subtitle_lines: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    title: Mapped[Title] = relationship(back_populates="episodes")
    entries: Mapped[list["EpisodeLemma"]] = relationship(
        back_populates="episode", cascade="all, delete-orphan"
    )


class Lemma(Base):
    __tablename__ = "lemmas"
    __table_args__ = (UniqueConstraint("text", "pos", name="uq_lemma_text_pos"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(64), index=True)
    pos: Mapped[str] = mapped_column(String(8))
    zipf: Mapped[float] = mapped_column(Float, default=0.0)
    level: Mapped[str | None] = mapped_column(String(8))


class EpisodeLemma(Base):
    __tablename__ = "episode_lemmas"
    __table_args__ = (
        UniqueConstraint("episode_id", "lemma_id", name="uq_episode_lemma"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    episode_id: Mapped[int] = mapped_column(
        ForeignKey("episodes.id", ondelete="CASCADE"), index=True
    )
    lemma_id: Mapped[int] = mapped_column(ForeignKey("lemmas.id"), index=True)
    count: Mapped[int] = mapped_column(Integer)
    example: Mapped[str] = mapped_column(String(300), default="")

    episode: Mapped[Episode] = relationship(back_populates="entries")
    lemma: Mapped[Lemma] = relationship()

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class UserWord(Base):
    __tablename__ = "user_words"
    __table_args__ = (UniqueConstraint("user_id", "lemma_id", name="uq_user_lemma"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    lemma_id: Mapped[int] = mapped_column(ForeignKey("lemmas.id"), index=True)
    status: Mapped[str] = mapped_column(String(16))  # known | learning
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )