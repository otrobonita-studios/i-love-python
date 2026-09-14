"""Git tab: the ask-git console and the commit timelines.

The console runs REAL git commands against this repo as you click through
the questions - including the genuine `git log -S` hunt for the planted
heart-curve bug. The timelines show this repo's actual history next to a
made-up bad one, so the difference is visible.
"""

import shlex
from dataclasses import dataclass, field

from nicegui import ui

from git_discipline import console, timeline


@dataclass
class _Session:
    """Client-side state for one ask-git session."""

    steps: tuple[console.Step, ...] = field(default_factory=console.build_steps)
    index: int = 0
    prior_outputs: list[str] = field(default_factory=list)
    finished: bool = False


def _execute_step(session: _Session) -> console.StepResult:
    step = session.steps[session.index]
    if step.resolve_command is None:
        command = step.display_command
    else:
        command = step.resolve_command(session.prior_outputs)
    argv = shlex.split(command)
    output = console._git(argv[1:] if argv and argv[0] == "git" else argv)
    session.prior_outputs.append(output)
    session.index += 1
    if session.index >= len(session.steps):
        session.finished = True
    return console.StepResult(step=step, command=command, output=output.rstrip() or "(no output)")


def _render_entry(entry: timeline.TimelineEntry, content: ui.column) -> None:
    good = entry.quality == "good"
    icon = "verified" if good else "report_problem"
    with ui.row().classes(
        f"items-start gap-2 w-full rounded p-2 {'bg-green-50' if good else 'bg-red-50'}"
    ):
        ui.icon(icon, size="1.25rem").classes("mt-0.5")
        with ui.column().classes("gap-0.5 flex-grow"):
            with ui.row().classes("gap-2 items-center"):
                ui.label(entry.sha).classes("font-mono text-base text-gray-500")
                ui.label(entry.subject).classes("text-base font-medium")
                ui.label(entry.date).classes("text-base text-gray-400")
            ui.label(entry.reason).classes("text-base text-gray-500")
            for manifest in entry.manifest:
                ui.label(f"Manifest: {manifest}").classes(
                    "text-base font-mono rounded bg-white px-1.5 py-0.5 text-gray-600"
                )


def _build_console() -> None:
    session = _Session()
    with ui.card().classes("w-full p-4 gap-3"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("terminal", size="1.5rem")
            ui.label("Ask git").classes("text-lg font-bold")
        ui.label(
            "A guided ask-git walk through a real bug in this history (the missing "
            "heart-curve term), using real git commands. Bisect is a documented gap."
        ).classes("ilp-lede")
        with ui.column().classes("w-full gap-2") as transcript:
            pass
        with ui.row().classes("gap-2") as actions:
            pass

    def ask() -> None:
        if session.finished:
            return
        result = _execute_step(session)
        with transcript, ui.column().classes("ilp-console-step"):
            ui.label(f"you: {result.step.prompt}").classes("ilp-console-you")
            ui.label(f"$ {result.command}").classes("ilp-console-cmd")
            ui.label(result.output).classes("ilp-console-out")
            ui.label(f"why: {result.step.explanation}").classes("ilp-console-why")
        actions.clear()
        with actions:
            if session.finished:
                ui.label("Session complete — every command above really ran on this repo.").classes(
                    "text-base text-green-800"
                )
                ui.button("Restart session", on_click=restart, icon="replay").props("flat dense")
            else:
                ui.button("Ask git", on_click=ask, icon="send").props("dense outline")

    def restart() -> None:
        nonlocal session
        session = _Session()
        transcript.clear()
        ask()

    ask()


def _build_timelines() -> None:
    with ui.card().classes("w-full p-4 gap-3"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("timeline", size="1.5rem")
            ui.label("Commit timelines").classes("text-lg font-bold")
        ui.label(
            "This repo's commits next to a labelled-bad timeline. Same shape, different discipline."
        ).classes("ilp-lede")
        ui.label("Green is this checkout. Red is fiction, labelled as such.").classes(
            "text-base text-gray-500"
        )
        with ui.grid(columns=2).classes("w-full gap-4"):
            with ui.column().classes("w-full gap-1"):
                ui.label("this repo (real)").classes("font-semibold text-green-800")
                with ui.column().classes("w-full gap-1 max-h-96 overflow-auto") as real_content:
                    for entry in timeline.real_timeline():
                        _render_entry(entry, real_content)
            with ui.column().classes("w-full gap-1"):
                ui.label("bad example").classes("font-semibold text-red-800")
                with ui.column().classes("w-full gap-1 max-h-96 overflow-auto") as bad_content:
                    for entry in timeline.bad_timeline():
                        _render_entry(entry, bad_content)


def build_git_tab() -> None:
    """Build the Git discipline tab (console + timelines)."""
    _build_console()
    _build_timelines()
