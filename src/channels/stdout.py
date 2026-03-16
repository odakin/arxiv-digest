"""Stdout delivery channel for testing and debugging."""

from .base import Channel


class StdoutChannel(Channel):
    """Print digest to stdout."""

    def __init__(self, config=None):
        pass

    @property
    def char_limit(self):
        return None

    def publish(self, header, papers):
        print(f"\n{'='*60}")
        print(header)
        print(f"{'='*60}\n")

        for i, p in enumerate(papers, 1):
            score = p.get("score", 0)
            cats = ", ".join(p.get("categories", [])[:3])
            title = p.get("title", "Untitled")
            url = p.get("url", "")
            authors = p.get("authors", [])
            reason = p.get("reason", "")
            summary = p.get("summary", "")

            author_str = ", ".join(authors[:4])
            if len(authors) > 4:
                author_str += " et al."

            print(f"[{i}] ⭐ {score}/100 | {cats}")
            print(f"    📄 {title}")
            print(f"    👤 {author_str}")
            if reason:
                print(f"    💬 {reason}")
            if summary:
                print(f"    📝 {summary}")
            print(f"    🔗 {url}")
            print()
