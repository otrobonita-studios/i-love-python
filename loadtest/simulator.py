"""Load the app from Python itself, in k6's shape.

Two flavors, both honest about their source:

- http_simulate(): real virtual users (threads) hammering the real endpoint
  with real HTTP requests, emitting k6-format NDJSON. Each VU keeps one
  connection alive across its iterations (k6's per-VU keep-alive), so the
  load is faithful and the client does not exhaust ephemeral ports.
  Used when k6 is not installed - a genuine load test, just driven by Python.
- offline_fixture(): a deterministic, network-free NDJSON stream, used for
  tests and for the "offline" demo mode. Labelled as a fixture, always.
"""

from __future__ import annotations

import http.client
import json
import math
import random
import threading
import time
from datetime import UTC, datetime
from urllib.parse import urlsplit

from loadtest.spec import LoadSpec

USER_AGENT = "i-love-python-loadtest"
REQUEST_TIMEOUT_S = 5.0


def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, UTC).isoformat()


def _split_url(url: str) -> tuple[str, int, str, str]:
    """(host, port, path, scheme) of the target URL."""
    parts = urlsplit(url)
    host = parts.hostname or "127.0.0.1"
    port = parts.port or (443 if parts.scheme == "https" else 80)
    return host, port, parts.path or "/", parts.scheme


def _connect(host: str, port: int, scheme: str) -> http.client.HTTPConnection:
    if scheme == "https":
        return http.client.HTTPSConnection(host, port, timeout=REQUEST_TIMEOUT_S)
    return http.client.HTTPConnection(host, port, timeout=REQUEST_TIMEOUT_S)


def _one_request(conn: http.client.HTTPConnection, path: str) -> tuple[int, str]:
    """One GET over an existing connection. (status, error); 0 = no response."""
    conn.request("GET", path, headers={"User-Agent": USER_AGENT})
    resp = conn.getresponse()
    resp.read()  # drain fully so the connection stays reusable (keep-alive)
    return resp.status, ""


def _get(url: str) -> tuple[int, str]:
    """One real HTTP GET on a fresh connection. (status, error); 0 = no response."""
    host, port, path, scheme = _split_url(url)
    conn = _connect(host, port, scheme)
    try:
        return _one_request(conn, path)
    except Exception as exc:  # any network failure is a valid sample
        return 0, type(exc).__name__
    finally:
        conn.close()


def _phases(spec: LoadSpec) -> list[tuple[int, float]]:
    """(vus, seconds) phases: linear ramp up, hold, linear ramp down."""
    phases: list[tuple[int, float]] = []
    if spec.ramp_up_s > 0:
        steps = max(1, spec.ramp_up_s)
        per = spec.ramp_up_s / steps
        for i in range(steps):
            vus = max(1, round(spec.vus * (i + 1) / steps))
            phases.append((vus, per))
    if spec.hold_s > 0:
        phases.append((spec.vus, spec.hold_s))
    if spec.ramp_down_s > 0:
        steps = max(1, spec.ramp_down_s)
        per = spec.ramp_down_s / steps
        for i in range(steps):
            vus = max(0, round(spec.vus * (steps - i) / steps))
            phases.append((vus, per))
    return [(v, d) for v, d in phases if v > 0 and d > 0]


