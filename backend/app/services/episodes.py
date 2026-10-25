from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Episode, EpisodeLemma, Lemma, Title
from app.nlp.analyzer import LemmaStat

PHRASAL_POS = "PHRASAL"
MIN_PHRASAL_COUNT = 2
MAX_EXAMPLE_LEN = 300


def get_or_create_title(db: Session, name: str) -> Title:
    title = db.scalar(select(Title).where(Title.name == name))
    if title is None:
        title = Title(name=name)
        db.add(title)
        db.flush()
    return title


def save_analysis(
    db: Session,
    title_name: str,
    season: int | None,
    number: int | None,
    subtitle_lines: int,
    stats: list[LemmaStat],
    phrasal: list[tuple[str, int]],
) -> Episode:
    title = get_or_create_title(db, title_name)

    old = db.scalar(
        select(Episode).where(
            Episode.title_id == title.id,
            Episode.season == season,
            Episode.number == number,
        )
    )
    if old is not None:
        db.delete(old)
        db.flush()

    episode = Episode(
        title_id=title.id, season=season, number=number, subtitle_lines=subtitle_lines
    )
    db.add(episode)
    db.flush()

    items = [
        (s.lemma, s.pos, s.zipf, s.level, s.count, s.example[:MAX_EXAMPLE_LEN])
        for s in stats
    ]
    items += [
        (phrase, PHRASAL_POS, 0.0, None, count, "")
        for phrase, count in phrasal
        if count >= MIN_PHRASAL_COUNT
    ]

    texts = {item[0] for item in items}
    existing = {
        (lemma.text, lemma.pos): lemma
        for lemma in db.scalars(select(Lemma).where(Lemma.text.in_(texts)))
    }

    for text, pos, zipf, level, count, example in items:
        lemma = existing.get((text, pos))
        if lemma is None:
            lemma = Lemma(text=text, pos=pos, zipf=zipf, level=level)
            db.add(lemma)
            existing[(text, pos)] = lemma
        db.add(
            EpisodeLemma(
                episode_id=episode.id, lemma=lemma, count=count, example=example
            )
        )

    db.commit()
    return episode