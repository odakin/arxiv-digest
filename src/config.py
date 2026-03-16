"""Load configuration from config.yaml, with per-profile overrides."""

from pathlib import Path

import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT_DIR / "config.yaml"
PROFILES_DIR = ROOT_DIR / "profiles"
STATE_DIR = ROOT_DIR / "state"

DEFAULT_PROFILE = "default"


def _deep_merge(base, override):
    """Merge override dict into base dict (mutates base). Nested dicts are merged."""
    for key, val in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(val, dict):
            _deep_merge(base[key], val)
        else:
            base[key] = val
    return base


def load_config(profile_name=DEFAULT_PROFILE):
    """Load root config.yaml, then deep-merge profiles/<name>/config.yaml on top."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)

    profile_config_path = PROFILES_DIR / profile_name / "config.yaml"
    if profile_config_path.exists():
        with open(profile_config_path, encoding="utf-8") as f:
            override = yaml.safe_load(f) or {}
        config = _deep_merge(config, override)

    return config


def get_profile_dir(profile_name=DEFAULT_PROFILE):
    """Return profiles/<name>/ directory."""
    return PROFILES_DIR / profile_name


def get_profile(profile_name=DEFAULT_PROFILE):
    """Read research interest profile(s) from profiles/<name>/.

    Combines interest_profile.txt (hand-curated) with
    inspire_profile.txt (auto-generated) if both exist.
    At least one must exist.
    """
    profile_dir = get_profile_dir(profile_name)
    manual_path = profile_dir / "interest_profile.txt"
    inspire_path = profile_dir / "inspire_profile.txt"

    has_manual = manual_path.exists()
    has_inspire = inspire_path.exists()

    if not has_manual and not has_inspire:
        raise FileNotFoundError(
            f"No profile found in profiles/{profile_name}/. "
            "Create interest_profile.txt from templates/interest_profile.txt "
            "or run python3 -m tools.setup_inspire <BAI> --profile "
            f"{profile_name}"
        )

    parts = []
    if has_manual:
        parts.append(manual_path.read_text(encoding="utf-8"))
    if has_inspire:
        parts.append(inspire_path.read_text(encoding="utf-8"))

    return "\n\n".join(parts)


def get_enabled_channels(config):
    """Return list of (name, settings) for enabled channels."""
    channels = config.get("channels", {})
    return [
        (name, settings)
        for name, settings in channels.items()
        if settings.get("enabled", False)
    ]


def list_profiles():
    """Return list of profile names found in profiles/ directory."""
    if not PROFILES_DIR.exists():
        return []
    return sorted(
        d.name for d in PROFILES_DIR.iterdir()
        if d.is_dir() and (
            (d / "interest_profile.txt").exists()
            or (d / "inspire_profile.txt").exists()
        )
    )
