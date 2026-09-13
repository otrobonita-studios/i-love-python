"""Quality panel UI: real tool output, honestly shown.

Everything on this screen is produced by the real tools (ruff, mypy,
pytest, radon, bandit, pip-audit, lang-audit). If a tool fails or is
unavailable, the panel says so - it never paints a green picture.
"""

from nicegui import run, ui

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
        f"rounded px-2 py-0.5 text-xs font-bold {_status_style(status)}"
    )


def _tool_card(result: telemetry.ToolResult) -> None:
    icon = "verified" if result.status == "pass" else "report_problem"
    with ui.card().classes("w-full gap-1 p-3"):
        with ui.row().classes("items-center justify-between w-full gap-2"):
            with ui.row().classes("items-center gap-2"):
                ui.icon(icon).classes("text-xl")
                ui.label(result.name).classes("font-semibold")
            _badge(result.status)
        ui.label(result.detail).classes("text-xs text-gray-600 w-full break-words")
        ui.label(result.command).classes("text-[10px] text-gray-400 w-full font-mono break-all")
        ui.label(f"{result.duration_ms} ms").classes("text-[10px] text-gray-400")
        with ui.expansion("plain english").classes("w-full text-xs"):
            ui.label(explain_tool(result.name, result.status, result.detail))


def _render_report(report: telemetry.TelemetryReport, content: ui.column) -> None:
    content.clear()
    with content:
        with ui.row().classes("items-center gap-4 text-sm text-gray-500"):
            ui.label(f"Python {report.python}")
            ui.label(f"generated {report.generated_at}")

        with ui.grid(columns=2).classes("w-full gap-3"):
            for result in report.tools:
                _tool_card(result)

        with ui.card().classes("w-full p-3 gap-2"):
            ui.label("Coverage by file (real pytest --cov run)").classes("font-semibold text-sm")
            if report.coverage_files:
                for file in report.coverage_files:
                    with ui.row().classes("items-center gap-3 w-full"):
                        ui.label(file.path).classes("w-56 truncate font-mono text-xs")
                        ui.linear_progress(value=file.pct / 100.0, show_value=False).classes(
                            "flex-grow"
                        )
                        ui.label(f"{file.covered}/{file.total} ({file.pct:.1f}%)").classes(
                            "w-28 text-right text-xs"
                        )
            else:
                ui.label("No coverage data - see the pytest result above for why.").classes(
                    "text-xs"
                )
            with ui.row().classes("items-center gap-3 w-full"):
                ui.label("Overall").classes("font-semibold text-sm")
                ui.linear_progress(
                    value=(report.coverage_pct / 100.0) if report.coverage_pct else 0.0,
                    show_value=False,
                ).classes("flex-grow")
                label = f"{report.coverage_pct:.1f}%" if report.coverage_pct is not None else "n/a"
                ui.label(label).classes("w-28 text-right text-sm font-semibold")

        with ui.card().classes("w-full p-3 gap-2"):
            ui.label("Complexity (real radon cc run)").classes("font-semibold text-sm")
            if report.complexity is not None:
                ui.label(telemetry.complexity_detail(report.complexity)).classes(
                    "text-sm font-mono"
                )
            else:
                ui.label("Complexity data unavailable.").classes("text-xs")

        with ui.card().classes("w-full p-3 gap-1"):
            ui.label("The honest summary").classes("font-semibold text-sm")
            failed = [t for t in report.tools if t.status == "fail"]
            unavailable = [t for t in report.tools if t.status == "unavailable"]
            if not failed and not unavailable:
                ui.label("Every tool passed. Nothing is simulated - this is their actual output.")
            else:
                for tool in failed:
                    ui.label(f"{tool.name}: {tool.detail}")
                for tool in unavailable:
                    ui.label(f"{tool.name}: {tool.detail}")
                ui.label("These are real failures or limitations, shown as-is. No fakes.").classes(
                    "text-xs"
                )


async def _refresh(content: ui.column) -> None:
    """Re-run the whole quality stack in a worker thread and re-render."""
    content.clear()
    with content, ui.row().classes("items-center gap-3 w-full"):
        ui.spinner(size="lg")
        ui.label("Running the real quality stack (ruff, mypy, pytest, radon, bandit, pip-audit)...")
    collected = await run.io_bound(telemetry.collect)
    if collected is None:
        content.clear()
        with content:
            ui.label("The quality run was cancelled - re-run it when ready.").classes(
                "text-xs text-amber-300"
            )
        return
    telemetry.write_report(collected)
    _render_report(collected, content)


def build_panel() -> None:
    """Build the Quality tab and start with a real collection run."""
    with ui.card().classes("w-full p-4 gap-3"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("monitoring").classes("text-2xl")
            ui.label("Quality telemetry").classes("text-lg font-bold")
        with ui.column().classes("w-full gap-3") as content:
            pass
        ui.button(
            "Re-run quality stack",
            on_click=lambda: _refresh(content),
            icon="refresh",
        ).props("outline dense")
    # Initial load: real collection, honestly rendered.
    ui.timer(0.4, lambda: _refresh(content), once=True)


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
