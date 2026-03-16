"""Auto-update INSPIRE profiles when new papers by registrants are detected."""

from .config import load_config, list_profiles, PROFILES_DIR


def _parse_bai(bai):
    """Extract surname and initials from INSPIRE BAI.

    E.g. "K.Y.Oda.1" → ("Oda", ["K", "Y"])
         "N.Ogawa.3" → ("Ogawa", ["N"])
    """
    parts = bai.split(".")
    # Last part is disambiguator number, second-to-last is surname
    if len(parts) < 3:
        return None, []
    surname = parts[-2]
    initials = [p for p in parts[:-2] if p]
    return surname, initials


def _author_matches(author_name, surname, initials):
    """Check if an arXiv author name matches a BAI's surname + first initial.

    Author names from arXiv are typically "Firstname Lastname" or "F. Lastname".
    """
    words = author_name.strip().split()
    if not words:
        return False
    # Surname = last word of the author name
    if words[-1].lower() != surname.lower():
        return False
    # Check first initial
    if initials and words[0]:
        return words[0][0].upper() == initials[0].upper()
    return True


def check_for_profile_updates(papers):
    """Check if any fetched papers are by INSPIRE-registered profile authors.

    Scans all profiles for inspire_bai config, matches against paper authors,
    and regenerates inspire_profile.txt for any matches.

    Returns list of (profile_name, bai) that were updated.
    """
    # Lazy import to avoid circular dependency
    from tools.setup_inspire import regenerate_profile

    # Collect BAI info from all profiles
    profile_bais = []
    for name in list_profiles():
        cfg = load_config(name)
        bai = cfg.get("inspire_bai")
        if bai:
            surname, initials = _parse_bai(bai)
            if surname:
                profile_bais.append((name, bai, surname, initials))

    if not profile_bais:
        return []

    # Check each paper's authors against registered profiles
    matched = set()
    for paper in papers:
        for author in paper.get("authors", []):
            for prof_name, bai, surname, initials in profile_bais:
                if prof_name not in matched and _author_matches(author, surname, initials):
                    matched.add(prof_name)

    # Regenerate matched profiles
    updated = []
    for prof_name, bai, _, _ in profile_bais:
        if prof_name in matched:
            print(f"  New paper detected for {prof_name} ({bai}), regenerating INSPIRE profile...")
            if regenerate_profile(bai, prof_name):
                updated.append((prof_name, bai))
                print(f"    Updated profiles/{prof_name}/inspire_profile.txt")
            else:
                print(f"    Warning: INSPIRE fetch failed for {bai}")

    return updated
