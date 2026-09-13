"""Integration: the full load-test loop, end to end.

spec -> compile k6 JS -> validate -> (node --check if available) ->
parse a real NDJSON stream -> panel-ready report -> persona review of a
real commit in this repo.
"""

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from loadtest.generate import compile_js, validate_structure, write_js
from loadtest.report import parse_ndjson
from loadtest.simulator import offline_fixture
from loadtest.spec import LoadSpec
from review.personas import review_diff
from review.store import commit_count, pick_commit

NODE = shutil.which("node")


def test_full_loop_with_fixture() -> None:
    # 1. Spec -> JS
    spec = LoadSpec()
    js = compile_js(spec)
    assert validate_structure(js, spec) == []

    # 2. Write it (generated artifact, GENERATED header)
    with tempfile.TemporaryDirectory() as tmp:
        out = write_js(spec, Path(tmp) / "load_test.js")
        assert out.read_text(encoding="utf-8").startswith("// GENERATED")

    # 3. Parse a real-shaped NDJSON stream into a panel-ready report
    ndjson, fixture_spec = offline_fixture(seed=11)
    report = parse_ndjson(ndjson, source="fixture")
    assert report.total_requests > 0
    assert report.p95_ms > 0
    assert report.avg_ms > 0
    assert len(report.series) >= 2
    assert all(point.vus >= 0 for point in report.series)
    assert fixture_spec.target_url == spec.target_url

    # 4. Thresholds: the fixture should sit comfortably under the defaults
    assert report.p95_ms < spec.p95_ms
    assert report.error_rate < spec.error_rate


@pytest.mark.skipif(NODE is None, reason="node not available")
def test_node_syntax_checks_generated_js() -> None:
    assert NODE is not None
    with tempfile.TemporaryDirectory() as tmp:
        out = write_js(LoadSpec(), Path(tmp) / "load_test.js")
        mjs = Path(tmp) / "check.mjs"
        mjs.write_text(out.read_text(encoding="utf-8"), encoding="utf-8")
        proc = subprocess.run(
            [NODE, "--check", str(mjs)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode == 0, proc.stderr


def test_personas_review_a_real_commit() -> None:
    count = commit_count()
    assert count >= 2
    # Find the newest commit that actually has a file diff (merge commits do not).
    commit = None
    diff = ""
    for i in range(min(6, count)):
        candidate, candidate_diff = pick_commit(i)
        if "diff --git" in candidate_diff:
            commit, diff = candidate, candidate_diff
            break
    assert commit is not None
    review = review_diff(diff, commit.sha)
    assert len(review.verdicts) == 3
    assert review.consensus_tone in ("ok", "caution", "block")


def test_report_serializes_to_panel_data() -> None:
    """The exact shape the UI consumes must be stable."""
    ndjson, _ = offline_fixture(seed=3)
    report = parse_ndjson(ndjson, source="fixture")
    series = [(p.t_s, p.vus, p.avg_ms) for p in report.series]
    assert report.source == "fixture"
    assert report.total_requests > 0
    assert len(series) >= 2
