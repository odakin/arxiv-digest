"""Load configuration from config.yaml."""

from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config.yaml"
PROFILE_PATH = ROOT_DIR / "interest_profile.txt"
INSPIRE_PROFILE_PATH = ROOT_DIR / "inspire_profile.txt"
STATE_DIR = ROOT_DIR / "state"


def load_config():
    """Load and return config dict from config.yaml."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_profile():
    """Read research interest profile(s).

    Combines the hand-curated profile (interest_profile.txt) with the
    INSPIRE-derived profile (inspire_profile.txt) if both exist.
    At least one must exist.
    """
    has_manual = PROFILE_PATH.exists()
    has_inspire = INSPIRE_PROFILE_PATH.exists()

    if not has_manual and not has_inspire:
        raise FileNotFoundError(
            "No profile found. Create interest_profile.txt from "
            "templates/interest_profile.txt or run "
            "python3 -m tools.setup_inspire <BAI>"
        )

    parts = []
    if has_manual:
        parts.append(PROFILE_PATH.read_text(encoding="utf-8"))
    if has_inspire:
        parts.append(INSPIRE_PROFILE_PATH.read_text(encoding="utf-8"))

    return "\n\n".join(parts)


def get_enabled_channels(config):
    """Return list of (name, settings) for enabled channels."""
    channels = config.get("channels", {})
    return [
        (name, settings)
        for name, settings in channels.items()
        if settings.get("enabled", False)
    ]
