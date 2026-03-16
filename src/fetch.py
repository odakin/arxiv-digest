"""Mode B step 1: fetch arXiv papers → state/today_papers.json.

Usage:
    python3 -m src.fetch [--force]
"""

import argparse
import json
from datetime import date

from .config import load_config, get_profile, STATE_DIR
from .fetch_arxiv import fetch_new_papers


def main():
    parser = argparse.ArgumentParser(description="Fetch arXiv papers for digest")
    parser.add_argument("--force", action="store_true",
                        help="Run even on weekends")
    args = parser.parse_args()

    config = load_config()
    categories = config.get("arxiv_categories", [])

    if not categories:
        print("No arXiv categories configured. Set arxiv_categories in config.yaml.")
        return

    # Check weekend
    weekday = date.today().weekday()
    if weekday in (5, 6) and not args.force:
        day_name = "Saturday" if weekday == 5 else "Sunday"
        print(f"Today is {day_name} — no arXiv updates.")
        return

    # Fetch
    print("Fetching arXiv RSS...")
    papers = fetch_new_papers(categories)
    print(f"  Found {len(papers)} new papers")

    if not papers:
        print("No new papers found.")
        return

    # Get profile for Claude to read
    profile = get_profile()

    # Write output JSON
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = STATE_DIR / "today_papers.json"

    output = {
        "date": date.today().isoformat(),
        "total_papers": len(papers),
        "profile": profile,
        "config": {
            "scoring_threshold": config.get("scoring_threshold", 75),
            "language": config.get("language", "en"),
            "scoring_instructions": config.get("scoring_instructions", ""),
        },
        "papers": papers,
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"  Wrote {len(papers)} papers to {output_path}")
    print("Ready for scoring. Claude Code scheduled task will handle the rest.")


if __name__ == "__main__":
    main()
