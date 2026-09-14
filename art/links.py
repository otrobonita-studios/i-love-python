"""Chrome links: the generated map, the podcast, and the public repo.

Pure Python, no NiceGUI. The landing and footer render these; the app
serves the wiring diagram from generated/docs (Python-generated HTML).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WIRING_FILE = ROOT / "generated" / "docs" / "wiring-diagram.html"
WIRING_HREF = "/docs/wiring-diagram.html"
PODCAST_HREF = (
    "https://cdn-media.otrobonita.com/audio/podcasts/i-love-python/i-love-python-podcast.m4a"
)
REPO_HREF = "https://github.com/otrobonita-studios/i-love-python"


@dataclass(frozen=True)
class ChromeLink:
    """One footer/landing link: label, href, open-in-new-tab."""

    label: str
    href: str
    new_tab: bool = True


def wiring_diagram_file() -> Path:
    """Path of the generated architectural map. Missing means not generated."""
    return WIRING_FILE


NAV_ITEMS: tuple[tuple[str, str], ...] = (
    ("Letter", "#letter"),
    ("Curve", "#curve"),
    ("Quality", "#quality"),
    ("Explain", "#explain"),
    ("House", "#house"),
    ("Review", "#review"),
    ("Git", "#git"),
    ("Load", "#load"),
    ("Listen", "#listen"),
)


def chrome_links() -> tuple[ChromeLink, ...]:
    """The three links the chrome always shows, in display order."""
    return (
        ChromeLink("Architectural map", WIRING_HREF),
        ChromeLink("Podcast", PODCAST_HREF),
        ChromeLink("GitHub", REPO_HREF),
    )
