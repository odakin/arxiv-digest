"""Mode B step 3: read scored_papers.json → publish to channels.

Usage:
    python3 -m src.post [--profile NAME]
"""

import argparse
import json
import sys
import traceback

from .config import load_config, STATE_DIR
from .publish import publish, notify_error


def main():
    config = None
    try:
        parser = argparse.ArgumentParser(description="Publish scored papers")
        parser.add_argument("--profile", help="Profile name from profiles/ directory")
        args = parser.parse_args()

        config = load_config(args.profile)

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

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}\n\n{traceback.format_exc()}"
        print(f"\n*** ERROR in post ***\n{error_msg}", file=sys.stderr)
        if config:
            notify_error(config, f"Post error: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
