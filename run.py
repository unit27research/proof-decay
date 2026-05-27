#!/usr/bin/env python3
import argparse
from pathlib import Path

from proof_decay import analyze_decay, render_markdown


def main() -> int:
    parser = argparse.ArgumentParser(description="Review stale or condition-shifted proof for Markdown/text claims.")
    parser.add_argument("claims", help="Markdown/text file containing current claims.")
    parser.add_argument("--proof", default="", help="Optional structured proof notes file.")
    parser.add_argument("--output", default="proof_decay_review.md", help="Markdown review output path.")
    parser.add_argument("--review-date", default="", help="Review date in YYYY-MM-DD format. Defaults to today.")
    parser.add_argument("--review-only", action="store_true", help="Accepted for symmetry; output is always review-only.")
    args = parser.parse_args()

    claims_text = Path(args.claims).read_text(encoding="utf-8")
    proof_text = Path(args.proof).read_text(encoding="utf-8") if args.proof else ""

    review = analyze_decay(claims_text, proof_text, review_date=args.review_date or None)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_markdown(review), encoding="utf-8")

    print(f"Wrote {output_path}")
    print(f"Reviewed {len(review['reviews'])} claim(s)")
    print("Review-only mode: no source rewrite generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
