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
        ui.icon(icon).classes("text-lg mt-0.5")
        with ui.column().classes("gap-0.5 flex-grow"):
            with ui.row().classes("gap-2 items-center"):
                ui.label(entry.sha).classes("font-mono text-xs text-gray-500")
                ui.label(entry.subject).classes("text-sm font-medium")
                ui.label(entry.date).classes("text-[10px] text-gray-400")
            ui.label(entry.reason).classes("text-xs text-gray-500")
            for manifest in entry.manifest:
                ui.label(f"Manifest: {manifest}").classes(
                    "text-[10px] font-mono rounded bg-white px-1.5 py-0.5 text-gray-600"
                )


def _build_console() -> None:
    session = _Session()
    with ui.card().classes("w-full p-4 gap-3"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("terminal").classes("text-2xl")
            ui.label("Ask git").classes("text-lg font-bold")
        ui.label(
            "The heart once rendered with a wrong top - the bug is real in this repo's history. "
            "Walk through how a developer finds it using nothing but git."
        ).classes("text-xs text-gray-500")
        with ui.column().classes("w-full gap-2") as transcript:
            pass
        with ui.row().classes("gap-2") as actions:
            pass

    def ask() -> None:
        if session.finished:
            return
        result = _execute_step(session)
        with transcript, ui.card().classes("w-full p-3 gap-2 bg-gray-900 text-gray-100"):
            ui.label(f"you: {result.step.prompt}").classes("text-xs text-gray-300")
            ui.label(f"$ {result.command}").classes("font-mono text-xs text-sky-300")
            ui.code(result.output, language="bash").classes(
                "text-xs max-h-48 overflow-auto bg-black/40 rounded p-2"
            )
            ui.label(f"why: {result.step.explanation}").classes("text-[11px] text-gray-400")
        actions.clear()
        with actions:
            if session.finished:
                ui.label("Session complete - every command above really ran on this repo.").classes(
                    "text-xs text-green-300"
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
            ui.icon("timeline").classes("text-2xl")
            ui.label("Commit timelines").classes("text-lg font-bold")
        with ui.tabs() as tabs:
            real_tab = ui.tab("this repo (real)", icon="verified")
            bad_tab = ui.tab("bad example", icon="report_problem")
        with ui.tab_panels(tabs, value=real_tab):
            with ui.tab_panel(real_tab), ui.column().classes("w-full gap-1") as real_content:
                for entry in timeline.real_timeline():
                    _render_entry(entry, real_content)
            with ui.tab_panel(bad_tab), ui.column().classes("w-full gap-1") as bad_content:
                for entry in timeline.bad_timeline():
                    _render_entry(entry, bad_content)
        ui.label(
            "Real history: atomic commits, each with a Manifest: trailer tracing it to the spec. "
            "Bad history: giant merges, no traceability. Same data structure, different discipline."
        ).classes("text-xs text-gray-500")


def build_git_tab() -> None:
    """Build the Git discipline tab (console + timelines)."""
    _build_console()
    _build_timelines()
