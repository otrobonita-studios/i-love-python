"""Unit tests for loadtest/simulator.py (Python VU engine and offline fixture).

http_simulate is exercised against a real local HTTP server (so the VU
threads, NDJSON emission, and failure accounting are all genuine), and the
offline fixture is checked for determinism and parseability.
"""

from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import loadtest.simulator as simulator
from loadtest.report import parse_ndjson
from loadtest.spec import LoadSpec


class _OkHandler(BaseHTTPRequestHandler):
    """Tiny 200-OK server for the live simulation test."""

    def do_GET(self) -> None:  # fixed method name required by http.server
        body = b'{"ok": true}'
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:  # silence per-request logging
        return None


def _serve() -> tuple[ThreadingHTTPServer, int]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _OkHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, port


def test_offline_fixture_is_deterministic_per_seed() -> None:
    text_a, spec_a = simulator.offline_fixture(seed=7)
    text_b, spec_b = simulator.offline_fixture(seed=7)
    assert text_a == text_b
    assert spec_a == spec_b


def test_offline_fixture_seed_changes_output() -> None:
    text_a, _ = simulator.offline_fixture(seed=1)
    text_b, _ = simulator.offline_fixture(seed=2)
    assert text_a != text_b


def test_offline_fixture_parses_to_a_report() -> None:
    text, _ = simulator.offline_fixture(seed=7)
    report = parse_ndjson(text, "fixture")
    assert report.total_requests > 0
    assert report.avg_ms > 0
    assert report.p95_ms >= report.avg_ms
    assert report.series
    # The fixture is labelled as such, never as a real k6 run.
    assert report.source == "fixture"


def test_phases_cover_the_whole_duration() -> None:
    spec = LoadSpec(ramp_up_s=2, hold_s=3, ramp_down_s=1)
    phases = simulator._phases(spec)
    assert sum(duration for _, duration in phases) == spec.total_s
    assert all(vus > 0 for vus, _ in phases)
    assert all(vus <= spec.vus for vus, _ in phases)


def test_phases_drop_ramp_down_to_zero() -> None:
    spec = LoadSpec(ramp_up_s=1, hold_s=1, ramp_down_s=2)
    phases = simulator._phases(spec)
    assert phases[-1][0] < spec.vus  # final phase has fewer VUs
    assert all(duration > 0 for _, duration in phases)


def test_http_simulate_against_live_server() -> None:
    server, port = _serve()
    try:
        spec = LoadSpec(
            base_url=f"http://127.0.0.1:{port}", vus=2, ramp_up_s=1, hold_s=1, ramp_down_s=0
        )
        text = simulator.http_simulate(spec)
        report = parse_ndjson(text, "simulator")
        assert report.total_requests > 0
        assert report.failed_requests == 0
        assert report.avg_ms > 0
        assert report.series
    finally:
        server.shutdown()
        server.server_close()


def test_http_simulate_reports_failures_on_dead_target() -> None:
    spec = LoadSpec(base_url="http://127.0.0.1:1", vus=1, ramp_up_s=1, hold_s=1, ramp_down_s=0)
    text = simulator.http_simulate(spec)
    report = parse_ndjson(text, "simulator")
    assert report.total_requests > 0
    assert report.failed_requests == report.total_requests
    assert report.error_rate == 1.0


def test_get_returns_status_and_error_shape() -> None:
    status, error = simulator._get("http://127.0.0.1:1")
    assert status == 0
    assert error  # the exception type name, e.g. ConnectionRefusedError
