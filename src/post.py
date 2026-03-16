"""Mode B step 3: read scored_papers.json → publish to channels.

Usage:
    python3 -m src.post
"""

import json

from .config import load_config, STATE_DIR
from .publish import publish


def main():
    config = load_config()

    scored_path = STATE_DIR / "scored_papers.json"
    if not scored_path.exists():
        print(f"No scored papers found at {scored_path}")
        print("Run scoring first (Claude Code scheduled task step 2).")
        return

    with open(scored_path, encoding="utf-8") as f:
        data = json.load(f)

    scored_papers = data.get("scored_papers", [])
    total_fetched = data.get("total_fetched", 0)

    publish(config, scored_papers, total_fetched)
    print("Done.")


if __name__ == "__main__":
    main()
