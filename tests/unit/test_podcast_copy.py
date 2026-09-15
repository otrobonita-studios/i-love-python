"""Canonical /listen (Podcasts) copy and the episode list."""

from art import podcast_copy
from art.links import PODCAST_HREF


def test_headline_and_lede_are_canonical() -> None:
    assert podcast_copy.KICKER == "PODCAST"
    assert podcast_copy.TITLE_LINE_1 == "Forty minutes with"
    assert podcast_copy.TITLE_LINE_2 == "the thing itself."
    assert "Jesper" in podcast_copy.LEDE


def test_episodes_is_a_real_array_with_the_original_first() -> None:
    assert len(podcast_copy.EPISODES) >= 1
    first = podcast_copy.EPISODES[0]
    assert first.title == "I love Python — the walkthrough"
    assert first.byline == "Jesper Karlsson · Otrobonita AI Labs"
    assert first.href == PODCAST_HREF


def test_every_episode_has_a_real_audio_href() -> None:
    for episode in podcast_copy.EPISODES:
        assert episode.title
        assert episode.byline
        assert episode.href.startswith("https://")
