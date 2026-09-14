"""Explain tab: everything in plain English.

No new logic here - this mode re-uses the translator over real data:
the last telemetry report (or a fresh one) and any commit's real diff.
"""

from nicegui import run, ui

from explain.translator import explain_diff, explain_tool
from panel import telemetry
from review import store

TOOL_GLOSSARY = (
    (
        "ruff format",
        "Checks that every file is formatted the one right way. We check, we never rewrite.",
    ),
    ("ruff check", "Static analysis: unused imports, bugs-in-waiting, modern syntax."),
    ("mypy --strict", "Type checking at maximum strictness. The whole codebase is annotated."),
    ("pytest --cov", "Runs the real test suite and measures which lines the tests actually touch."),
    ("radon cc", "Cyclomatic complexity per function. A and B are simple; D and E are spaghetti."),
    ("bandit", "Security linting: SQL injection, shell tricks, bad randomness, and friends."),
    ("pip-audit", "Cross-checks installed packages against the CVE database. Needs network."),
    ("lang-audit", "Our own guard: the only non-Python source allowed is stuff Python generated."),
)


def _glossary() -> None:
    with ui.card().classes("w-full p-4 gap-3"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("menu_book", size="1.5rem")
            ui.label("What each tool actually does").classes("text-lg font-bold")
        for name, what in TOOL_GLOSSARY:
            with ui.row().classes("items-start gap-3 w-full"):
                ui.label(name).classes("w-40 shrink-0 font-mono text-base font-bold")
                ui.label(what).classes("text-base text-gray-600")


def _explanation_lines(report: telemetry.TelemetryReport) -> list[str]:
    lines = []
    for tool in report.tools:
        lines.append(explain_tool(tool.name, tool.status, tool.detail))
    if report.coverage_pct is not None:
        lines.append(
            f"Overall, the tests exercise {report.coverage_pct:.0f}% of the code - "
            "the rest is UI glue and entry points, deliberately outside coverage."
        )
    if report.complexity is not None:
        counts = telemetry.complexity_detail(report.complexity)
        lines.append(f"Complexity looks like this: {counts}. Simple is a feature.")
    return lines


async def _show_latest_quality(content: ui.column) -> None:
    content.clear()
    with content:
        ui.spinner(size="md")
        ui.label("Reading the latest quality report (or running one fresh)...").classes("text-base")
    cached = telemetry.load_report()
    if cached is not None:
        report: telemetry.TelemetryReport = cached
    else:
        fresh = await run.io_bound(telemetry.collect)
        if fresh is None:
            content.clear()
            with content:
                ui.label("No cached report and the fresh run was cancelled.").classes(
                    "text-base text-amber-800"
                )
            return
        report = fresh
        telemetry.write_report(report)
    content.clear()
    with content:
        for line in _explanation_lines(report):
            with ui.row().classes("gap-2 items-start"):
                ui.icon("translate", size="1.25rem").classes("text-gray-400 mt-0.5")
                ui.label(line).classes("text-base")


def _build_commit_explainer() -> None:
    commits = store.list_commits()
    options = {commit.sha: f"{commit.sha}  {commit.subject}" for commit in commits}
    selector = ui.select(options, value=next(iter(options)), label="commit").classes("flex-grow")

    with ui.column().classes("w-full gap-2") as content:
        pass

    def explain_selected() -> None:
        diff = store.commit_diff(selector.value)
        content.clear()
        with content:
            for bullet in explain_diff(diff):
                with ui.row().classes("gap-2 items-start"):
                    ui.icon("minimize", size="1.25rem").classes("text-gray-400 mt-0.5")
                    ui.label(bullet).classes("text-base")

    ui.button("Explain this commit", on_click=explain_selected, icon="auto_awesome").props(
        "dense outline"
    )
    ui.timer(0.4, explain_selected, once=True)


def build_explain_tab() -> None:
    """Build the Explain tab."""
    ui.label(
        "Quality reports and commit diffs in plain English. Same data as those tabs "
        "— legible, not re-measured."
    ).classes("ilp-lede")
    _glossary()
    with ui.card().classes("w-full p-4 gap-3"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("translate", size="1.5rem")
            ui.label("The quality run, in plain English").classes("text-lg font-bold")
        with ui.column().classes("w-full gap-2") as quality_content:
            pass
        ui.timer(0.6, lambda: _show_latest_quality(quality_content), once=True)
    with ui.card().classes("w-full p-4 gap-3"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("commit", size="1.5rem")
            ui.label("Any commit, in plain English").classes("text-lg font-bold")
        _build_commit_explainer()
