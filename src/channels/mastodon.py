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
        self._max_chars = self._fetch_instance_char_limit()

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

    def _fetch_instance_char_limit(self):
        """Fetch the actual character limit from the instance API."""
        for path in ("/api/v2/instance", "/api/v1/instance"):
            url = f"{self.instance}{path}"
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                # v2: configuration.statuses.max_characters
                if "configuration" in data:
                    limit = (
                        data["configuration"]
                        .get("statuses", {})
                        .get("max_characters")
                    )
                    if limit:
                        return int(limit)
                # v1: max_toot_chars (Pleroma/Akkoma) or fallback
                if "max_toot_chars" in data:
                    return int(data["max_toot_chars"])
            except (urllib.error.URLError, KeyError, ValueError):
                continue
        return 500  # safe default

    @property
    def char_limit(self):
        return self._max_chars

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
        """Format a single paper as a Mastodon post, fitting within char_limit.

        Structure (fixed parts are never truncated):
            mention_target
            ⭐ score/100 | categories
            👤 authors
            📄 title

            reason        ← truncated first if needed

            summary       ← truncated second if needed

            url           ← always preserved
        """
        limit = self._max_chars
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

        # Fixed parts that must not be truncated
        header_lines = [
            self.mention_target,
            f"⭐ {score}/100 | {cats}",
            f"👤 {author_str}" if author_str else "",
            f"📄 {title}",
        ]
        header = "\n".join(line for line in header_lines if line)
        footer = url

        # Overhead: newlines between header, body, footer sections
        # header + \n\n + [reason] + \n\n + [summary] + \n\n + url
        fixed_len = len(header) + len(footer)
        # 2 newlines before body + 2 newlines before url = 4 minimum
        overhead = 4
        budget = limit - fixed_len - overhead

        if budget <= 0:
            # Even header + url won't fit; just return them
            return f"{header}\n\n{footer}"

        # Try to fit both reason and summary
        # separator between reason and summary: \n\n = 2 chars
        if reason and summary:
            combined = len(reason) + len(summary) + 2
            if combined <= budget:
                body = f"{reason}\n\n{summary}"
            else:
                # Truncate summary first, then reason
                reason_budget = min(len(reason), budget * 2 // 3)
                summary_budget = budget - reason_budget - 2
                if summary_budget < 10:
                    # Drop summary entirely
                    reason = self._truncate(reason, budget)
                    body = reason
                else:
                    reason = self._truncate(reason, reason_budget)
                    summary = self._truncate(summary, summary_budget)
                    body = f"{reason}\n\n{summary}"
        elif reason:
            body = self._truncate(reason, budget)
        elif summary:
            body = self._truncate(summary, budget)
        else:
            body = ""

        if body:
            return f"{header}\n\n{body}\n\n{footer}"
        return f"{header}\n\n{footer}"

    @staticmethod
    def _truncate(text, max_len):
        """Truncate text to max_len, adding … if cut."""
        if len(text) <= max_len:
            return text
        return text[: max_len - 1] + "…"

    def post_text(self, text):
        """Post a plain text message."""
        if len(text) > self._max_chars:
            text = text[: self._max_chars - 1] + "…"
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