def http_simulate(spec: LoadSpec) -> str:
    """Run the load test from Python and return k6-format NDJSON."""
    lines: list[str] = []
    lock = threading.Lock()
    req_log: list[tuple[float, float]] = []  # (epoch, ms) - for per-second averages

    def emit(payload: dict[str, object]) -> None:
        with lock:
            lines.append(json.dumps(payload))

    def worker(stop: threading.Event) -> None:
        # One persistent connection per VU: k6 keeps its connections alive per
        # virtual user, and a no-keep-alive client both distorts the load and
        # exhausts the client's ephemeral ports under a hot loop (observed:
        # 65-99% client-side URLErrors against a healthy server).
        host, port, path, scheme = _split_url(spec.target_url)
        conn = _connect(host, port, scheme)
        while not stop.is_set():
            start = time.perf_counter()
            try:
                status, err = _one_request(conn, path)
            except Exception as exc:
                status, err = 0, type(exc).__name__
                conn = _connect(host, port, scheme)  # reconnect, as k6 would
            ms = (time.perf_counter() - start) * 1000.0
            now = time.time()
            with lock:
                req_log.append((now, ms))
            emit(
                {
                    "type": "Metric",
                    "data": {"metric": "http_req_duration", "value": round(ms, 3)},
                    "time": _iso(now),
                }
            )
            emit(
                {
                    "type": "http_req",
                    "data": {
                        "method": "GET",
                        "url": spec.target_url,
                        "status": status,
                        "error": err,
                    },
                    "time": _iso(now),
                }
            )

    for vus, duration_s in _phases(spec):
        now = time.time()
        emit({"type": "state", "data": {"vus": vus, "maxVUs": spec.vus}, "time": _iso(now)})
        stop = threading.Event()
        threads = [threading.Thread(target=worker, args=(stop,), daemon=True) for _ in range(vus)]
        for thread in threads:
            thread.start()
        deadline = time.monotonic() + duration_s
        cutoff = now
        while time.monotonic() < deadline:
            time.sleep(0.5)
            mark = time.time()
            with lock:
                fresh = [ms for ts, ms in req_log if ts > cutoff]
            avg = sum(fresh) / len(fresh) if fresh else 0.0
            emit(
                {
                    "type": "Point",
                    "data": {
                        "metric": "http_req_duration",
                        "values": {"avg": round(avg, 3), "count": len(fresh)},
                    },
                    "time": _iso(mark),
                }
            )
            cutoff = mark
        stop.set()
        for thread in threads:
            thread.join(timeout=REQUEST_TIMEOUT_S + 2)
    return "\n".join(lines)


def offline_fixture(seed: int = 7, requests_per_vu_s: float = 2.0) -> tuple[str, LoadSpec]:
    """Deterministic NDJSON that looks like a real run. No network at all.

    Returns the NDJSON text and the spec it was generated from, so the UI can
    show which settings the fixture used.
    """
    rng = random.Random(seed)  # nosec B311 - simulated latency, not cryptographic
    spec = LoadSpec()
    base = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC).timestamp()
    lines: list[str] = []
    clock = base
    for vus, duration_s in _phases(spec):
        seconds = max(1, math.ceil(duration_s))
        for s in range(seconds):
            t = clock + s * (duration_s / seconds)
            lines.append(
                json.dumps(
                    {"type": "state", "data": {"vus": vus, "maxVUs": spec.vus}, "time": _iso(t)}
                )
            )
            n_requests = max(1, int(vus * requests_per_vu_s * (duration_s / seconds)))
            durations: list[float] = []
            for _ in range(n_requests):
                slow = rng.random() < 0.03
                ms = rng.uniform(90.0, 280.0) if slow else rng.uniform(12.0, 45.0)
                failed = rng.random() < 0.015
                status = 500 if failed else 200
                durations.append(ms)
                lines.append(
                    json.dumps(
                        {
                            "type": "Metric",
                            "data": {"metric": "http_req_duration", "value": round(ms, 3)},
                            "time": _iso(t),
                        }
                    )
                )
                lines.append(
                    json.dumps(
                        {
                            "type": "http_req",
                            "data": {
                                "method": "GET",
                                "url": spec.target_url,
                                "status": status,
                                "error": "http error" if failed else "",
                            },
                            "time": _iso(t),
                        }
                    )
                )
            avg = sum(durations) / len(durations)
            lines.append(
                json.dumps(
                    {
                        "type": "Point",
                        "data": {
                            "metric": "http_req_duration",
                            "values": {"avg": round(avg, 3), "count": len(durations)},
                        },
                        "time": _iso(t),
                    }
                )
            )
        clock += duration_s
    return "\n".join(lines), spec
