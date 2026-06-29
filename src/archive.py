"""Archive scored papers to date-partitioned JSON files.

This module owns archive persistence end-to-end:

  - ``archive_scored_papers``: write per-profile JSON snapshots into
    ``archive/{year}/{month}/{date}_{profile}.json``.
  - ``commit_archives_to_git``: commit + push the archive/ tree so that
    snapshots survive across machines and don't accumulate as
    cross-session WIP leakage.

The git helper is intentionally scoped to ``archive/`` only and is
best-effort: any failure prints a warning and returns without raising,
so that scheduled-task runs are never broken by transient git issues
(network, remote divergence, etc.). The next run picks up whatever
the previous one left behind.

Currently only mode B (``post_all.py``) calls ``commit_archives_to_git``.
Mode A (``post.py``, single-profile, used by template consumers) does
not auto-commit, so template users keep manual control over when
their scored data is published to git.
"""

import json
import subprocess
from datetime import date
from pathlib import Path

ARCHIVE_DIR = Path(__file__).resolve().parent.parent / "archive"


def already_posted_on_origin(_today=None):
    """Return True if today's archive is already present on ``origin/main``.

    Defense-in-depth against double execution (= 2026-06-29 incident root):
    if another machine has already posted today's digest and pushed the
    archive commit, this returns True so the caller (``post_all.main``) can
    abort before posting and avoid duplicate distribution to Mastodon /
    Discord.

    Layered defense:
      - Layer 1 (cron-time): ``routine-host-gate.py`` checks
        ``private/active-routine-host.json`` before the launchd job runs.
      - Layer 2 (post-time, this function): even if the gate ledger is stale
        or both machines somehow pass it, the second runner sees today's
        archive already on origin and aborts before posting.

    Race window: ~tens of seconds between "first runner pushes" and "second
    runner fetches". Closing this window further would require a content
    lock on a shared remote, which is overkill for daily cadence.

    Fail-open: any git/network error returns False so the function can
    never block a legitimate run.
    """
    today = (_today or date.today()).isoformat()
    yyyy = today[:4]
    mm = today[5:7]
    repo_root = ARCHIVE_DIR.parent

    def run(args):
        return subprocess.run(
            args, cwd=str(repo_root),
            capture_output=True, text=True, timeout=15,
        )

    try:
        fetch = run(["git", "fetch", "origin", "--quiet"])
        if fetch.returncode != 0:
            return False  # fail-open: network/auth issues never block
        ls = run([
            "git", "ls-tree", "--name-only", "origin/main",
            f"archive/{yyyy}/{mm}/",
        ])
        if ls.returncode != 0:
            return False
        for line in ls.stdout.splitlines():
            # entries like: archive/2026/06/2026-06-29_odakin.json
            if today in line and line.endswith(".json"):
                return True
    except Exception:
        return False
    return False


def archive_scored_papers(profile_name, *, scored_path=None, data=None):
    """Copy scored papers to archive/{year}/{month}/{date}_{profile}.json.

    Provide either scored_path (Path to JSON file) or data (dict).
    Idempotent: re-running the same day overwrites the file.
    Returns the archive path on success, None if nothing to archive.
    """
    if data is None:
        if scored_path is None or not scored_path.exists():
            return None
        with open(scored_path, encoding="utf-8") as f:
            data = json.load(f)

    today = date.today()
    dest_dir = ARCHIVE_DIR / str(today.year) / f"{today.month:02d}"
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / f"{today.isoformat()}_{profile_name}.json"
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"  Archived → {dest.relative_to(ARCHIVE_DIR.parent)}")
    return dest


def commit_archives_to_git():
    """Commit and push any new files in archive/ to the repo's remote.

    Behaviour:

    - Stages ``archive/`` only — never touches unrelated WIP files.
    - No-op when nothing under ``archive/`` is new (idempotent re-runs).
    - Pulls with ``--rebase --autostash`` if the local branch is behind,
      so cross-machine race conditions self-heal.
    - On any failure (network, conflict, missing upstream), prints a
      ``WARNING:`` line and returns without raising. The local commit
      may exist; the next scheduled run will catch up via the standard
      pull-rebase path.

    Why this is here and not in ``post_all.py``: archive persistence
    (file IO + git) is the cohesive responsibility of this module, and
    keeping the git logic next to ``archive_scored_papers`` makes it
    obvious that the two halves of "save a daily snapshot" live
    together.
    """
    repo_root = ARCHIVE_DIR.parent

    def run(args):
        return subprocess.run(
            args, cwd=str(repo_root),
            capture_output=True, text=True,
        )

    fetch = run(["git", "fetch"])
    if fetch.returncode != 0:
        print(f"  WARNING: archive sync skipped (fetch failed): {fetch.stderr.strip()}")
        return

    behind = run(["git", "rev-list", "--count", "HEAD..@{u}"])
    if behind.returncode == 0 and int((behind.stdout or "0").strip() or 0) > 0:
        pull = run(["git", "pull", "--rebase", "--autostash"])
        if pull.returncode != 0:
            print(f"  WARNING: archive sync skipped (rebase failed): {pull.stderr.strip()}")
            return

    # Scope: archive/ only. Other dirty files (src/, configs, ...) stay
    # untouched in the working tree.
    add = run(["git", "add", "archive/"])
    if add.returncode != 0:
        print(f"  WARNING: archive add failed: {add.stderr.strip()}")
        return

    # Empty-commit guard.
    diff = run(["git", "diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        return  # nothing under archive/ to commit

    msg = f"archive: {date.today().isoformat()} daily digest"
    commit = run(["git", "commit", "-m", msg])
    if commit.returncode != 0:
        print(f"  WARNING: archive commit failed: {commit.stderr.strip()}")
        return

    push = run(["git", "push"])
    if push.returncode != 0:
        print(f"  WARNING: archive push deferred (will retry next run): {push.stderr.strip()}")
    else:
        print(f"  Archive committed and pushed: {msg}")
