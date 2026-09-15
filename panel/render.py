"""Quality panel UI: real tool output, honestly shown.

Everything on this screen is produced by the real tools (ruff, mypy,
pytest, radon, bandit, pip-audit, lang-audit). If a tool fails or is
unavailable, the panel says so - it never paints a green picture.
"""

from nicegui import run, ui

from explain import glossary
from explain.translator import explain_tool
from panel import telemetry


def _status_word(status: str) -> str:
    if status == "pass":
        return "PASS"
    if status == "fail":
        return "FAIL"
    if status == "warn":
        return "WARN"
    if status == "unavailable":
        return "N/A"
    return status


def _status_style(status: str) -> str:
    if status == "pass":
        return "bg-green-100 text-green-800"
    if status == "fail":
        return "bg-red-100 text-red-800"
    if status == "warn":
        return "bg-amber-100 text-amber-800"
    if status == "unavailable":
        return "bg-gray-200 text-gray-600"
    return "bg-gray-100"


def _badge(status: str) -> None:
    ui.label(_status_word(status)).classes(
        f"rounded px-2 py-0.5 text-base font-bold {_status_style(status)}"
    )


def _tool_card(result: telemetry.ToolResult) -> None:
    guide = glossary.lookup(result.name)
    with ui.card().classes("w-full gap-2 p-6").props(f"id={glossary.tool_anchor(result.name)}"):
        with ui.row().classes("items-center justify-between w-full gap-2"):
            with ui.row().classes("items-center gap-2"):
                ui.label(result.name).classes("font-semibold")
                if guide is not None:
                    ui.label(guide.kind).classes("ilp-kind")
            _badge(result.status)
        ui.label(result.command).classes("text-base ilp-mono w-full break-all")
        if guide is not None:
            ui.label(guide.what).classes("text-base w-full")
        ui.label(f"This run. {result.detail}").classes("text-base w-full break-words")
        if guide is not None:
            ui.link("Official docs", guide.href, new_tab=True).classes("ilp-link").props(
                "rel=noopener noreferrer"
            )
        with ui.expansion("command and this run").classes("w-full"):
            ui.label(f"{result.duration_ms} ms").classes("text-base")
            ui.label(explain_tool(result.name, result.status, result.detail))


def _render_report(report: telemetry.TelemetryReport, content: ui.column) -> None:
    content.clear()
    with content:
        with ui.row().classes("items-center gap-4 text-base text-gray-500"):
            ui.label(f"Python {report.python}")
            ui.label(f"generated {report.generated_at}")

        with ui.element("div").classes("ilp-card-grid"):
            for result in report.tools:
                _tool_card(result)

            with ui.card().classes("w-full p-6 gap-2 ilp-card-span"):
                with ui.row().classes("items-center gap-2 flex-wrap"):
                    ui.label("Coverage by file (real pytest --cov run)").classes(
                        "font-semibold text-base"
                    )
                    ui.link("pytest-cov docs", glossary.PYTEST_COV_HREF, new_tab=True).classes(
                        "ilp-link"
                    ).props("rel=noopener noreferrer")
                if report.coverage_files:
                    for file in report.coverage_files:
                        with ui.row().classes("items-center gap-3 w-full"):
                            ui.label(file.path).classes("w-72 truncate font-mono text-base")
                            ui.linear_progress(value=file.pct / 100.0, show_value=False).classes(
                                "flex-grow"
                            )
                            ui.label(f"{file.covered}/{file.total} ({file.pct:.1f}%)").classes(
                                "w-28 text-right text-base"
                            )
                else:
                    ui.label("No coverage data - see the pytest result above for why.").classes(
                        "text-base"
                    )
                with ui.row().classes("items-center gap-3 w-full"):
                    ui.label("Overall").classes("font-semibold text-base")
                    ui.linear_progress(
                        value=(report.coverage_pct / 100.0) if report.coverage_pct else 0.0,
                        show_value=False,
                    ).classes("flex-grow")
                    label = (
                        f"{report.coverage_pct:.1f}%" if report.coverage_pct is not None else "n/a"
                    )
                    ui.label(label).classes("w-28 text-right text-base font-semibold")

            with ui.card().classes("w-full p-6 gap-2"):
                ui.label("Complexity (real radon cc run)").classes("font-semibold text-base")
                if report.complexity is not None:
                    ui.label(telemetry.complexity_detail(report.complexity)).classes(
                        "text-base font-mono"
                    )
                else:
                    ui.label("Complexity data unavailable.").classes("text-base")
                for rank, meaning in glossary.RADON_LEGEND:
                    ui.label(f"{rank} — {meaning}").classes("text-base")

            with ui.card().classes("w-full p-6 gap-1"):
                ui.label("The honest summary").classes("font-semibold text-base")
                failed = [t for t in report.tools if t.status == "fail"]
                unavailable = [t for t in report.tools if t.status == "unavailable"]
                if not failed and not unavailable:
                    ui.label(
                        "Every tool passed. Nothing is simulated - this is their actual output."
                    )
                else:
                    for tool in failed:
                        ui.label(f"{tool.name}: {tool.detail}")
                    for tool in unavailable:
                        ui.label(f"{tool.name}: {tool.detail}")
                    ui.label(
                        "These are real failures or limitations, shown as-is. No fakes."
                    ).classes("text-base")


async def _refresh(content: ui.column) -> None:
    """Re-run the whole quality stack in a worker thread and re-render."""
    content.clear()
    with content, ui.row().classes("items-center gap-3 w-full"):
        ui.spinner(size="lg")
        ui.label(
            "Running the real quality stack (ruff, mypy, pytest, radon, bandit, "
            "pip-audit, lang-audit)..."
        )
    collected = await run.io_bound(telemetry.collect)
    if collected is None:
        content.clear()
        with content:
            ui.label("The quality run was cancelled - re-run it when ready.").classes(
                "text-base text-amber-800"
            )
        return
    telemetry.write_report(collected)
    _render_report(collected, content)


def build_panel() -> None:
    """Build the Quality tab and start with a real collection run."""
    with ui.column().classes("w-full gap-6"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("monitoring", size="1.5rem")
            ui.label("Quality telemetry").classes("text-lg font-bold")
        ui.label(
            "Real ruff, mypy --strict, pytest --cov, radon, bandit, pip-audit, and "
            "lang-audit on this checkout. Re-run to watch the same commands CI runs. "
            "N/A means unavailable — never a fake pass. New to these names? Stay on "
            "the cards, or skip to the field guide."
        ).classes("ilp-lede")
        with ui.column().classes("w-full gap-6") as content:
            pass
        ui.button(
            "Re-run quality stack",
            on_click=lambda: _refresh(content),
            icon="refresh",
        ).props("outline")
        cached = telemetry.load_report()
        if cached is not None:
            _render_report(cached, content)
        else:
            ui.timer(0.4, lambda: _refresh(content), once=True)
    from explain.render import build_field_guide

    build_field_guide()


def register_api() -> None:
    """Expose the telemetry report as JSON (also the k6 load-test target)."""
    from nicegui import app

    @app.get("/api/telemetry")
    def telemetry_api() -> telemetry.TelemetryReport:
        cached = telemetry.load_report()
        if cached is not None:
            return cached
        report = telemetry.collect()
        telemetry.write_report(report)
        return report
