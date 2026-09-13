"""Unit tests for the load spec dataclass."""

import pytest

from loadtest.spec import LoadSpec


def test_defaults_are_valid() -> None:
    spec = LoadSpec()
    assert spec.vus >= 1
    assert spec.target_url == "http://127.0.0.1:8321/api/health"
    assert spec.total_s == spec.ramp_up_s + spec.hold_s + spec.ramp_down_s


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"vus": 0}, "vus"),
        ({"vus": -3}, "vus"),
        ({"error_rate": 0.0}, "error_rate"),
        ({"error_rate": 1.5}, "error_rate"),
        ({"base_url": "ftp://nope"}, "base_url"),
        ({"endpoint": "no-slash"}, "endpoint"),
        ({"p95_ms": 0}, "p95_ms"),
        ({"ramp_up_s": 0, "hold_s": 0, "ramp_down_s": 0}, "duration"),
        # A ramp-down-only test never applies load, so it is not a load test.
        ({"ramp_up_s": 0, "hold_s": 0, "ramp_down_s": 3}, "duration of load"),
    ],
)
def test_invalid_specs_rejected(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        LoadSpec(**kwargs)  # type: ignore[arg-type]  # intentional invalid overrides


def test_target_url_strips_trailing_slash() -> None:
    spec = LoadSpec(base_url="http://x.example/")
    assert spec.target_url == "http://x.example/api/health"
