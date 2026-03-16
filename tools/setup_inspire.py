"""Generate interest_profile.txt from INSPIRE papers.

Usage:
    python -m tools.setup_inspire K.Y.Oda.1
    python -m tools.setup_inspire K.Y.Oda.1 --name "Kin-ya Oda" --affiliation "TWCU"
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

from .fetch_inspire import fetch_papers

ROOT_DIR = Path(__file__).resolve().parent.parent
PROFILE_PATH = ROOT_DIR / "interest_profile.txt"


def build_profile(papers, author_bai, name=None, affiliation=None):
    """Generate a research interest profile from paper list."""
    # Extract the author's last name from BAI (e.g. "K.Y.Oda.1" → "Oda")
    bai_parts = author_bai.split(".")
    author_surname = bai_parts[-2] if len(bai_parts) >= 2 else bai_parts[0]

    all_categories = Counter()
    all_coauthors = Counter()
    recent_titles = []

    for p in papers:
        for c in p.get("categories", []):
            all_categories[c] += 1

        for a in p.get("authors", []):
            if author_surname not in a:
                all_coauthors[a] += 1

        if p.get("year", 0) >= 2020:
            recent_titles.append(p.get("title", ""))

    top_cats = [f"{cat} ({count})" for cat, count in all_categories.most_common(10)]
    top_collabs = [n for n, _ in all_coauthors.most_common(15)]

    display_name = name or author_bai
    affil_line = f"\nAffiliation: {affiliation}" if affiliation else ""

    profile = f"""Research Interest Profile: {display_name}
{affil_line}

Publication record: {len(papers)} papers

Primary arXiv categories: {', '.join(top_cats)}

Frequent collaborators: {', '.join(top_collabs)}

Recent focus (2020-present): {'; '.join(recent_titles[:10])}

When scoring papers, consider:
1. Direct overlap with the above themes (highest relevance)
2. Papers by frequent collaborators (high relevance)
3. New methods or results applicable to the above themes (moderate relevance)
4. General developments in the field (lower relevance)
"""
    return profile


def main():
    parser = argparse.ArgumentParser(description="Generate interest profile from INSPIRE")
    parser.add_argument("bai", help="INSPIRE BAI (e.g. K.Y.Oda.1)")
    parser.add_argument("--name", help="Display name")
    parser.add_argument("--affiliation", help="Affiliation")
    args = parser.parse_args()

    print(f"Fetching papers for {args.bai} from INSPIRE...")
    papers = fetch_papers(args.bai)
    print(f"  Found {len(papers)} papers")

    if not papers:
        print("No papers found. Check the BAI.")
        sys.exit(1)

    profile = build_profile(papers, args.bai, args.name, args.affiliation)
    PROFILE_PATH.write_text(profile, encoding="utf-8")
    print(f"  Wrote profile to {PROFILE_PATH}")
    print("\nGenerated profile (review and edit as needed):")
    print(profile)


if __name__ == "__main__":
    main()
