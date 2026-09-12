"""Telemetry: run the real toolchain and report what actually happened.

Every result in a TelemetryReport comes from a real subprocess. Nothing is
simulated: if a tool is missing, offline, or slow, the report says exactly
that, with an honest status ("unavailable" / "warn") instead of a fake pass.
"""

from __future__ import annotations

import concurrent.futures
import json
import subprocess  # nosec B404 - running the fixed local toolchain is the purpose of this module
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERATED_DIR = ROOT / "generated" / "telemetry"
PY = sys.executable

TOP_PACKAGES = (
    "art",
    "panel",
    "review",
    "git_discipline",
    "explain",
    "loadtest",
    "scripts",
)


def _existing_packages() -> tuple[str, ...]:
    return tuple(name for name in TOP_PACKAGES if (ROOT / name).is_dir())


@dataclass(frozen=True)
class ToolResult:
    """Outcome of one real tool run."""

    name: str
    command: str
    status: str  # "pass" | "fail" | "warn" | "unavailable"
    detail: str
    duration_ms: int = 0


@dataclass(frozen=True)
class CoverageFile:
    """Per-file coverage from the pytest/coverage JSON report."""

    path: str
    covered: int
    total: int
    pct: float


@dataclass(frozen=True)
class Complexity:
    """Radon cyclomatic-complexity rank counts (A is best, E is worst)."""

    a: int
    b: int
    c: int
    d: int
    e: int


@dataclass(frozen=True)
class TelemetryReport:
    """Everything the quality panel displays, from real tool runs."""

    tools: tuple[ToolResult, ...]
    coverage_pct: float | None
    coverage_files: tuple[CoverageFile, ...]
    complexity: Complexity | None
    python: str
    generated_at: str


def _tail(text: str, limit: int = 220) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    tail = " | ".join(lines[-4:])
    return tail if len(tail) <= limit else "…" + tail[-limit:]


