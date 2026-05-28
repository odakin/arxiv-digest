# arxiv-digest

[Japanese version](README.ja.md)

AI-powered daily arXiv digest for researchers. Get personalized paper recommendations delivered to Mastodon, Discord, email, or other channels every morning.

## Why this exists

A typical arXiv RSS feed in an active field shows 50-200 new papers per day. Reading every title is wasteful; missing a relevant one is costly. arxiv-digest scores each new paper against your hand-written research interests using Claude, then delivers only the top matches with a short reason for each. Two execution modes share the same fetch / score / publish pipeline — only the scoring step differs:

| Mode | Scoring | Cost | Requirements |
|------|---------|------|-------------|
| **A: GitHub Actions** | Anthropic API | ~$0.01/day (Sonnet) | GitHub + API key |
| **B: Local Claude Code** | Claude Code scheduled task | **Free** (Pro Max) | Always-on Mac/PC |

## What it looks like

Sample delivery (truncated):

```
📚 arXiv Daily Digest
Delivering 4 papers out of 87 new submissions.

⭐ 92/100 | hep-ph, gr-qc
👤 Smith, Jones, Doe, et al.
📄 Paper title here

Reason: Direct continuation of your line on X — improves the bound from ...
Summary: The authors compute Y to two loops and find Z.

https://arxiv.org/abs/2604.XXXXX
```

The same papers can be fanned out to multiple channels simultaneously.

## Quick start (Mode A)

1. Click **"Use this template"** → **"Create a new repository"**
2. Edit `config.yaml` and `profiles/default/interest_profile.txt`
3. Add GitHub Secrets for your channels (`ANTHROPIC_API_KEY` plus e.g. `MASTODON_ACCESS_TOKEN`)
4. Enable GitHub Actions — the schedule fires every weekday morning

Full walkthrough — INSPIRE auto-profile for HEP, channel-specific setup, troubleshooting — in [docs/setup-guide.md](docs/setup-guide.md). Mode B (free with Claude Pro Max) is covered in the same guide.

## Delivery channels

| Channel | Auth | Status |
|---------|------|--------|
| Mastodon | Access token | Available |
| Discord | Webhook URL | Available |
| Email (SMTP/STARTTLS) | Username + app password | Available |
| stdout | None | Available (testing) |
| Slack | Webhook URL | Planned |
| Bluesky | App password | Planned |

To add a channel: subclass `Channel` in `src/channels/base.py`, register the class in `src/publish.py`, optionally extend `config.yaml`. Existing channels (`discord.py`, `mastodon.py`, `email.py`) are the reference pattern.

## What's where

- `config.yaml` — root defaults; per-profile overrides under `profiles/<name>/config.yaml`
- `profiles/default/` — starting point; copy or rename to make your own profile
- `src/` — fetch / score / publish pipeline (`src/channels/` = delivery channels)
- `skill/SKILL.md` — Mode B Claude Code scoring instructions
- `tools/setup_inspire.py` — auto-generate HEP profile from INSPIRE BAI
- `docs/setup-guide.md` — full setup walkthrough
- `CLAUDE.md` — maintainer reference (structure, modes, profiles)
- `DESIGN.md` — design judgments (why mode A vs B, archive ownership, etc.)

## License

MIT — see [LICENSE](LICENSE).
