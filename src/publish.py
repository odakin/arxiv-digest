"""Dispatch scored papers to enabled delivery channels."""

from .config import get_enabled_channels
from .channels.mastodon import MastodonChannel
from .channels.stdout import StdoutChannel

CHANNEL_CLASSES = {
    "mastodon": MastodonChannel,
    "stdout": StdoutChannel,
}


def publish(config, scored_papers, total_fetched):
    """Publish scored papers to all enabled channels.

    Args:
        config: loaded config dict
        scored_papers: list of paper dicts with score, reason, summary
        total_fetched: total number of papers fetched from arXiv
    """
    if not scored_papers:
        print("No papers to publish.")
        return

    language = config.get("language", "en")
    if language == "ja":
        header = (
            f"📚 arXiv新着ダイジェスト\n"
            f"本日の新着 {total_fetched} 件中 {len(scored_papers)} 件をお届けします。"
        )
    else:
        header = (
            f"📚 arXiv Daily Digest\n"
            f"Delivering {len(scored_papers)} papers out of {total_fetched} new submissions."
        )

    enabled = get_enabled_channels(config)
    if not enabled:
        print("No channels enabled. Enable at least one in config.yaml.")
        return

    for name, settings in enabled:
        cls = CHANNEL_CLASSES.get(name)
        if cls is None:
            print(f"Channel '{name}' not implemented yet, skipping.")
            continue
        try:
            channel = cls(settings)
            channel.publish(header, scored_papers)
        except Exception as e:
            print(f"Error publishing to {name}: {e}")
