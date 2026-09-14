"""Explain tab: everything in plain English.

No new logic here - this mode re-uses the translator over real data:
the last telemetry report (or a fresh one) and any commit's real diff.
The letter and field guide only typeset explain/letter.py and glossary.py.
"""

from __future__ import annotations

from nicegui import run, ui

from explain import glossary, letter
from explain import zen as zen_mod
from explain.translator import explain_diff, explain_tool
from panel import telemetry
from review import store


def _paragraph(text: str, *, link_tools: bool = False) -> None:
    ui.html(f"<p>{letter.typeset_html(text, link_tools=link_tools)}</p>", sanitize=False)


def _import_this() -> None:
    with ui.row().classes("ilp-this-row items-center gap-3 w-full"):
        with ui.element("div").classes("ilp-this-well"):
            ui.label(">>> import this").classes("ilp-mono")
        btn = ui.button("Execute", icon="play_arrow")
    output = ui.column().classes("w-full gap-2")
    caption = ui.label(letter.IDLE_CAPTION).classes("ilp-this-caption")

    def run() -> None:
        output.clear()
        with output:
            ui.label(zen_mod.zen_of_python()).classes("ilp-zen-out")
        caption.set_text(letter.ZEN_CAPTION)
        btn.set_text("Again")
        btn.props("icon=replay")

    btn.on_click(run)


def build_intro() -> None:
    """House letter of introduction above the room cards. Canonical copy."""
    from explain import intro

    with ui.element("section").classes("ilp-letter w-full"):
        ui.label(intro.KICKER).classes("ilp-letter-kicker")
        ui.label(intro.TITLE).classes("ilp-letter-title")
        for paragraph in intro.PARAGRAPHS:
            ui.html(f"<p>{intro.typeset_html(paragraph)}</p>", sanitize=False)
        for line in intro.SIGN_OFF:
            ui.label(line)
        ui.label(intro.PLAN_HEADING).classes("ilp-letter-title")
        ui.label(" → ".join(intro.STACK)).classes("ilp-mono")
        with ui.element("div").classes("ilp-card-grid"):
            for room in intro.ROOMS:
                with ui.card().classes("p-6 gap-2"):
                    ui.link(f"{room.number}  {room.name}", room.href).classes("ilp-nav-item")
                    ui.label(room.line)
                    ui.label(room.path).classes("ilp-mono")


def build_letter() -> None:
    """Typeset the love letter and the import-this control. No paraphrasing."""
    with ui.element("section").classes("ilp-letter w-full"):
        ui.label(letter.KICKER).classes("ilp-letter-kicker")
        ui.label(letter.TITLE).classes("ilp-letter-title")
        for paragraph in letter.PARAGRAPHS:
            _paragraph(paragraph)
        _import_this()
        _paragraph(letter.CLOSING, link_tools=True)


def build_field_guide() -> None:
    """Long-form glossary: what, why, docs. Deterministic, no LLM."""
    with ui.card().classes("w-full p-4 gap-3").props("id=field-guide"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("menu_book", size="1.5rem")
            ui.label("You do not have to already know these.").classes("text-lg font-bold")
        for guide in glossary.GUIDES:
            with ui.column().classes("w-full gap-1"):
                ui.label(f"{guide.name} · {guide.kind}").classes("font-semibold ilp-mono")
                ui.label(guide.what).classes("text-base")
                ui.label(guide.why).classes("text-base")
                ui.link("Official docs", guide.href, new_tab=True).classes("ilp-link").props(
                    "rel=noopener noreferrer"
                )


def _glossary() -> None:
    build_field_guide()


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
