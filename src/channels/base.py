"""Base class for delivery channels."""


class Channel:
    """Base class for delivery channels."""

    def publish(self, header, papers):
        """Publish header and scored papers to this channel.

        Args:
            header: header text (e.g. "arXiv新着ダイジェスト: 133件中5件")
            papers: list of paper dicts with keys:
                score, title, authors, categories, url, reason, summary
                Channels should truncate to their char_limit as needed.
        """
        raise NotImplementedError

    @property
    def char_limit(self):
        """Max characters per post. None means no limit."""
        return None
