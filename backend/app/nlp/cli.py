import argparse
import sys

from app.nlp.analyzer import analyze_lines
from app.nlp.srt_parser import parse_srt


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Analyze an .srt file")
    parser.add_argument("path")
    parser.add_argument("--top", type=int, default=50)
    args = parser.parse_args()

    lines = parse_srt(args.path)
    stats, phrasal = analyze_lines(lines)

    print(f"Subtitle lines: {len(lines)}, candidate words: {len(stats)}\n")
    print(f"{'lemma':<18}{'pos':<7}{'count':>6}{'zipf':>7}  example")
    for item in stats[: args.top]:
        print(
            f"{item.lemma:<18}{item.pos:<7}{item.count:>6}"
            f"{item.zipf:>7.2f}  {item.example[:70]}"
        )

    print("\nPhrasal verbs:")
    for phrase, count in phrasal[:20]:
        print(f"{phrase:<22}{count}")


if __name__ == "__main__":
    main()