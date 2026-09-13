"""Unit tests for panel/telemetry.py: honest statuses and real parsing logic.

The subprocess layer (_run) is monkeypatched with canned outputs, so every
parse branch is exercised deterministically while the honesty rules are
asserted: failures stay failures, timeouts are warnings, missing tools are
"unavailable" - never fake passes.
"""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

import panel.telemetry as tel


def _fake_run(
    table: dict[str, tuple[int, str]],
) -> Callable[[list[str], int], tuple[int, str, float]]:
    def fake_run(cmd: list[str], timeout: int) -> tuple[int, str, float]:
        joined = " ".join(cmd)
        for key, value in table.items():
            if key in joined:
                return value[0], value[1], 0.01
        raise AssertionError(f"unexpected command in telemetry test: {joined}")

    return fake_run


CLEAN_TABLE: dict[str, tuple[int, str]] = {
    "ruff format": (0, "47 files already formatted\n"),
    "ruff check": (0, "All checks passed!\n"),
    "mypy": (0, "Success: no issues found in 28 source files\n"),
    "pytest": (0, "69 passed in 3.21s\n"),
    "radon": (0, "    F 53:0 to_svg - A\n    F 10:0 heart_point - A\n    C 1:0 LoadSpec - B\n"),
    "bandit": (0, "no issues identified\n"),
    "pip_audit": (0, "No known vulnerabilities found\n"),
    "scripts/lang_audit.py": (0, "ok\n"),
}


@pytest.fixture
def clean_tools(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(tel, "_run", _fake_run(CLEAN_TABLE))
    monkeypatch.setattr(tel, "GENERATED_DIR", tmp_path / "telemetry")


def _patch_failing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    key: str,
    value: tuple[int, str],
) -> None:
    table = dict(CLEAN_TABLE)
    table[key] = value
    monkeypatch.setattr(tel, "_run", _fake_run(table))
    monkeypatch.setattr(tel, "GENERATED_DIR", tmp_path / "telemetry")


def test_collect_reports_all_tools_in_order(clean_tools: None) -> None:
    report = tel.collect()
    assert [t.name for t in report.tools] == list(tel.TOOL_ORDER)
    assert all(t.status == "pass" for t in report.tools)
    assert report.python


def test_collect_parses_complexity(clean_tools: None) -> None:
    report = tel.collect()
    assert report.complexity == tel.Complexity(a=2, b=1, c=0, d=0, e=0)
    assert tel.complexity_detail(report.complexity) == "A:2 B:1 C:0 D:0 E:0"


def test_coverage_json_parsed_into_files(clean_tools: None, tmp_path: Path) -> None:
    gen = tmp_path / "telemetry"
    gen.mkdir(parents=True, exist_ok=True)
    payload = {
        "files": {
            "art\\heart.py": {"summary": {"covered_lines": 40, "num_statements": 40}},
            "art\\__init__.py": {"summary": {"covered_lines": 0, "num_statements": 0}},
            "panel\\telemetry.py": {"summary": {"covered_lines": 50, "num_statements": 100}},
        },
        "totals": {"covered_lines": 90, "num_statements": 140},
    }
    (gen / "coverage.json").write_text(json.dumps(payload), encoding="utf-8")
    pct, files = tel._parse_coverage_json()
    assert pct == pytest.approx(100 * 90 / 140)
    assert [f.path for f in files] == ["art/heart.py", "panel/telemetry.py"]
    assert files[1].pct == pytest.approx(50.0)


def test_parse_coverage_json_without_file(clean_tools: None) -> None:
    pct, files = tel._parse_coverage_json()
    assert pct is None
    assert files == ()


def test_failed_tool_stays_failed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_failing(
        monkeypatch,
        tmp_path,
        "ruff check",
        (1, "F401 `os` imported but unused\nFound 1 error.\n"),
    )
    report = tel.collect()
    by_name = {t.name: t for t in report.tools}
    assert by_name["ruff lint"].status == "fail"
    assert "F401" in by_name["ruff lint"].detail
    assert by_name["mypy --strict"].status == "pass"


def test_missing_executable_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(cmd: list[str], timeout: int) -> tuple[int, str, float]:
        raise FileNotFoundError("nope")

    monkeypatch.setattr(tel, "_run", boom)
    result = tel.run_ruff_format()
    assert result.status == "unavailable"
    assert "not found" in result.detail


def test_timeout_is_warn_not_crash(monkeypatch: pytest.MonkeyPatch) -> None:
    def slow(cmd: list[str], timeout: int) -> tuple[int, str, float]:
        raise subprocess.TimeoutExpired(cmd, timeout)

    monkeypatch.setattr(tel, "_run", slow)
    result = tel.run_bandit()
    assert result.status == "warn"
    assert "timed out" in result.detail


def test_pip_audit_offline_is_warn(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_failing(monkeypatch, tmp_path, "pip_audit", (2, "error: unable to perform audit\n"))
    result = tel.run_pip_audit()
    assert result.status == "warn"
    assert "offline" in result.detail


def test_pip_audit_vulnerabilities_fail(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _patch_failing(
        monkeypatch,
        tmp_path,
        "pip_audit",
        (1, "Name: requests  Vulnerabilities: 1  ID: PYSEC-2024-001\n"),
    )
    result = tel.run_pip_audit()
    assert result.status == "fail"
    assert "PYSEC-2024-001" in result.detail


def test_radon_warns_on_complex_functions(monkeypatch: pytest.MonkeyPatch) -> None:
    table = dict(CLEAN_TABLE)
    table["radon"] = (0, "    F 10:0 parse_ndjson - D\n    F 20:0 loop - E\n")
    monkeypatch.setattr(tel, "_run", _fake_run(table))
    result = tel.run_radon()
    assert result.status == "warn"
    assert "D:1" in result.detail
    assert "E:1" in result.detail


def test_report_roundtrip(clean_tools: None, tmp_path: Path) -> None:
    report = tel.collect()
    path = tel.write_report(report, tmp_path / "report.json")
    loaded = tel.load_report(path)
    assert loaded is not None
    assert [t.name for t in loaded.tools] == [t.name for t in report.tools]
    assert loaded.coverage_pct == report.coverage_pct
    assert loaded.complexity == report.complexity


def test_load_report_missing_returns_none(tmp_path: Path) -> None:
    assert tel.load_report(tmp_path / "nope.json") is None


def test_load_report_corrupt_returns_none(tmp_path: Path) -> None:
    bad = tmp_path / "report.json"
    bad.write_text("{not json", encoding="utf-8")
    assert tel.load_report(bad) is None


def test_main_returns_zero_when_clean(
    clean_tools: None, capsys: pytest.CaptureFixture[str]
) -> None:
    assert tel.main() == 0
    out = capsys.readouterr().out
    assert "ruff format" in out
    assert "pass" in out


def test_main_returns_one_when_failing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _patch_failing(monkeypatch, tmp_path, "bandit", (1, ">> Issue: [B101:assert_used]\n"))
    assert tel.main() == 1
    out = capsys.readouterr().out
    assert "fail" in out
