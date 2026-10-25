import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from app.nlp.analyzer import analyze_lines
from app.nlp.srt_parser import parse_srt


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Analyze an .srt file")
    parser.add_argument("path")
    parser.add_argument("--top", type=int, default=50)
    parser.add_argument("--json", dest="json_path", help="save full result to JSON")
    args = parser.parse_args()

    lines = parse_srt(args.path)
    stats, phrasal = analyze_lines(lines)

    print(f"Subtitle lines: {len(lines)}, candidate words: {len(stats)}\n")
    print(f"{'lemma':<22}{'pos':<7}{'level':<7}{'count':>6}{'zipf':>7}  example")
    for item in stats[: args.top]:
        print(
            f"{item.lemma:<22}{item.pos:<7}{item.level:<7}{item.count:>6}"
            f"{item.zipf:>7.2f}  {item.example[:60]}"
        )

    print("\nPhrasal verbs:")
    for phrase, count in phrasal[:20]:
        print(f"{phrase:<22}{count}")

    if args.json_path:
        result = {
            "source": Path(args.path).name,
            "subtitle_lines": len(lines),
            "lemmas": [asdict(item) for item in stats],
            "phrasal_verbs": [{"phrase": p, "count": c} for p, c in phrasal],
        }
        out = Path(args.json_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()