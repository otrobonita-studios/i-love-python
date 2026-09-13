"""Unit tests for git_discipline/console.py (the ask-git session).

The git layer (_git) is monkeypatched so the session logic is testable on
any machine; the resolvers (sha extraction, blame line finding) are tested
directly against their real inputs.
"""

from __future__ import annotations

import pytest

import git_discipline.console as console


def test_session_has_four_questions() -> None:
    steps = console.build_steps()
    assert len(steps) == 4
    assert all(s.prompt and s.display_command and s.explanation for s in steps)
    assert steps[1].display_command.startswith("git log -S")


def test_resolve_show_uses_sha_from_search_output() -> None:
    outputs = ["log out\n", "abc1234 fix: restore missing cos(4t) term\n"]
    assert console._resolve_show(outputs) == "git show abc1234 -- art/heart.py"


def test_resolve_show_falls_back_to_head() -> None:
    assert console._resolve_show(["out", "   "]) == "git show HEAD -- art/heart.py"


def test_resolve_blame_targets_the_cos4t_line() -> None:
    command = console._resolve_blame([])
    assert command.startswith("git blame -L")
    assert command.endswith("art/heart.py")


def test_run_session_executes_all_steps(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    def fake_git(args: list[str]) -> str:
        calls.append(args)
        if "-S" in args:
            return "abc1234 fix: restore missing cos(4t) term\n"
        return f"fake output for {args[0]}\n"

    monkeypatch.setattr(console, "_git", fake_git)
    results = console.run_session()
    assert len(results) == 4
    assert "abc1234" in results[2].command
    assert all(r.output for r in results)
    assert calls[1][0] == "log"
    assert "-S" in calls[1]
    assert console.SEARCH_TERM in calls[1]


def test_git_failure_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(args: list[str]) -> str:
        raise RuntimeError("git log failed")

    monkeypatch.setattr(console, "_git", broken)
    with pytest.raises(RuntimeError, match="git log failed"):
        console.run_session()


def test_missing_git_is_a_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(console, "GIT", None)
    with pytest.raises(RuntimeError, match="git executable"):
        console._git(["log"])
