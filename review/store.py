"""Pull real commits and diffs out of this repo's git history.

The review panel never invents diffs: it shows actual commits from
`git log` and the actual patch from `git show`.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Commit:
    """One commit from the real history."""

    sha: str
    subject: str
    date: str
    body: str


def _git(args: list[str]) -> str:
    proc = subprocess.run(  # nosec B603 - fixed argv, no shell, only git in our own repo
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def commit_count() -> int:
    """How many commits are in the history."""
    out = _git(["rev-list", "--count", "HEAD"])
    return int(out.strip() or 0)


def list_commits() -> list[Commit]:
    """All commits, newest first, with body (trailers included)."""
    out = _git(["log", "--pretty=format:%H%x1f%ad%x1f%s%x1f%b", "--date=short"])
    commits: list[Commit] = []
    for record in out.split("\x1f\n"):
        if not record.strip():
            continue
        parts = record.split("\x1f", 3)
        if len(parts) < 3:
            continue
        sha, date, subject = parts[0], parts[1], parts[2]
        body = parts[3].strip() if len(parts) > 3 else ""
        commits.append(Commit(sha=sha, subject=subject, date=date, body=body))
    return commits


def commit_diff(sha: str) -> str:
    """The real unified diff of one commit."""
    return _git(["show", "--format=", "--unified=3", sha])


def pick_commit(index: int) -> tuple[Commit, str]:
    """Fetch a commit by index (clamped) plus its diff."""
    commits = list_commits()
    if not commits:
        raise RuntimeError("no commits found")
    clamped = max(0, min(index, len(commits) - 1))
    commit = commits[clamped]
    return commit, commit_diff(commit.sha)
