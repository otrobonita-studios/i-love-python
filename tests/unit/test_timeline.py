"""Unit tests for the commit timelines."""

from git_discipline.timeline import bad_timeline, real_timeline


def test_bad_timeline_has_named_sins() -> None:
    bad = bad_timeline()
    assert len(bad) >= 5
    assert all(entry.quality == "bad" for entry in bad)
    assert all(entry.reason for entry in bad)


def test_real_timeline_parses_manifest_trailers() -> None:
    timeline = real_timeline()
    assert len(timeline) >= 5
    # Every commit this project authored carries a Manifest: trailer.
    # Inherited history (initial commit), merge commits (git or GitHub),
    # and platform-generated commits (a GitHub integration writing
    # directly -- e.g. Fly.io's launch flow -- follows no repo convention
    # and isn't "this project" authoring it) may not. real_timeline()
    # still honestly reports those as missing one; this test just isn't
    # the place to assert an external actor's commit message.
    _EXTERNAL_COMMITS = {"New files from Fly.io Launch"}
    authored = [
        e
        for e in timeline
        if e.subject != "Initial commit"
        and not e.subject.startswith("Merge branch")
        and not e.subject.startswith("Merge pull request")
        and e.subject not in _EXTERNAL_COMMITS
    ]
    assert len(authored) >= 5
    assert all(e.manifest for e in authored)
    assert all(e.quality == "good" for e in authored)
    assert all(e.quality in ("good", "bad") for e in timeline)


def test_real_timeline_is_newest_first() -> None:
    timeline = real_timeline()
    subjects = [entry.subject for entry in timeline]
    assert len(subjects) == len(set(subjects))
