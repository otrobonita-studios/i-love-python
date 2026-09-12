"""An "ask git" session: debugging the heart-curve bug against real history.

The session is a guided conversation. Each step is a question a developer
might ask, a real git command, and a plain-English explanation of why that
command answers the question. Outputs are produced by actually running git
on this repo - the planted bug (commit that dropped -cos(4t)) really exists
in the history, so `git log -S` genuinely finds it.
"""

from __future__ import annotations

import shlex
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SEARCH_TERM = "math.cos(4.0 * t)"


@dataclass(frozen=True)
class Step:
    """One question in the ask-git session."""

    prompt: str
    display_command: str
    explanation: str
    resolve_command: Callable[[list[str]], str] | None = None


@dataclass(frozen=True)
class StepResult:
    """A step with its real, executed output."""

    step: Step
    command: str
    output: str


def _git(args: list[str]) -> str:
    proc = subprocess.run(  # nosec B603 - fixed argv, no shell, git in our own repo
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


def _resolve_show(prior_outputs: list[str]) -> str:
    first_line = (prior_outputs[1].splitlines() or [""])[0]
    sha = first_line.split()[0] if first_line.strip() else "HEAD"
    return f"git show {sha} -- art/heart.py"


def _resolve_blame(_prior_outputs: list[str]) -> str:
    source = (ROOT / "art" / "heart.py").read_text(encoding="utf-8")
    for i, line in enumerate(source.splitlines(), start=1):
        if "cos(4.0 * t)" in line:
            return f"git blame -L {i},{i} art/heart.py"
    return "git log -1 --oneline -- art/heart.py"


def build_steps() -> tuple[Step, ...]:
    """The four questions, in order."""
    return (
        Step(
            prompt="The heart renders wrong - the top looks off. Where do I start?",
            display_command="git log --oneline -- art/heart.py",
            explanation="Look at the file's own history, newest first. Scope it to one file.",
            resolve_command=lambda _outputs: "git log --oneline -- art/heart.py",
        ),
        Step(
            prompt="The formula should have a fourth cosine term. Which commit changed that?",
            display_command=f"git log -S '{SEARCH_TERM}' --oneline -- art/heart.py",
            explanation=(
                "-S finds commits where the number of occurrences of the term changed - "
                "exactly the commit that added or removed it."
            ),
            resolve_command=lambda _outputs: (
                f"git log -S '{SEARCH_TERM}' --oneline -- art/heart.py"
            ),
        ),
        Step(
            prompt="Show me exactly what that commit did.",
            display_command="git show <sha> -- art/heart.py",
            explanation="Read the real diff: what changed, and against which version.",
            resolve_command=_resolve_show,
        ),
        Step(
            prompt="And who owns that line now?",
            display_command="git blame -L <n>,<n> art/heart.py",
            explanation="Blame maps each line to its last commit - accountability, not blame.",
            resolve_command=_resolve_blame,
        ),
    )


def run_session() -> list[StepResult]:
    """Execute the whole session against the real repo, step by step."""
    outputs: list[str] = []
    results: list[StepResult] = []
    for step in build_steps():
        command = (
            step.display_command if step.resolve_command is None else step.resolve_command(outputs)
        )
        argv = shlex.split(command)
        output = _git(argv[1:] if argv and argv[0] == "git" else argv)
        outputs.append(output)
        results.append(
            StepResult(step=step, command=command, output=output.rstrip() or "(no output)")
        )
    return results
