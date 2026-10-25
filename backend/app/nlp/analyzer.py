from collections import Counter
from dataclasses import dataclass

import spacy
from wordfreq import zipf_frequency

SKIP_POS = {"PROPN", "PUNCT", "SPACE", "X", "INTJ", "NUM", "SYM"}

_nlp = None


def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm", disable=["ner"])
    return _nlp


@dataclass
class LemmaStat:
    lemma: str
    pos: str
    count: int
    zipf: float
    example: str


def analyze_lines(
    lines: list[str], max_zipf: float = 4.5
) -> tuple[list[LemmaStat], list[tuple[str, int]]]:
    nlp = get_nlp()
    doc = nlp(" ".join(lines))

    counts: Counter = Counter()
    examples: dict = {}
    phrasal: Counter = Counter()

    for sent in doc.sents:
        for token in sent:
            if token.dep_ == "prt" and token.head.pos_ == "VERB":
                phrasal[f"{token.head.lemma_.lower()} {token.lower_}"] += 1

            if not token.is_alpha or token.is_stop or token.pos_ in SKIP_POS:
                continue
            lemma = token.lemma_.lower()
            if len(lemma) < 3:
                continue
            key = (lemma, token.pos_)
            counts[key] += 1
            examples.setdefault(key, sent.text.strip())

    stats = []
    for (lemma, pos), count in counts.items():
        zipf = zipf_frequency(lemma, "en")
        if zipf == 0 or zipf > max_zipf:
            continue
        stats.append(LemmaStat(lemma, pos, count, zipf, examples[(lemma, pos)]))

    stats.sort(key=lambda s: (-s.count, s.zipf))
    return stats, phrasal.most_common()