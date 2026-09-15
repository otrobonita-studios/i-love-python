"""Canonical /listen ("Podcasts") page copy: kicker, headline, lede, episodes.

EPISODES is a plain tuple -- appending the next recording is a one-line
addition here, nothing in render.py changes. First entry is the original
walkthrough; more are expected.
"""

from __future__ import annotations

from dataclasses import dataclass

from art.links import PODCAST_HREF

KICKER = "PODCAST"
TITLE_LINE_1 = "Forty minutes with"
TITLE_LINE_2 = "the thing itself."
LEDE = (
    "The long-form walkthrough of what this is and why — recorded for the "
    "original repo, still the best way to hear the argument in Jesper's voice."
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
        byline="Jesper Karlsson · Otrobonita AI Labs",
        href=PODCAST_HREF,
    ),
)
