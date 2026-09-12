"""Commit timelines: this repo's real history vs. a deliberately bad one.

The panel shows both side by side. The real timeline is read from `git log`
(including the Manifest: trailers that trace every commit to a spec line).
The bad timeline is synthetic, with an explicit reason for each sin.
"""

from __future__ import annotations

import re
import shutil
import subprocess  # nosec B404 - running the local git binary is this module's job
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TRAILER_RE = re.compile(r"^Manifest:\s*(.+)$", re.MULTILINE)


@dataclass(frozen=True)
class TimelineEntry:
    """One commit shown on the timeline."""

    sha: str
    subject: str
    date: str
    manifest: tuple[str, ...]
    quality: str  # "good" | "bad"
    reason: str


GIT = shutil.which("git")


def _git_log() -> str:
    if GIT is None:
        raise RuntimeError("git executable not found on this machine")
    proc = subprocess.run(  # nosec B603 - fixed argv, no shell, git in our own repo
        [GIT, "log", "--pretty=format:%x00%H%x1f%ad%x1f%s%x1f%b", "--date=short"],
        cwd=ROOT,
        shell=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"git log failed: {proc.stderr.strip()}")
    return proc.stdout


def real_timeline() -> list[TimelineEntry]:
    """This repo's actual history, newest first, with Manifest trailers."""
    entries: list[TimelineEntry] = []
    for record in _git_log().split("\x00"):
        if not record.strip():
            continue
        parts = record.split("\x1f", 3)
        if len(parts) < 3:
            continue
        sha, date, subject = parts[0], parts[1], parts[2]
        body = parts[3] if len(parts) > 3 else ""
        manifests = tuple(m.strip() for m in TRAILER_RE.findall(body))
        good = bool(manifests)
        entries.append(
            TimelineEntry(
                sha=sha[:7],
                subject=subject,
                date=date,
                manifest=manifests,
                quality="good" if good else "bad",
                reason="has a Manifest: trailer tracing it to the spec"
                if good
                else "missing a Manifest: trailer",
            )
        )
    return entries


def bad_timeline() -> list[TimelineEntry]:
    """A synthetic example of how NOT to commit, with the sin named."""
    return [
        TimelineEntry(
            sha="0000000",
            subject="update",
            date="n/a",
            manifest=(),
            quality="bad",
            reason="no description - future you will not know what changed",
        ),
        TimelineEntry(
            sha="0000000",
            subject="fix",
            date="n/a",
            manifest=(),
            quality="bad",
            reason="fixes what? for whom? which symptom?",
        ),
        TimelineEntry(
            sha="0000000",
            subject="WIP",
            date="n/a",
            manifest=(),
            quality="bad",
            reason="unfinished work committed as if it were done",
        ),
        TimelineEntry(
            sha="0000000",
            subject="fix(2)",
            date="n/a",
            manifest=(),
            quality="bad",
            reason="patch-on-patch instead of one atomic change",
        ),
        TimelineEntry(
            sha="0000000",
            subject="revert 'fix(2)'",
            date="n/a",
            manifest=(),
            quality="bad",
            reason="revert-happy history: the real fix never landed",
        ),
        TimelineEntry(
            sha="0000000",
            subject="misc changes + big feature + style + bugfix",
            date="n/a",
            manifest=(),
            quality="bad",
            reason="four commits in one - bisecting and review become impossible",
        ),
    ]
