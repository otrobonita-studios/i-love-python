"""Plain-English field guide for the eight quality tools.

No NiceGUI. panel/render.py looks up by telemetry tool name.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolGuide:
    """One glossary row: kind, what, why, and official docs."""

    name: str
    kind: str
    what: str
    why: str
    href: str


PYTEST_COV_HREF = "https://pytest-cov.readthedocs.io/en/latest/"

RADON_LEGEND: tuple[tuple[str, str], ...] = (
    ("A", "Simple. A few branches. Easy to test."),
    ("B", "A little branching. Still readable."),
    ("C", "Getting busy. Allowed in small numbers."),
    ("D", "Too many paths. This would fail the gate."),
    ("E", "A maze. Instant fail."),
)

# Closing-paragraph mentions → telemetry tool name (for in-page links).
MENTION_TO_TOOL: dict[str, str] = {
    "ruff": "ruff format",
    "mypy": "mypy --strict",
    "radon": "radon cc",
    "pytest": "pytest --cov",
    "bandit": "bandit -r",
}

GUIDES: tuple[ToolGuide, ...] = (
    ToolGuide(
        name="ruff format",
        kind="formatter",
        what=(
            "A Python code formatter, from Astral. It picks the spaces, quotes, "
            "and line breaks so nobody has to. The equivalent of one house style "
            "for the whole repo."
        ),
        why=(
            "We run it as a check, never a rewrite: if a file isn't already "
            "formatted, the snapshot fails."
        ),
        href="https://docs.astral.sh/ruff/formatter/",
    ),
    ToolGuide(
        name="ruff lint",
        kind="linter",
        what=(
            "A linter: it reads the code without running it and flags unused "
            "imports, likely bugs, and outdated syntax. Think of a proofreader "
            "that never gets tired."
        ),
        why=(
            "Catches the mistakes a formatter cannot — the ones that are still "
            "valid Python, just wrong."
        ),
        href="https://docs.astral.sh/ruff/linter/",
    ),
    ToolGuide(
        name="mypy --strict",
        kind="type checker",
        what=(
            "A static type checker. Python is dynamic; mypy reads the type "
            "annotations and proves — before the program runs — that names, "
            "returns, and optionals actually match."
        ),
        why=(
            "--strict is the hardest setting: no untyped functions, no implicit "
            "optionals. The whole codebase is annotated to survive it."
        ),
        href="https://mypy.readthedocs.io/en/stable/command_line.html#cmdoption-mypy-strict",
    ),
    ToolGuide(
        name="pytest --cov",
        kind="tests",
        what=(
            "pytest is the test runner. The --cov plugin (pytest-cov) then counts "
            "which lines those tests actually executed. Green tests with untested "
            "code still leave you blind."
        ),
        why=(
            "This repo fails the run if coverage drops under 70% — and a single "
            "failed test fails the gate even when coverage is high."
        ),
        href="https://docs.pytest.org/en/stable/",
    ),
    ToolGuide(
        name="radon cc",
        kind="complexity",
        what=(
            "Cyclomatic complexity: how many independent paths a function has. "
            "A is a straight line. E is a maze."
        ),
        why="The gate allows A, B, and a few C's. D and E would fail the build.",
        href="https://radon.readthedocs.io/en/latest/intro.html#cyclomatic-complexity",
    ),
    ToolGuide(
        name="bandit -r",
        kind="security",
        what=(
            "A security linter from PyCQA. It hunts for patterns that become "
            "exploits: SQL injection, shelling out with user input, weak "
            "cryptography, eval()."
        ),
        why=(
            "It does not prove the code is safe. It catches the obvious mistakes "
            "before a reviewer has to."
        ),
        href="https://bandit.readthedocs.io/en/latest/",
    ),
    ToolGuide(
        name="pip-audit",
        kind="dependencies",
        what=(
            "A PyPA tool that checks installed packages against the "
            "known-vulnerability database. Perfect formatting can still ship a "
            "rotten dependency."
        ),
        why="Needs network. If this check is missing, we show N/A — never a fake pass.",
        href="https://github.com/pypa/pip-audit",
    ),
    ToolGuide(
        name="lang-audit",
        kind="house rule",
        what=(
            "Ours. A small Python script that walks the tree and fails if it "
            "finds hand-authored JavaScript, shell, or other non-Python source."
        ),
        why=(
            "Generated files need a GENERATED header, or they live under "
            "generated/. Love, in this studio, is one language."
        ),
        href=(
            "https://github.com/otrobonita-studios/i-love-python/blob/main/scripts/lang_audit.py"
        ),
    ),
)

_BY_NAME = {guide.name: guide for guide in GUIDES}


def lookup(name: str) -> ToolGuide | None:
    """Return the glossary row for a telemetry tool name, if we have one."""
    return _BY_NAME.get(name)


def tool_anchor(name: str) -> str:
    """DOM id for a quality card (`ruff format` → `tool-ruff-format`)."""
    slug = name.lower().replace(" ", "-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return "tool-" + slug
