"""Unit tests for the NDJSON report parser."""

import json

from loadtest.report import LoadReport, parse_ndjson, percentile


def _line(payload: dict[str, object]) -> str:
    return json.dumps(payload)


def _sample_ndjson() -> str:
    lines = [
        _line(
            {"type": "state", "data": {"vus": 1, "maxVUs": 2}, "time": "2026-01-01T00:00:00.000Z"}
        ),
        _line(
            {
                "type": "Metric",
                "data": {"metric": "http_req_duration", "value": 10.0},
                "time": "2026-01-01T00:00:00.100Z",
            }
        ),
        _line(
            {
                "type": "http_req",
                "data": {"method": "GET", "url": "u", "status": 200, "error": ""},
                "time": "2026-01-01T00:00:00.100Z",
            }
        ),
        _line(
            {
                "type": "Metric",
                "data": {"metric": "http_req_duration", "value": 20.0},
                "time": "2026-01-01T00:00:00.200Z",
            }
        ),
        _line(
            {
                "type": "http_req",
                "data": {"method": "GET", "url": "u", "status": 500, "error": "http error"},
                "time": "2026-01-01T00:00:00.200Z",
            }
        ),
        _line(
            {
                "type": "Point",
                "data": {"metric": "http_req_duration", "values": {"avg": 15.0, "count": 2}},
                "time": "2026-01-01T00:00:00.300Z",
            }
        ),
        "this is not json",
    ]
    return "\n".join(lines)


def test_percentile_known_values() -> None:
    assert percentile([1, 2, 3, 4], 0.5) == 2.5
    assert percentile([7], 0.95) == 7
    assert percentile([], 0.95) == 0.0
    assert percentile([10, 20, 30, 40, 50], 0.95) > 40


def test_parse_sample_report() -> None:
    report = parse_ndjson(_sample_ndjson(), source="test")
    assert isinstance(report, LoadReport)
    assert report.total_requests == 2
    assert report.failed_requests == 1
    assert report.error_rate == 0.5
    assert report.p95_ms == 19.5  # linear interpolation between 10 and 20
    assert report.max_ms == 20.0
    assert len(report.series) >= 2
    assert report.series[0].vus == 1


def test_parse_garbage_is_safe() -> None:
    report = parse_ndjson("hello\nworld\n{broken", source="test")
    assert report.total_requests == 0
    assert report.p95_ms == 0.0
    assert report.series == ()


def test_series_is_downsampled() -> None:
    from loadtest.simulator import offline_fixture

    ndjson, _ = offline_fixture(seed=1, requests_per_vu_s=50.0)
    report = parse_ndjson(ndjson, source="fixture")
    assert len(report.series) <= 80


def test_all_failures_gives_full_error_rate() -> None:
    lines = [
        _line(
            {
                "type": "http_req",
                "data": {"status": 503, "error": "x"},
                "time": "2026-01-01T00:00:00Z",
            }
        ),
        _line(
            {
                "type": "http_req",
                "data": {"status": 503, "error": "x"},
                "time": "2026-01-01T00:00:01Z",
            }
        ),
    ]
    report = parse_ndjson("\n".join(lines), source="test")
    assert report.error_rate == 1.0
    assert report.total_requests == 2
