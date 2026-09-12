"""Three deterministic review personas.

Each persona has a narrow, explainable rulebook. Given a unified diff they
produce a verdict (ok / caution / block) plus a one-line note. The same diff
always gets the same review - no LLM, no mood, no fakes.
"""

from __future__ import annotations

from dataclasses import dataclass

from explain.translator import DiffStats, extract_diff_stats

TONE_OK = "ok"
TONE_CAUTION = "caution"
TONE_BLOCK = "block"

_TONE_RANK = {TONE_OK: 0, TONE_CAUTION: 1, TONE_BLOCK: 2}


@dataclass(frozen=True)
class Verdict:
    """One persona's call on a diff."""

    persona: str
    tone: str
    note: str


@dataclass(frozen=True)
class Review:
    """All persona verdicts plus a consensus."""

    commit: str
    verdicts: tuple[Verdict, ...]
    consensus_tone: str
    consensus_note: str


def purist(stats: DiffStats, diff: str) -> Verdict:
    """Cares about the pure-Python rule and commit shape."""
    if stats.non_python_files:
        if "GENERATED" in diff:
            return Verdict(
                "Purist", TONE_OK, "Non-Python file, but it declares itself GENERATED - acceptable."
            )
        return Verdict(
            "Purist",
            TONE_CAUTION,
            "Hand-authored non-Python source? That violates the pure-Python rule.",
        )
    if stats.files > 6:
        return Verdict("Purist", TONE_CAUTION, "More than six files in one commit - split it up.")
    if not stats.touches_tests and stats.added + stats.removed > 40:
        return Verdict(
            "Purist", TONE_CAUTION, "A sizeable change with no test changes - where is the proof?"
        )
    return Verdict("Purist", TONE_OK, "Clean, Python-first diff. No style sins visible.")


def skeptic(diff: str) -> Verdict:
    """Cares about dangerous patterns."""
    if "eval(" in diff or "exec(" in diff:
        return Verdict("Skeptic", TONE_BLOCK, "Dynamic code execution in the diff. Not happening.")
    if "os.system(" in diff or "shell=True" in diff:
        return Verdict(
            "Skeptic", TONE_CAUTION, "Shell invocation spotted - why not a fixed argv list?"
        )
    if "subprocess." in diff:
        return Verdict(
            "Skeptic", TONE_OK, "Subprocess use, but with fixed arguments - acceptable here."
        )
    if len(diff) < 2000:
        return Verdict("Skeptic", TONE_OK, "Too small to be dangerous. Approving, grudgingly.")
    return Verdict(
        "Skeptic", TONE_OK, "No dangerous patterns found. I still watched it the whole time."
    )


def pragmatist(stats: DiffStats) -> Verdict:
    """Cares about shipping safely and quickly."""
    if stats.touches_tests:
        return Verdict("Pragmatist", TONE_OK, "Tests came along - that lowers the risk. Ship it.")
    if stats.removed > stats.added and stats.removed > 20:
        return Verdict(
            "Pragmatist", TONE_OK, "Mostly deletions - usually the safest kind of change."
        )
    if stats.added > 300:
        return Verdict(
            "Pragmatist", TONE_CAUTION, "Big diff - review it in two passes before merging."
        )
    return Verdict("Pragmatist", TONE_OK, "Small and focused. Ship it and learn from it.")


def review_diff(diff: str, commit: str = "") -> Review:
    """Run all three personas over a diff and form a consensus."""
    stats = extract_diff_stats(diff)
    verdicts = (purist(stats, diff), skeptic(diff), pragmatist(stats))
    worst = max(_TONE_RANK[v.tone] for v in verdicts)
    consensus_tone = (TONE_OK, TONE_CAUTION, TONE_BLOCK)[worst]
    if consensus_tone == TONE_OK:
        consensus_note = "All three agree: this is fine to ship."
    elif consensus_tone == TONE_CAUTION:
        consensus_note = "One of us is worried - read the caution before merging."
    else:
        consensus_note = "A hard stop. Fix it and bring it back."
    return Review(
        commit=commit,
        verdicts=verdicts,
        consensus_tone=consensus_tone,
        consensus_note=consensus_note,
    )
