"""Generate inspire_profile.txt from INSPIRE papers.

This generates the auto-derived profile (inspire_profile.txt), which is
separate from the hand-curated profile (interest_profile.txt). The scorer
reads both files. Monthly INSPIRE regeneration only touches this file,
so hand-curated priorities are never overwritten.

Usage:
    python3 -m tools.setup_inspire K.Y.Oda.1
    python3 -m tools.setup_inspire K.Y.Oda.1 --name "Kin-ya Oda" --affiliation "TWCU"
    python3 -m tools.setup_inspire N.Ogawa.3 --profile ogawa
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

from .fetch_inspire import fetch_papers

ROOT_DIR = Path(__file__).resolve().parent.parent
PROFILES_DIR = ROOT_DIR / "profiles"
DEFAULT_PROFILE = "default"


def build_profile(papers, author_bai, name=None, affiliation=None):
    """Generate a research interest profile from paper list."""
    # Extract the author's last name from BAI (e.g. "K.Y.Oda.1" -> "Oda")
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

    # Classify categories into tiers by publication weight
    total_papers = len(papers)
    primary_cats = []    # >=20% of papers
    secondary_cats = []  # >=5% of papers
    peripheral_cats = [] # <5% of papers (typically from cross-listing)
    for cat, count in all_categories.most_common():
        frac = count / total_papers
        entry = f"{cat} ({count}, {frac:.0%})"
        if frac >= 0.20:
            primary_cats.append(entry)
        elif frac >= 0.05:
            secondary_cats.append(entry)
        else:
            peripheral_cats.append(entry)

    top_collabs = [n for n, _ in all_coauthors.most_common(15)]

    display_name = name or author_bai
    affil_line = f"\nAffiliation: {affiliation}" if affiliation else ""

    # Build category weight section
    cat_lines = []
    if primary_cats:
        cat_lines.append(f"Primary fields (>=20%): {', '.join(primary_cats)}")
    if secondary_cats:
        cat_lines.append(f"Secondary fields (5-20%): {', '.join(secondary_cats)}")
    if peripheral_cats:
        cat_lines.append(f"Peripheral fields (<5%, via cross-listing): {', '.join(peripheral_cats)}")
    cat_section = "\n".join(cat_lines)

    profile = f"""Research Interest Profile: {display_name}
{affil_line}

Publication record: {len(papers)} papers (including cross-listed)

{cat_section}

Frequent collaborators: {', '.join(top_collabs)}

Recent focus (2020-present): {'; '.join(recent_titles[:10])}

When scoring papers, consider:
1. Direct overlap with primary/secondary fields (highest relevance)
2. Papers by frequent collaborators (high relevance)
3. New methods or results applicable to the above themes (moderate relevance)
4. Peripheral fields: relevant only if connecting to primary interests (lower relevance)
"""
    return profile


def regenerate_profile(bai, profile_name, name=None, affiliation=None):
    """Fetch from INSPIRE and write inspire_profile.txt. Returns True if updated."""
    papers = fetch_papers(bai)
    if not papers:
        return False

    profile = build_profile(papers, bai, name, affiliation)

    output_dir = PROFILES_DIR / profile_name
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "inspire_profile.txt"
    output_path.write_text(profile, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate interest profile from INSPIRE")
    parser.add_argument("bai", help="INSPIRE BAI (e.g. K.Y.Oda.1)")
    parser.add_argument("--name", help="Display name")
    parser.add_argument("--affiliation", help="Affiliation")
    parser.add_argument("--profile", default=DEFAULT_PROFILE,
                        help="Profile name (writes to profiles/<name>/, default: %(default)s)")
    args = parser.parse_args()

    print(f"Fetching papers for {args.bai} from INSPIRE...")
    if regenerate_profile(args.bai, args.profile, args.name, args.affiliation):
        output_path = PROFILES_DIR / args.profile / "inspire_profile.txt"
        print(f"  Wrote INSPIRE profile to {output_path}")

        interest_path = PROFILES_DIR / args.profile / "interest_profile.txt"
        if not interest_path.exists():
            print(f"\n  Note: {interest_path} does not exist yet.")
            print("  Create it from templates/interest_profile.txt to add your personal priorities.")
        else:
            print(f"\n  Hand-curated profile at {interest_path} is untouched.")

        print(f"\nGenerated INSPIRE profile:\n{output_path.read_text(encoding='utf-8')}")
    else:
        print("No papers found. Check the BAI.")
        sys.exit(1)


if __name__ == "__main__":
    main()
