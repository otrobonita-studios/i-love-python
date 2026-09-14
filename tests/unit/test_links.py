"""Tests for art/links.py (chrome URLs, no NiceGUI)."""

from __future__ import annotations

import tomllib

import scripts.wiring_diagram as diagram
from art.links import (
    NAV_ITEMS,
    PODCAST_HREF,
    REPO_HREF,
    ROOT,
    WIRING_HREF,
    chrome_links,
    wiring_diagram_file,
)

README = ROOT / "README.md"
PYPROJECT = ROOT / "pyproject.toml"


def test_chrome_links_are_map_podcast_and_repo() -> None:
    links = chrome_links()
    assert tuple(link.label for link in links) == (
        "Architectural map",
        "Podcast",
        "GitHub",
    )
    hrefs = {link.href for link in links}
    assert hrefs == {WIRING_HREF, PODCAST_HREF, REPO_HREF}
    assert all(link.new_tab for link in links)


def test_nav_items_are_sections_not_tabs() -> None:
    labels = [name for name, _href in NAV_ITEMS]
    assert labels == [
        "Letter",
        "Curve",
        "Quality",
        "Explain",
        "House",
        "Review",
        "Git",
        "Load",
        "Listen",
    ]
    assert dict(NAV_ITEMS)["House"] == "/map"
    assert all(href.startswith("/") for _name, href in NAV_ITEMS)
    assert not any("#" in href for _name, href in NAV_ITEMS)


def test_repo_url_matches_pyproject() -> None:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    assert data["project"]["urls"]["repository"] == REPO_HREF


def test_podcast_url_is_the_cdn_m4a() -> None:
    assert PODCAST_HREF.startswith("https://cdn-media.otrobonita.com/")
    assert PODCAST_HREF.endswith("/i-love-python/i-love-python-podcast.m4a")
    readme = README.read_text(encoding="utf-8")
    assert (
        "cdn-media.otrobonita.com/audio/podcasts/i-love-python/i-love-python-podcast.m4a" in readme
    )


def test_wiring_href_is_served_under_docs() -> None:
    assert WIRING_HREF == "/docs/wiring-diagram.html"


def test_wiring_file_is_the_generated_map() -> None:
    path = wiring_diagram_file()
    assert path == diagram.GENERATED_DIR / "wiring-diagram.html"
    assert path.is_file()
    header = path.read_text(encoding="utf-8").splitlines()[0]
    assert "GENERATED" in header
    assert "scripts/wiring_diagram.py" in header
