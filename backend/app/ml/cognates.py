"""Cheap cognate detector: does an English word have a Russian look-alike?

The English word is transliterated into Cyrillic with several spelling
variants, common Latin suffixes are mapped to Russian endings, and the most
frequent matching Russian word decides the feature value.
"""
from functools import lru_cache

from wordfreq import zipf_frequency

MAX_VARIANTS = 120
MIN_CANDIDATE_LEN = 3

# (english suffix, russian endings), longest suffixes first
SUFFIXES = [
    ("ically", ["ически", "ический"]),
    ("ology", ["ология"]),
    ("ical", ["ический", "ичный", "ик"]),
    ("tion", ["ция", "ции"]),
    ("sion", ["зия", "сия", "ссия"]),
    ("ism", ["изм"]),
    ("ist", ["ист"]),
    ("ity", ["итет", "ость"]),
    ("ic", ["ик", "ический", "ный"]),
    ("ous", ["ный", "озный"]),
    ("ive", ["ивный", "ив"]),
    ("ize", ["изировать", "изация"]),
    ("ise", ["изировать"]),
    ("ate", ["ировать", "ат"]),
    ("al", ["аль", "альный", "ал"]),
    ("ure", ["ура"]),
    ("ine", ["ин", "ина"]),
    ("ium", ["ий"]),
    ("ent", ["ент", "ентный"]),
    ("ant", ["ант", "антный"]),
    ("or", ["ор"]),
    ("er", ["ер", "р"]),
    ("y", ["ия", "ий", ""]),
]

# Plain endings tried for any stem
GENERIC_ENDINGS = ["", "а", "ь", "ий", "ия", "ик", "ный"]

DIGRAPHS = {
    "ph": ["ф"],
    "th": ["т", "с"],
    "ch": ["ч", "к", "х"],
    "sh": ["ш"],
    "ck": ["к"],
    "qu": ["кв", "к"],
    "ee": ["и"],
    "oo": ["у"],
    "ea": ["и", "еа"],
    "ou": ["ау", "у"],
    "ai": ["эй", "ай"],
    "ay": ["ей", "ай"],
    "ng": ["нг"],
}

LETTERS = {
    "a": ["а", "э"],
    "b": ["б"],
    "c": ["к", "ц", "с"],
    "d": ["д"],
    "e": ["е", "э", ""],
    "f": ["ф"],
    "g": ["г", "дж"],
    "h": ["х", "г", ""],
    "i": ["и", "ай"],
    "j": ["дж", "ж"],
    "k": ["к"],
    "l": ["л"],
    "m": ["м"],
    "n": ["н"],
    "o": ["о"],
    "p": ["п"],
    "q": ["к"],
    "r": ["р"],
    "s": ["с", "з"],
    "t": ["т"],
    "u": ["у", "ю", "а"],
    "v": ["в"],
    "w": ["в", "у"],
    "x": ["кс"],
    "y": ["и", "й"],
    "z": ["з", "ц"],
}


def _split_pieces(stem: str) -> list[list[str]]:
    pieces: list[list[str]] = []
    i = 0
    while i < len(stem):
        pair = stem[i : i + 2]
        if pair in DIGRAPHS:
            pieces.append(DIGRAPHS[pair])
            i += 2
            continue
        letter = stem[i]
        if letter in LETTERS:
            pieces.append(LETTERS[letter])
        i += 1
    return pieces


def _transliterate(stem: str) -> list[str]:
    variants = [""]
    for alternatives in _split_pieces(stem):
        variants = [v + alt for v in variants for alt in alternatives][:MAX_VARIANTS]
    return variants


@lru_cache(maxsize=20000)
def cognate_zipf(word: str) -> float:
    """Highest Russian word frequency (zipf) among look-alike candidates, 0 if none."""
    word = word.lower().strip()
    if not word.isalpha() or not word.isascii() or len(word) < 3:
        return 0.0

    options = [(word, GENERIC_ENDINGS)]
    for suffix, endings in SUFFIXES:
        if word.endswith(suffix) and len(word) - len(suffix) >= 2:
            options.append((word[: -len(suffix)], endings + GENERIC_ENDINGS[:1]))
            break

    best = 0.0
    seen: set[str] = set()
    for stem, endings in options:
        for variant in _transliterate(stem):
            for ending in endings:
                candidate = variant + ending
                if len(candidate) < MIN_CANDIDATE_LEN or candidate in seen:
                    continue
                seen.add(candidate)
                best = max(best, zipf_frequency(candidate, "ru"))
    return round(best, 2)