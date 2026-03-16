"""Mode A entry point: fetch → score (API) → publish.

Usage:
    python3 -m src.main [--profile NAME]
"""

import argparse
import sys
import traceback
from datetime import date

from .config import load_config, DEFAULT_PROFILE
from .fetch_arxiv import fetch_new_papers
from .scorer import score_papers
from .publish import publish, notify_error


def main():
    config = None
    try:
        parser = argparse.ArgumentParser(description="arXiv digest (Mode A)")
        parser.add_argument("--profile", default=DEFAULT_PROFILE,
                            help="Profile name from profiles/ directory (default: %(default)s)")
        args = parser.parse_args()

        config = load_config(args.profile)
        config["_profile_name"] = args.profile
        categories = config.get("arxiv_categories", [])

        if not categories:
            print("No arXiv categories configured. Set arxiv_categories in config.yaml.")
            return

        # Check weekend
        weekday = date.today().weekday()
        if weekday in (5, 6):
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

        # Score
        print("Scoring papers with API...")
        scored = score_papers(config, papers)
        print(f"  {len(scored)} papers scored above threshold")

        # Publish
        publish(config, scored, len(papers))
        print("Done.")

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
        print(f"\n*** ERROR ***\n{error_msg}", file=sys.stderr)
        if config:
            notify_error(config, f"{type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
