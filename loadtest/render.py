"""Load test tab: spec -> compiled k6 JS -> real execution -> chart.

The k6 script is *generated* from a Python dataclass, syntax-checked with
node when available, and the execution is a genuine load test from Python
(threaded virtual users hitting this very server) or a deterministic
offline fixture. The report is always labelled with its source.
"""

import shutil
import subprocess  # nosec B404 - running the local node binary is this module's job
import tempfile
from pathlib import Path

from nicegui import run, ui

from loadtest import generate, report, simulator
from loadtest.spec import LoadSpec

NODE = shutil.which("node")


def _node_check(js: str) -> tuple[bool, str]:
    if NODE is None:
        return False, "node not found - skipped (script still validated structurally)"
    with tempfile.TemporaryDirectory() as tmp:
        mjs = Path(tmp) / "check.mjs"
        mjs.write_text(js, encoding="utf-8")
        proc = subprocess.run(  # nosec B603 - fixed argv, no shell, node on our own file
            [NODE, "--check", str(mjs)],
            shell=False,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        detail = proc.stderr.strip() or proc.stdout.strip() or "syntax OK"
        return proc.returncode == 0, detail


def _render_artifact(
    js: str,
    problems: list[str],
    node_ok: bool,
    node_detail: str,
    target: ui.column,
) -> None:
    """Show the compiled script as a compact artifact, not a page-filling dump."""
    target.clear()
    preview = "\n".join(js.splitlines()[:2])
    with (
        target,
        ui.column().classes("w-full gap-2 rounded border border-gray-200 bg-gray-50 p-3"),
    ):
        with ui.row().classes("items-center gap-2 flex-wrap w-full"):
            ui.label("generated/k6/load.js").classes("font-mono text-base font-semibold")
            ui.label("compiled by Python · do not edit").classes("text-base text-gray-400")
            if problems:
                ui.label("structural fail").classes(
                    "text-base uppercase tracking-wide rounded px-1.5 py-0.5 bg-red-50 text-red-800"
                )
            else:
                ui.label("structural OK").classes(
                    "text-base uppercase tracking-wide rounded px-1.5 py-0.5 "
                    "bg-green-50 text-green-800"
                )
            node_style = "bg-green-50 text-green-800" if node_ok else "bg-amber-50 text-amber-800"
            ui.label(f"node --check: {node_detail}").classes(
                f"text-base rounded px-1.5 py-0.5 {node_style}"
            )
        ui.label(preview).classes("font-mono text-base text-gray-600 whitespace-pre-wrap")
        if problems:
            for problem in problems:
                ui.label(problem).classes("text-base text-red-700")
        with ui.expansion("full compiled script").classes("w-full"):
            ui.code(js, language="javascript").classes("w-full text-base max-h-64 overflow-auto")


def _render_stats(result: report.LoadReport, target: ui.column) -> None:
    target.clear()
    with target:
        with ui.row().classes("gap-3 flex-wrap"):
            for label, value in (
                ("requests", f"{result.total_requests}"),
                ("failed", f"{result.failed_requests}"),
                ("error rate", f"{result.error_rate:.2%}"),
                ("avg", f"{result.avg_ms:.1f} ms"),
                ("p95", f"{result.p95_ms:.1f} ms"),
                ("max", f"{result.max_ms:.1f} ms"),
            ):
                with ui.card().classes("p-3 gap-0.5 min-w-24"):
                    ui.label(label).classes("text-base uppercase text-gray-400")
                    ui.label(value).classes("text-lg font-bold")
        with ui.row().classes("items-center gap-2"):
            ui.icon("science", size="1.25rem").classes("text-gray-400")
            source_note = {
                "python simulator": "real HTTP from this process against this server",
                "offline fixture": "deterministic, no network — not a live run",
                "k6": "the k6 binary hitting this server",
            }.get(result.source, "labelled so the origin is never implied")
            ui.label(f"source: {result.source} — {source_note}").classes("text-base text-gray-500")
        if result.series:
            points = list(result.series)
            ui.echart(
                {
                    "legend": {"data": ["avg ms", "VUs"]},
                    "xAxis": {"type": "category", "data": [f"{p.t_s:.0f}s" for p in points]},
                    "yAxis": [
                        {"type": "value", "name": "ms"},
                        {"type": "value", "name": "VUs", "splitLine": {"show": False}},
                    ],
                    "series": [
                        {
                            "name": "avg ms",
                            "type": "line",
                            "smooth": True,
                            "data": [round(p.avg_ms, 1) for p in points],
                            "markLine": {
                                "data": [
                                    {"yAxis": round(result.p95_ms, 1), "name": "p95"},
                                ]
                            },
                        },
                        {
                            "name": "VUs",
                            "type": "line",
                            "yAxisIndex": 1,
                            "data": [p.vus for p in points],
                        },
                    ],
                    "tooltip": {"trigger": "axis"},
                }
            ).classes("w-full h-56")
            ui.label(
                "Avg latency (ms) and virtual users, one point per second. "
                "The dashed mark is measured p95."
            ).classes("text-base text-gray-500")


def build_loadtest_tab() -> None:
    """Build the Load Test tab."""
    with ui.card().classes("w-full p-4 gap-3"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("speed", size="1.5rem")
            ui.label("Load test").classes("text-lg font-bold")
        ui.label(
            "A Python LoadSpec compiles to k6 JavaScript and hits /api/health. Real k6 "
            "if installed, a labelled Python simulator if not. The chart names its source."
        ).classes("ilp-lede")

        with ui.grid(columns=6).classes("w-full gap-2 items-end"):
            vus = ui.number("VUs", value=4, min=1, max=64).props("dense outlined")
            ramp_up = ui.number("ramp up (s)", value=2, min=0, max=30).props("dense outlined")
            hold = ui.number("hold (s)", value=6, min=0, max=60).props("dense outlined")
            ramp_down = ui.number("ramp down (s)", value=2, min=0, max=30).props("dense outlined")
            p95 = ui.number("p95 target (ms)", value=250, min=10).props("dense outlined")
            err = ui.number("error budget", value=0.05, min=0.01, max=1, step=0.01).props(
                "dense outlined"
            )

        def make_spec() -> LoadSpec:
            return LoadSpec(
                vus=int(vus.value or 4),
                ramp_up_s=int(ramp_up.value or 2),
                hold_s=int(hold.value or 6),
                ramp_down_s=int(ramp_down.value or 2),
                p95_ms=int(p95.value or 250),
                error_rate=float(err.value or 0.05),
            )

        with ui.column().classes("w-full gap-2") as code_box:
            pass

        def compile_script() -> None:
            spec = make_spec()
            js = generate.compile_js(spec)
            problems = generate.validate_structure(js, spec)
            node_ok, node_detail = _node_check(js)
            _render_artifact(js, problems, node_ok, node_detail, code_box)

        with ui.column().classes("w-full gap-3") as results:
            pass

        async def run_live() -> None:
            results.clear()
            with results:
                ui.spinner(size="lg")
                ui.label(
                    f"Running a real load test against {make_spec().target_url} - a few seconds..."
                ).classes("text-base")
            spec = make_spec()
            ndjson = await run.io_bound(simulator.http_simulate, spec)
            if ndjson is None:
                results.clear()
                with results:
                    ui.label(
                        "The load test was cancelled or returned no data - nothing to chart."
                    ).classes("text-base text-amber-800")
                return
            _render_stats(report.parse_ndjson(ndjson, source="python simulator"), results)

        def run_fixture() -> None:
            ndjson, _ = simulator.offline_fixture(seed=7)
            _render_stats(report.parse_ndjson(ndjson, source="offline fixture"), results)

        with ui.row().classes("gap-2 flex-wrap"):
            ui.button("Compile k6 script from spec", on_click=compile_script, icon="build").props(
                "outline dense"
            )
            ui.button("Run live load test", on_click=run_live, icon="rocket_launch").props("dense")
            ui.button(
                "Run offline fixture (deterministic)", on_click=run_fixture, icon="science"
            ).props("dense outline")

        # Compile once on load so the generated script is visible immediately.
        ui.timer(0.4, compile_script, once=True)
