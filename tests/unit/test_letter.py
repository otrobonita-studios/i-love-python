"""Tests for the love letter, zen decode, and tool glossary."""

from __future__ import annotations

from pathlib import Path

from explain import glossary, letter, zen

ROOT = Path(__file__).resolve().parent.parent.parent
SPEC = ROOT / "docs" / "spec-love.md"

TELEMETRY_NAMES = (
    "ruff format",
    "ruff lint",
    "mypy --strict",
    "pytest --cov",
    "radon cc",
    "bandit -r",
    "pip-audit",
    "lang-audit",
)


def test_letter_copy_matches_the_spec() -> None:
    spec = SPEC.read_text(encoding="utf-8")
    assert len(letter.PARAGRAPHS) == 11
    assert letter.PARAGRAPHS[0].startswith("I guess everyone has been there.")
    assert letter.PARAGRAPHS[10].endswith("write this one:")
    assert letter.CLOSING.startswith("The rest in the repo is not for the faint-hearted:")
    assert letter.KICKER == "A letter, not a dashboard"
    assert letter.TITLE == "For the love of the inaccessible"
    for paragraph in (*letter.PARAGRAPHS, letter.CLOSING):
        assert paragraph in spec


def test_zen_is_decoded_from_cpython_this() -> None:
    text = zen.zen_of_python()
    assert text.startswith("The Zen of Python, by Tim Peters")
    assert "Readability counts." in text
    assert "Namespaces are one honking great idea" in text
    assert "import this" not in text.splitlines()[0]


def test_glossary_covers_every_telemetry_tool() -> None:
    names = {guide.name for guide in glossary.GUIDES}
    assert names == set(TELEMETRY_NAMES)
    for name in TELEMETRY_NAMES:
        row = glossary.lookup(name)
        assert row is not None
        assert row.href
        assert row.what
        assert row.why
        assert row.kind
    assert glossary.lookup("not-a-tool") is None
    assert glossary.PYTEST_COV_HREF.startswith("https://")
    assert len(glossary.RADON_LEGEND) == 5
    assert glossary.tool_anchor("ruff format") == "tool-ruff-format"
    assert glossary.tool_anchor("mypy --strict") == "tool-mypy-strict"
