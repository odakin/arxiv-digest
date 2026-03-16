"""Mode A entry point: fetch → score (API) → publish.

Usage:
    python3 -m src.main
"""

from datetime import date

from .config import load_config
from .fetch_arxiv import fetch_new_papers
from .scorer import score_papers
from .publish import publish


def main():
    config = load_config()
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


if __name__ == "__main__":
    main()
