from collections import Counter
from dataclasses import dataclass

import spacy
from wordfreq import zipf_frequency

SKIP_POS = {"PROPN", "PUNCT", "SPACE", "X", "INTJ", "NUM", "SYM"}
SKIP_ENTITIES = {"PERSON", "GPE", "LOC", "FAC", "ORG"}

_nlp = None


def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


SPOKEN_SHORT = {"goin", "doin"}


def is_spoken_variant(lemma: str) -> bool:
    """Spoken spelling like "fuckin" or "nothin" for "fucking" or "nothing"."""
    if lemma in SPOKEN_SHORT:
        return True
    if len(lemma) < 5 or not lemma.endswith("in"):
        return False
    base = zipf_frequency(lemma + "g", "en")
    return base >= 4.5 and base - zipf_frequency(lemma, "en") >= 1.0


def rough_level(zipf: float) -> str:
    """Baseline difficulty estimate from word frequency (not real CEFR)."""
    if zipf >= 4.2:
        return "B1"
    if zipf >= 3.7:
        return "B2"
    if zipf >= 3.0:
        return "C1"
    return "C2"


def looks_like_name(mid_total: int, mid_caps: int) -> bool:
    """A word that is almost always capitalized mid-sentence is likely a name."""
    return mid_total > 0 and mid_caps / mid_total >= 0.8


@dataclass
class LemmaStat:
    lemma: str
    pos: str
    count: int
    zipf: float
    level: str
    example: str


def analyze_lines(
    lines: list[str], max_zipf: float = 4.5, min_zipf: float = 1.5
) -> tuple[list[LemmaStat], list[tuple[str, int]]]:
    nlp = get_nlp()
    doc = nlp(" ".join(lines))

    counts: Counter = Counter()
    pos_counts: dict[str, Counter] = {}
    examples: dict[str, str] = {}
    mid_total: Counter = Counter()
    mid_caps: Counter = Counter()
    phrasal: Counter = Counter()

    for sent in doc.sents:
        for token in sent:
            if token.dep_ == "prt" and token.head.pos_ == "VERB":
                phrasal[f"{token.head.lemma_.lower()} {token.lower_}"] += 1

            if not token.is_alpha or token.is_stop or token.pos_ in SKIP_POS:
                continue
            if token.ent_type_ in SKIP_ENTITIES:
                continue
            lemma = token.lemma_.lower()
            if is_spoken_variant(lemma):
                continue
            if len(lemma) < 3:
                continue

            if not token.is_sent_start:
                mid_total[lemma] += 1
                if token.text[0].isupper():
                    mid_caps[lemma] += 1

            counts[lemma] += 1
            pos_counts.setdefault(lemma, Counter())[token.pos_] += 1
            examples.setdefault(lemma, sent.text.strip())

    stats = []
    for lemma, count in counts.items():
        if looks_like_name(mid_total[lemma], mid_caps[lemma]):
            continue
        zipf = zipf_frequency(lemma, "en")
        if zipf < min_zipf or zipf > max_zipf:
            continue
        pos = pos_counts[lemma].most_common(1)[0][0]
        stats.append(
            LemmaStat(lemma, pos, count, zipf, rough_level(zipf), examples[lemma])
        )

    stats.sort(key=lambda s: (-s.count, s.zipf))
    return stats, phrasal.most_common()