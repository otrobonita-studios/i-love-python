"""Unit tests for the k6 JavaScript compiler."""

import shutil
import subprocess
from pathlib import Path

import pytest

from loadtest.generate import GENERATED_HEADER, compile_js, validate_structure, write_js
from loadtest.spec import LoadSpec

NODE = shutil.which("node")


def test_compiled_js_has_required_shape() -> None:
    spec = LoadSpec()
    js = compile_js(spec)
    assert js.startswith(GENERATED_HEADER)
    assert "import http from 'k6/http';" in js
    assert "export default function" in js
    assert spec.target_url in js
    assert f"p(95)<{spec.p95_ms}" in js
    assert f"rate<{spec.error_rate}" in js
    assert f"target: {spec.vus}" in js


def test_validation_finds_no_problems_for_valid_spec() -> None:
    spec = LoadSpec()
    assert validate_structure(compile_js(spec), spec) == []


def test_validation_catches_malformed_scripts() -> None:
    spec = LoadSpec()
    problems = validate_structure("nope", spec)
    assert any("header" in p for p in problems)
    assert any("import" in p for p in problems)


def test_write_js_creates_file_with_header(tmp_path: Path) -> None:
    out = tmp_path / "k6" / "load_test.js"
    written = write_js(LoadSpec(), out)
    assert written == out
    text = out.read_text(encoding="utf-8")
    assert text.startswith(GENERATED_HEADER)


def _broken_compile(_spec: LoadSpec) -> str:
    return "broken"


def test_write_js_refuses_invalid_compilation(monkeypatch: pytest.MonkeyPatch) -> None:
    # Force a compiler that emits garbage; write_js must refuse to write it.
    import loadtest.generate as generate

    monkeypatch.setattr(generate, "compile_js", _broken_compile)
    with pytest.raises(ValueError, match="validation"):
        write_js(LoadSpec(), Path("should_not_exist.js"))


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_node_accepts_generated_script(tmp_path: Path) -> None:
    assert NODE is not None
    out = write_js(LoadSpec(), tmp_path / "load_test.js")
    mjs = tmp_path / "check.mjs"
    mjs.write_text(out.read_text(encoding="utf-8"), encoding="utf-8")
    proc = subprocess.run(
        [NODE, "--check", str(mjs)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
