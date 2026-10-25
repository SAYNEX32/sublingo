import random
import sys

from sqlalchemy import select
from wordfreq import top_n_list, zipf_frequency

from app.database import SessionLocal
from app.models import Lemma
from app.nlp.analyzer import SKIP_POS, get_nlp

MIN_ZIPF = 4.51
MAX_ZIPF = 5.6
MAX_WORDS = 300
FUNCTION_POS = {"AUX", "ADP", "DET", "PRON", "CCONJ", "SCONJ", "PART"}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    nlp = get_nlp()
    words = [
        word
        for word in top_n_list("en", 8000)
        if word.isalpha()
        and word.isascii()
        and len(word) >= 4
        and MIN_ZIPF <= zipf_frequency(word, "en") <= MAX_ZIPF
    ]

    entries = []
    for doc in nlp.pipe(words):
        token = doc[0]
        if token.is_stop or token.pos_ in SKIP_POS | FUNCTION_POS:
            continue
        if token.lemma_.lower() != token.text.lower():
            continue
        entries.append((token.text.lower(), token.pos_))

    entries = random.Random(42).sample(entries, min(MAX_WORDS, len(entries)))

    added = 0
    with SessionLocal() as db:
        for text, pos in entries:
            if db.scalar(select(Lemma.id).where(Lemma.text == text, Lemma.pos == pos)):
                continue
            zipf = zipf_frequency(text, "en")
            level = "A2" if zipf >= 5.0 else "B1"
            db.add(Lemma(text=text, pos=pos, zipf=zipf, level=level))
            added += 1
        db.commit()
    print(f"Added {added} frequent words")


if __name__ == "__main__":
    main()