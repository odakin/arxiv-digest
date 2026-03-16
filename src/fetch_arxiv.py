"""Fetch new arXiv submissions from RSS feed, with HTML fallback."""

import re
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape


NS = {
    "arxiv": "http://arxiv.org/schemas/atom",
    "dc": "http://purl.org/dc/elements/1.1/",
}


def _clean_html(text):
    """Strip HTML tags and decode entities."""
    text = unescape(text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def _clean_latex(text):
    """Clean common LaTeX escapes from author names."""
    text = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", text)
    text = re.sub(r"[\\{}]", "", text)
    return text.strip()


def _extract_arxiv_id(link):
    """Extract arXiv ID from abs URL like http://arxiv.org/abs/2503.12345v1."""
    m = re.search(r"abs/(\d+\.\d+)", link)
    return m.group(1) if m else None


def _extract_abstract(description):
    """Extract abstract from RSS description field."""
    if not description:
        return ""
    m = re.search(r"Abstract:\s*(.*)", description, re.DOTALL)
    if m:
        return _clean_html(m.group(1))
    return _clean_html(description)


def _build_rss_url(categories):
    """Build arXiv RSS URL from category list."""
    return "https://rss.arxiv.org/rss/" + "+".join(categories)


def _fetch_via_rss(categories):
    """Fetch papers from arXiv RSS feed."""
    url = _build_rss_url(categories)
    req = urllib.request.Request(url, headers={"User-Agent": "arXiv-digest/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()

    root = ET.fromstring(data)

    papers = []
    seen_ids = set()

    for item in root.iter("item"):
        announce_el = item.find("arxiv:announce_type", NS)
        announce = (announce_el.text or "").strip() if announce_el is not None else ""
        if announce and announce != "new":
            continue

        title_el = item.find("title")
        if title_el is None or title_el.text is None:
            continue
        title = title_el.text.strip()

        link_el = item.find("link")
        link = link_el.text.strip() if link_el is not None and link_el.text else ""

        arxiv_id = _extract_arxiv_id(link)
        if not arxiv_id or arxiv_id in seen_ids:
            continue
        seen_ids.add(arxiv_id)

        desc_el = item.find("description")
        abstract = _extract_abstract(desc_el.text if desc_el is not None else "")

        authors = []
        for creator in item.findall("dc:creator", NS):
            if creator.text:
                for name in creator.text.split(","):
                    cleaned = _clean_latex(name.strip())
                    if cleaned:
                        authors.append(cleaned)

        categories = []
        for cat_el in item.findall("category"):
            cat_text = cat_el.text
            if cat_text:
                categories.append(cat_text.strip())

        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "categories": categories,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
        })

    return papers


def _fetch_via_html(category):
    """Fetch new papers from arXiv HTML listing for a single category."""
    url = f"https://arxiv.org/list/{category}/new"
    req = urllib.request.Request(url, headers={"User-Agent": "arXiv-digest/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read().decode("utf-8")

    papers = []

    new_section = re.search(
        r"<h3>New submissions.*?</h3>(.*?)(?:<h3>|</dl>)", data, re.DOTALL
    )
    if not new_section:
        return papers

    section = new_section.group(1)

    entries = re.findall(
        r"<dt>.*?arXiv:(\d+\.\d+).*?</dt>\s*<dd>(.*?)</dd>", section, re.DOTALL
    )

    for arxiv_id, dd in entries:
        m = re.search(
            r"<div class='list-title[^']*'>.*?<span class='descriptor'>Title:</span>\s*(.*?)</div>",
            dd, re.DOTALL,
        )
        title = _clean_html(m.group(1)) if m else ""

        authors = []
        m = re.search(r"<div class='list-authors'>(.*?)</div>", dd, re.DOTALL)
        if m:
            for a_match in re.finditer(r">([^<]+)</a>", m.group(1)):
                name = a_match.group(1).strip()
                if name:
                    authors.append(name)

        cats = []
        m = re.search(r"<div class='list-subjects'>(.*?)</div>", dd, re.DOTALL)
        if m:
            for cat_match in re.finditer(r"\(([a-z-]+(?:\.[A-Z]+)?)\)", m.group(1)):
                cats.append(cat_match.group(1))

        m = re.search(r"<p class='mathjax'>\s*(.*?)\s*</p>", dd, re.DOTALL)
        abstract = _clean_html(m.group(1)) if m else ""

        papers.append({
            "arxiv_id": arxiv_id,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "categories": cats,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
        })

    return papers


def fetch_new_papers(categories):
    """Fetch today's new arXiv submissions.

    Args:
        categories: list of arXiv category strings (e.g. ["hep-ph", "gr-qc"])

    Returns:
        list of paper dicts
    """
    papers = _fetch_via_rss(categories)
    if papers:
        return papers

    # RSS empty — fall back to HTML scraping
    print("  RSS feed empty, falling back to HTML scraping...")
    seen_ids = set()
    all_papers = []
    for cat in categories:
        for p in _fetch_via_html(cat):
            if p["arxiv_id"] not in seen_ids:
                seen_ids.add(p["arxiv_id"])
                all_papers.append(p)

    return all_papers
