import re
from pathlib import Path

import srt

HTML_TAG_RE = re.compile(r"<[^>]+>")
ASS_TAG_RE = re.compile(r"\{\\[^}]*\}")
BRACKETS_RE = re.compile(r"\[[^\]]*\]|\([^)]*\)")
MUSIC_RE = re.compile(r"[♪♫#]+")
DASH_RE = re.compile(r"^[ \t]*-[ \t]*", re.M)
SPEAKER_RE = re.compile(r"^[ \t]*[A-Z][A-Z0-9 .'\-]{1,25}:[ \t]*", re.M)
SPACES_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    text = HTML_TAG_RE.sub("", text)
    text = ASS_TAG_RE.sub("", text)
    text = BRACKETS_RE.sub("", text)
    text = MUSIC_RE.sub("", text)
    text = DASH_RE.sub("", text)
    text = SPEAKER_RE.sub("", text)
    return SPACES_RE.sub(" ", text).strip()


def decode_srt(raw: bytes) -> str:
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1")


def parse_srt_content(content: str) -> list[str]:
    lines = []
    for subtitle in srt.parse(content, ignore_errors=True):
        cleaned = clean_text(subtitle.content)
        if cleaned:
            lines.append(cleaned)
    return lines


def parse_srt(path: str | Path) -> list[str]:
    return parse_srt_content(decode_srt(Path(path).read_bytes()))

WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def count_words(lines: list[str]) -> int:
    return sum(len(WORD_RE.findall(line)) for line in lines)