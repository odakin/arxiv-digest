"""Load configuration from config.yaml."""

from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config.yaml"
PROFILE_PATH = ROOT_DIR / "interest_profile.txt"
STATE_DIR = ROOT_DIR / "state"


def load_config():
    """Load and return config dict from config.yaml."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_profile():
    """Read the research interest profile text."""
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            f"interest_profile.txt not found at {PROFILE_PATH}. "
            "Create one from templates/interest_profile.txt or run "
            "python -m tools.setup_inspire <BAI>"
        )
    return PROFILE_PATH.read_text(encoding="utf-8")


def get_enabled_channels(config):
    """Return list of (name, settings) for enabled channels."""
    channels = config.get("channels", {})
    return [
        (name, settings)
        for name, settings in channels.items()
        if settings.get("enabled", False)
    ]
