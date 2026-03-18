"""Mastodon delivery channel."""

import json
import os
import time
import urllib.request

from .base import Channel


class MastodonChannel(Channel):
    """Post digest to Mastodon as public mentions."""

    def __init__(self, config):
        self.instance = config["instance"]
        self.mention_target = config.get("mention_target", "")
        self.bot_account = config.get("bot_account", "")
        self.token = os.environ.get("MASTODON_ACCESS_TOKEN")
        if not self.token:
            raise RuntimeError(
                "MASTODON_ACCESS_TOKEN not set. "
                f"Create an app at {self.instance}/settings/applications "
                "and set the token as an environment variable."
            )
        self._verify_token_owner()

    def _verify_token_owner(self):
        """Verify that the access token belongs to the expected bot account."""
        if not self.bot_account:
            return
        url = f"{self.instance}/api/v1/accounts/verify_credentials"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {self.token}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            actual = data.get("username", "")
            if actual != self.bot_account:
                raise RuntimeError(
                    f"MASTODON_ACCESS_TOKEN belongs to @{actual}, "
                    f"but bot_account is configured as @{self.bot_account}. "
                    f"Set the correct token for @{self.bot_account}."
                )
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Failed to verify Mastodon token: {e}"
            )

    @property
    def char_limit(self):
        return 500

    def publish(self, header, papers):
        # Header toot
        header_text = f"{self.mention_target} {header}" if self.mention_target else header
        self._post(header_text)
        time.sleep(1)

        # Individual paper toots
        for p in papers:
            toot = self._format_paper(p)
            self._post(toot)
            time.sleep(1)

        print(f"Mastodon: posted {len(papers) + 1} toots to {self.instance}")

    def _format_paper(self, paper):
        """Format a single paper as a Mastodon post (max 500 chars)."""
        score = paper.get("score", 0)
        cats = ", ".join(paper.get("categories", [])[:3])
        reason = paper.get("reason", "")
        summary = paper.get("summary", "")
        title = paper.get("title", "Untitled")
        url = paper.get("url", "")
        authors = paper.get("authors", [])

        # Extract last names
        last_names = []
        for a in authors:
            if ", " in a:
                last_names.append(a.split(", ")[0])
            else:
                last_names.append(a.split()[-1])
        if len(last_names) > 4:
            author_str = ", ".join(last_names[:4]) + " et al."
        else:
            author_str = ", ".join(last_names)

        parts = [
            self.mention_target,
            f"⭐ {score}/100 | {cats}",
            f"👤 {author_str}" if author_str else "",
            f"📄 {title}",
            "",
            reason,
            "",
            summary if summary else "",
            "",
            url,
        ]
        # Remove consecutive empty lines
        cleaned = []
        for p in parts:
            if p == "" and cleaned and cleaned[-1] == "":
                continue
            cleaned.append(p)
        toot = "\n".join(cleaned)

        if len(toot) > 500:
            toot = toot[:497] + "..."

        return toot

    def post_text(self, text):
        """Post a plain text message."""
        if len(text) > 500:
            text = text[:497] + "..."
        self._post(text)

    def _post(self, text):
        """Post a status to Mastodon."""
        url = f"{self.instance}/api/v1/statuses"
        payload = json.dumps({
            "status": text,
            "visibility": "public",
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
