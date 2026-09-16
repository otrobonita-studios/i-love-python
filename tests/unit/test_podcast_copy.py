"""Canonical /listen (Podcasts) copy and the episode list."""

from art import podcast_copy


def test_headline_and_lede_are_canonical() -> None:
    assert podcast_copy.KICKER == "PODCAST SERIES"
    assert podcast_copy.TITLE_LINE_1 == "Learn Python"
    assert podcast_copy.TITLE_LINE_2 == "by Car"
    assert "driving hours" in podcast_copy.LEDE
    assert "seasoned developer" in podcast_copy.LEDE


def test_episodes_is_a_real_array_with_the_series_opener_first() -> None:
    assert len(podcast_copy.EPISODES) >= 8
    first = podcast_copy.EPISODES[0]
    assert first.title == "The Zen of Python Philosophy"
    assert first.byline == "Jesper Karlsson · Otrobonita AI Labs"
    assert first.href.startswith("https://cdn-media.otrobonita.com/")


def test_the_walkthrough_episode_was_dropped() -> None:
    titles = {episode.title for episode in podcast_copy.EPISODES}
    assert "I love Python — the walkthrough" not in titles


def test_the_python_series_is_all_present() -> None:
    titles = {episode.title for episode in podcast_copy.EPISODES}
    assert "The Zen of Python Philosophy" in titles
    assert "Shipping Python Backends with Docker and CI/CD" in titles
    hrefs = {episode.href for episode in podcast_copy.EPISODES}
    assert len(hrefs) == len(podcast_copy.EPISODES)  # no duplicate audio URLs


def test_every_episode_has_a_real_audio_href() -> None:
    for episode in podcast_copy.EPISODES:
        assert episode.title
        assert episode.byline
        assert episode.href.startswith("https://")
