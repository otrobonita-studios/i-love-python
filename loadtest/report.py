"""Parse k6-format NDJSON output into a panel-ready LoadReport.

Works with real k6 output as well as the Python simulator's output, because
both emit the same event subset: state, http_req, Metric, Point.
"""

from __future__ import annotations

import contextlib
import json
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Any

MAX_SERIES_POINTS = 80


@dataclass(frozen=True)
class SeriesPoint:
    """One point on the load timeline (for the live chart)."""

    t_s: float
    vus: int
    avg_ms: float


@dataclass(frozen=True)
class LoadReport:
    """Aggregated, panel-ready results of one load run."""

    source: str  # "k6" | "simulator" | "fixture"
    duration_s: float
    total_requests: int
    failed_requests: int
    error_rate: float
    avg_ms: float
    p95_ms: float
    max_ms: float
    series: tuple[SeriesPoint, ...]


def percentile(values: list[float], q: float) -> float:
    """Linear-interpolation percentile. q in [0, 1]. Empty input -> 0.0."""
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    idx = (len(ordered) - 1) * q
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return ordered[lo]
    frac = idx - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def _event_time(event: dict[str, Any]) -> float | None:
    raw = event.get("time")
    if not isinstance(raw, str):
        return None
    try:
        # k6 emits ISO-8601 with Z; normalize for fromisoformat.
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _iter_events(text: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            events.append(parsed)
    return events


def _build_series(
    states: list[tuple[float, int]],
    points: list[tuple[float, float]],
) -> tuple[SeriesPoint, ...]:
    """Merge state (vus) and Point (avg duration) events onto one timeline."""
    if not states and not points:
        return ()
    timestamps = sorted({t for t, _ in states} | {t for t, _ in points})
    if not timestamps:
        return ()
    origin = timestamps[0]
    vus_at: dict[float, int] = {}
    cur = 0
    for t, v in sorted(states):
        cur = v
        vus_at[t] = cur
    avg_at = dict(sorted(points))
    merged: list[SeriesPoint] = []
    cur_vus = 0
    cur_avg = 0.0
    for t in timestamps:
        if t in vus_at:
            cur_vus = vus_at[t]
        if t in avg_at:
            cur_avg = avg_at[t]
        merged.append(SeriesPoint(t_s=round(t - origin, 3), vus=cur_vus, avg_ms=round(cur_avg, 3)))
    if len(merged) > MAX_SERIES_POINTS:
        step = math.ceil(len(merged) / MAX_SERIES_POINTS)
        merged = merged[::step][:MAX_SERIES_POINTS]
    return tuple(merged)


def parse_ndjson(text: str, source: str = "k6") -> LoadReport:
    """Turn k6-format NDJSON into a LoadReport. Never raises on bad lines."""
    durations: list[float] = []
    failed = 0
    total = 0
    states: list[tuple[float, int]] = []
    points: list[tuple[float, float]] = []
    first_time: float | None = None
    last_time: float | None = None

    for event in _iter_events(text):
        t = _event_time(event)
        if t is not None:
            first_time = t if first_time is None else min(first_time, t)
            last_time = t if last_time is None else max(last_time, t)
        etype = event.get("type")
        data = event.get("data", {})
        if etype == "state":
            vus = data.get("vus", 0)
            if t is not None:
                states.append((t, int(vus)))
        elif etype == "http_req":
            total += 1
            status = str(data.get("status", ""))
            error = data.get("error", "")
            if status != "200" or error:
                failed += 1
        elif etype == "Metric":
            if data.get("metric") == "http_req_duration":
                with contextlib.suppress(TypeError, ValueError):
                    durations.append(float(data.get("value")))
        elif etype == "Point":
            if data.get("metric") == "http_req_duration" and t is not None:
                values = data.get("values", {})
                with contextlib.suppress(TypeError, ValueError):
                    points.append((t, float(values.get("avg", 0.0))))

    duration_s = (
        (last_time - first_time) if (first_time is not None and last_time is not None) else 0.0
    )
    total = total or len(durations)
    if total and not durations:
        durations = [0.0] * total
    error_rate = failed / total if total else 0.0
    avg_ms = sum(durations) / len(durations) if durations else 0.0
    return LoadReport(
        source=source,
        duration_s=round(duration_s, 3),
        total_requests=total,
        failed_requests=failed,
        error_rate=round(error_rate, 5),
        avg_ms=round(avg_ms, 3),
        p95_ms=round(percentile(durations, 0.95), 3),
        max_ms=round(max(durations), 3) if durations else 0.0,
        series=_build_series(states, points),
    )
