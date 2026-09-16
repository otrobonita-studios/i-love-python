"""Canonical /listen ("Podcasts") page copy: kicker, headline, lede, episodes.

EPISODES is a plain tuple -- appending the next recording is a one-line
addition here, nothing in render.py changes. First entry is the original
walkthrough; more are expected.
"""

from __future__ import annotations

from dataclasses import dataclass

from art.links import PODCAST_HREF

_CDN_BASE = "https://cdn-media.otrobonita.com/audio/podcasts/i-love-python"
_BYLINE = "Jesper Karlsson · Otrobonita AI Labs"

KICKER = "PODCAST SERIES"
TITLE_LINE_1 = "Learn Python"
TITLE_LINE_2 = "by Car"
LEDE = (
    "A relaxed transition into Python for the seasoned developer — nine "
    "conversations, recorded for the original repo, still the best way to "
    "hear the argument in Jesper's voice."
)


@dataclass(frozen=True)
class Episode:
    """One podcast episode: title, byline, and its real audio URL."""

    title: str
    byline: str
    href: str


EPISODES: tuple[Episode, ...] = (
    Episode(
        title="I love Python — the walkthrough",
        byline=_BYLINE,
        href=PODCAST_HREF,
    ),
    Episode(
        title="The Zen of Python Philosophy",
        byline=_BYLINE,
        href=f"{_CDN_BASE}/The_Zen_of_Python_Philosophy.m4a",
    ),
    Episode(
        title="Python for Experienced Developers",
        byline=_BYLINE,
        href=f"{_CDN_BASE}/Python_for_Experienced_Developers.m4a",
    ),
    Episode(
        title="NumPy, SciPy, and Pandas for Beginners",
        byline=_BYLINE,
        href=f"{_CDN_BASE}/NumPy_SciPy_and_Pandas_for_Beginners.m4a",
    ),
    Episode(
        title="Bypass the Front-End Wall with NiceGUI",
        byline=_BYLINE,
        href=f"{_CDN_BASE}/Bypass_the_front-end_wall_with_NiceGUI.m4a",
    ),
    Episode(
        title="How Python Backends Actually Work",
        byline=_BYLINE,
        href=f"{_CDN_BASE}/How_Python_Backends_Actually_Work.m4a",
    ),
    Episode(
        title="Python Backend Architecture: Data, Security, and Stability",
        byline=_BYLINE,
        href=f"{_CDN_BASE}/Python_Backend_Architecture_Data,_Security_and_Stability.m4a",
    ),
    Episode(
        title="Flask, Django, and FastAPI: Architectural Tradeoffs",
        byline=_BYLINE,
        href=f"{_CDN_BASE}/Flask_Django_and_FastAPI_Architectural_Tradeoffs.m4a",
    ),
    Episode(
        title="Shipping Python Backends with Docker and CI/CD",
        byline=_BYLINE,
        href=f"{_CDN_BASE}/Shipping_Python_Backends_with_Docker_and_CICD.m4a",
    ),
)
