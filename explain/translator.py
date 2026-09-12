"""Plain-English explanations of what happened in code and tooling.

Deterministic, rule-based translation: given a diff or a tool result, it
produces short human-readable bullets. No network, no LLM, no fakes.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiffStats:
    """Facts extracted from a unified diff."""

    files: int
    added: int
    removed: int
    new_files: int
    touches_tests: bool
    non_python_files: int


def extract_diff_stats(diff: str) -> DiffStats:
    """Parse a unified diff into plain facts (pure function)."""
    files = set()
    new_files = 0
    non_python = 0
    added = 0
    removed = 0
    touches_tests = False
    for line in diff.splitlines():
        if line.startswith("--- /dev/null"):
            new_files += 1
        elif line.startswith("+++ b/"):
            path = line.removeprefix("+++ b/")
            files.add(path)
            if path.startswith("tests/") or "/test_" in path:
                touches_tests = True
            if not path.endswith(".py") and not path.endswith(
                (".md", ".toml", ".txt", ".yml", ".yaml")
            ):
                non_python += 1
        elif line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return DiffStats(
        files=len(files),
        added=added,
        removed=removed,
        new_files=new_files,
        touches_tests=touches_tests,
        non_python_files=non_python,
    )


def explain_diff(diff: str) -> list[str]:
    """Turn a unified diff into a few plain-English bullets."""
    stats = extract_diff_stats(diff)
    bullets: list[str] = []
    if stats.files == 0:
        return ["This diff touches no files - nothing to explain."]
    bullets.append(
        f"Touches {stats.files} file(s), adding {stats.added} and removing {stats.removed} lines."
    )
    if stats.new_files:
        bullets.append(f"Introduces {stats.new_files} brand-new file(s).")
    if stats.touches_tests:
        bullets.append("Includes test changes - good sign for durability.")
    else:
        bullets.append("No test changes - consider what could break this.")
    if stats.non_python_files:
        bullets.append(f"Modifies {stats.non_python_files} non-Python file(s).")
    if stats.removed > stats.added * 2 and stats.removed > 20:
        bullets.append("Mostly deletions - a cleanup or refactor in disguise.")
    return bullets


def explain_tool(name: str, status: str, detail: str) -> str:
    """Explain one tool result in one plain sentence."""
    if status == "pass":
        return f"{name} passed: {detail}"
    if status == "fail":
        return f"{name} failed - read this carefully: {detail}"
    if status == "unavailable":
        return f"{name} is not installed here, so we are not pretending it ran."
    if status == "warn":
        return f"{name} ran with a warning (not a failure): {detail}"
    return f"{name} reported: {detail}"


def explain_all(
    names: tuple[str, ...],
    statuses: tuple[str, ...],
    details: tuple[str, ...],
) -> list[str]:
    """Explain many tool results at once, in the given order."""
    return [
        explain_tool(name, status, detail)
        for name, status, detail in zip(names, statuses, details, strict=True)
    ]