def _run(cmd: list[str], timeout: int) -> tuple[int, str, float]:
    start = time.monotonic()
    proc = subprocess.run(  # nosec B603 - fixed argv list, no shell, no untrusted input
        cmd,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    return proc.returncode, proc.stdout + "\n" + proc.stderr, time.monotonic() - start


Parser = Callable[[int, str], tuple[str, str]]


def _tool(name: str, cmd: list[str], timeout: int, parse: Parser) -> ToolResult:
    """Run one tool, never raising: failures become honest statuses."""
    command = " ".join(cmd)
    try:
        rc, out, secs = _run(cmd, timeout)
    except FileNotFoundError:
        return ToolResult(name, command, "unavailable", "executable not found", 0)
    except subprocess.TimeoutExpired:
        return ToolResult(name, command, "warn", f"timed out after {timeout}s", timeout * 1000)
    except OSError as exc:
        return ToolResult(name, command, "unavailable", str(exc), 0)
    status, detail = parse(rc, out)
    return ToolResult(name, command, status, detail, int(secs * 1000))


# ---------------------------------------------------------------------------
# One runner per tool. Each parse() maps (rc, output) to (status, detail).
# ---------------------------------------------------------------------------


def run_ruff_format() -> ToolResult:
    return _tool(
        "ruff format",
        [PY, "-m", "ruff", "format", "--check", "."],
        60,
        lambda rc, out: ("pass", _tail(out, 80)) if rc == 0 else ("fail", _tail(out)),
    )


def run_ruff_lint() -> ToolResult:
    return _tool(
        "ruff lint",
        [PY, "-m", "ruff", "check", "."],
        60,
        lambda rc, out: ("pass", _tail(out, 80)) if rc == 0 else ("fail", _tail(out)),
    )


def run_mypy() -> ToolResult:
    targets = list(_existing_packages())
    if (ROOT / "app.py").is_file():
        targets.append("app.py")
    return _tool(
        "mypy --strict",
        [PY, "-m", "mypy", "--strict", *targets],
        180,
        lambda rc, out: ("pass", _tail(out, 100)) if rc == 0 else ("fail", _tail(out)),
    )


def _parse_coverage_json() -> tuple[float | None, tuple[CoverageFile, ...]]:
    path = GENERATED_DIR / "coverage.json"
    if not path.is_file():
        return None, ()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None, ()
    files = []
    for rel, summary in sorted(data.get("files", {}).items()):
        covered = summary.get("covered_lines", 0)
        total = summary.get("num_statements", 0)
        if total == 0:
            continue
        files.append(
            CoverageFile(path=rel, covered=covered, total=total, pct=100.0 * covered / total)
        )
    total_covered = data.get("totals", {}).get("covered_lines", 0)
    total_statements = data.get("totals", {}).get("num_statements", 0)
    pct = 100.0 * total_covered / total_statements if total_statements else None
    return pct, tuple(files)


def run_pytest() -> ToolResult:
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    result = _tool(
        "pytest --cov",
        [
            PY,
            "-m",
            "pytest",
            "-q",
            "--cov",
            f"--cov-report=json:{GENERATED_DIR / 'coverage.json'}",
        ],
        300,
        lambda rc, out: ("pass", _tail(out, 90)) if rc == 0 else ("fail", _tail(out)),
    )
    return result


def _parse_radon_rank(line: str) -> str | None:
    # radon cc line: "    F 25:0 heart_point - A"  (F=function, C=class)
    parts = line.split()
    if len(parts) >= 4 and parts[0] in ("F", "C") and parts[-2] == "-" and parts[-1] in "ABCDE":
        return parts[-1]
    return None


def parse_radon(output: str) -> Complexity | None:
    """Count cyclomatic-complexity ranks from radon cc output."""
    counts = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    for line in output.splitlines():
        rank = _parse_radon_rank(line)
        if rank:
            counts[rank] += 1
    if not any(counts.values()):
        return None
    return Complexity(**{key.lower(): value for key, value in counts.items()})


def complexity_detail(complexity: Complexity | None) -> str:
    if complexity is None:
        return "no ranked functions found"
    return f"A:{complexity.a} B:{complexity.b} C:{complexity.c} D:{complexity.d} E:{complexity.e}"


def _radon_pair() -> tuple[ToolResult, Complexity | None]:
    pkgs = list(_existing_packages())
    cmd = [PY, "-m", "radon", "cc", *pkgs]
    command = " ".join(cmd)
    try:
        rc, out, secs = _run(cmd, 60)
    except FileNotFoundError:
        return ToolResult("radon cc", command, "unavailable", "executable not found", 0), None
    except subprocess.TimeoutExpired:
        return ToolResult("radon cc", command, "warn", "timed out after 60s", 60000), None
    except OSError as exc:
        return ToolResult("radon cc", command, "unavailable", str(exc), 0), None
    complexity = parse_radon(out)
    ms = int(secs * 1000)
    if rc != 0:
        return ToolResult("radon cc", command, "warn", _tail(out), ms), complexity
    if complexity is None:
        return ToolResult("radon cc", command, "pass", "no ranked functions found", ms), None
    bad = complexity.d + complexity.e
    return ToolResult(
        "radon cc", command, "warn" if bad else "pass", complexity_detail(complexity), ms
    ), complexity


def run_radon() -> ToolResult:
    return _radon_pair()[0]


def run_bandit() -> ToolResult:
    pkgs = list(_existing_packages())

    def parse(rc: int, out: str) -> tuple[str, str]:
        if rc == 0:
            return "pass", "no issues identified"
        if rc == 1:
            return "fail", _tail(out)
        return "warn", _tail(out)

    return _tool("bandit -r", [PY, "-m", "bandit", "-q", "-r", *pkgs], 120, parse)


def run_pip_audit() -> ToolResult:
    def parse(rc: int, out: str) -> tuple[str, str]:
        if rc == 0:
            return "pass", _tail(out, 80)
        if rc == 1:
            return "fail", _tail(out)
        return "warn", "audit error (possibly offline) - not a vulnerability finding"

    return _tool("pip-audit", [PY, "-m", "pip_audit"], 120, parse)


def run_lang_audit() -> ToolResult:
    def parse(rc: int, out: str) -> tuple[str, str]:
        if rc == 0:
            return "pass", "all hand-authored source is Python"
        if rc == 1:
            return "fail", _tail(out)
        return "warn", _tail(out)

    return _tool("lang-audit", [PY, "scripts/lang_audit.py"], 30, parse)


def _run_pytest_and_coverage() -> tuple[ToolResult, float | None, tuple[CoverageFile, ...]]:
    """pytest + coverage in one go, then parse the JSON report."""
    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    result = run_pytest()
    pct, files = _parse_coverage_json()
    return result, pct, files


TOOL_ORDER = (
    "ruff format",
    "ruff lint",
    "mypy --strict",
    "pytest --cov",
    "radon cc",
    "bandit -r",
    "pip-audit",
    "lang-audit",
)


def write_report(report: TelemetryReport, path: Path | None = None) -> Path:
    """Persist the report as JSON (default: generated/telemetry/report.json)."""
    target = path or (GENERATED_DIR / "report.json")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    return target


def load_report(path: Path | None = None) -> TelemetryReport | None:
    """Read a previously written report, or None if there is none."""
    target = path or (GENERATED_DIR / "report.json")
    if not target.is_file():
        return None
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    tools = tuple(ToolResult(**tool) for tool in data.get("tools", []))
    files = tuple(CoverageFile(**f) for f in data.get("coverage_files", []))
    raw_complexity = data.get("complexity")
    complexity = Complexity(**raw_complexity) if raw_complexity else None
    return TelemetryReport(
        tools=tools,
        coverage_pct=data.get("coverage_pct"),
        coverage_files=files,
        complexity=complexity,
        python=data.get("python", ""),
        generated_at=data.get("generated_at", ""),
    )


def collect() -> TelemetryReport:
    """Run the whole quality stack in parallel and build the report."""
    runners = [
        run_ruff_format,
        run_ruff_lint,
        run_mypy,
        run_bandit,
        run_pip_audit,
        run_lang_audit,
    ]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda runner: runner(), runners))
    radon_result, complexity = _radon_pair()
    pytest_result, pct, files = _run_pytest_and_coverage()
    by_name = {tool.name: tool for tool in [*results, radon_result, pytest_result]}
    tools = tuple(by_name[name] for name in TOOL_ORDER)
    return TelemetryReport(
        tools=tools,
        coverage_pct=pct,
        coverage_files=files,
        complexity=complexity,
        python=PY,
        generated_at=datetime.now(UTC).isoformat(timespec="seconds"),
    )


def _icon(status: str) -> str:
    if status == "pass":
        return "[ok]"
    if status == "fail":
        return "[!!]"
    if status == "warn":
        return "[~~]"
    return "[--]"


def main() -> int:
    """CLI: run the full stack, print a table, persist JSON. 0 = no failures."""
    print("Running quality stack (this is what the panel shows)...")
    report = collect()
    path = write_report(report)
    for tool in report.tools:
        print(f"  {_icon(tool.status)} {tool.name:<15} {tool.status:<12} {tool.detail[:70]}")
    if report.coverage_pct is not None:
        print(f"  coverage: {report.coverage_pct:.1f}% over {len(report.coverage_files)} files")
    if report.complexity is not None:
        print(f"  complexity: {complexity_detail(report.complexity)}")
    print(f"  report: {path}")
    return 1 if any(tool.status == "fail" for tool in report.tools) else 0


if __name__ == "__main__":
    raise SystemExit(main())
