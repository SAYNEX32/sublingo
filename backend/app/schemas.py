from typing import Literal

from pydantic import BaseModel, Field


class EpisodeOut(BaseModel):
    id: int
    title: str
    season: int | None
    number: int | None
    subtitle_lines: int
    word_count: int


class WordOut(BaseModel):
    lemma_id: int
    lemma: str
    pos: str
    level: str | None
    zipf: float
    count: int
    example: str


class EpisodeWords(BaseModel):
    episode: EpisodeOut
    words: list[WordOut]


class MarkIn(BaseModel):
    lemma_ids: list[int] = Field(min_length=1, max_length=2000)
    status: Literal["known", "learning", "unknown"]


class MarkOut(BaseModel):
    updated: int


class UserWordOut(BaseModel):
    lemma_id: int
    lemma: str
    pos: str
    status: str


class ReportOut(BaseModel):
    episode: EpisodeOut
    total_words: int
    unknown_occurrences: int
    coverage: float
    target: float
    words_to_target: int | None
    to_learn: list[WordOut]