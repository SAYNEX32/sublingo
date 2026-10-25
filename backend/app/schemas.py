from pydantic import BaseModel


class EpisodeOut(BaseModel):
    id: int
    title: str
    season: int | None
    number: int | None
    subtitle_lines: int
    word_count: int


class WordOut(BaseModel):
    lemma: str
    pos: str
    level: str | None
    zipf: float
    count: int
    example: str


class EpisodeWords(BaseModel):
    episode: EpisodeOut
    words: list[WordOut]