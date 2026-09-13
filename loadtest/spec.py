"""The load test specification - a plain Python dataclass.

This is the single source of truth for the load test. The k6 script is
*compiled* from it (loadtest/generate.py), never hand-written. Validation
lives here, so a bad spec fails fast in Python before any JavaScript exists.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoadSpec:
    """What to hit, with how many virtual users, and what 'good' means."""

    base_url: str = "http://127.0.0.1:8321"
    endpoint: str = "/api/health"
    vus: int = 4
    ramp_up_s: int = 2
    hold_s: int = 6
    ramp_down_s: int = 2
    p95_ms: int = 250
    error_rate: float = 0.05

    def __post_init__(self) -> None:
        if not self.base_url.startswith(("http://", "https://")):
            raise ValueError(f"base_url must start with http(s)://, got {self.base_url!r}")
        if not self.endpoint.startswith("/"):
            raise ValueError(f"endpoint must start with '/', got {self.endpoint!r}")
        if self.vus < 1:
            raise ValueError(f"vus must be >= 1, got {self.vus}")
        for name in ("ramp_up_s", "hold_s", "ramp_down_s"):
            value = getattr(self, name)
            if value < 0:
                raise ValueError(f"{name} must be >= 0, got {value}")
        if self.ramp_up_s + self.hold_s + self.ramp_down_s == 0:
            raise ValueError("total duration must be > 0 seconds")
        if self.ramp_up_s + self.hold_s <= 0:
            raise ValueError(
                "ramp_up_s + hold_s must be > 0: a load test that never applies "
                "load has no duration of load to measure"
            )
        if self.p95_ms <= 0:
            raise ValueError(f"p95_ms must be > 0, got {self.p95_ms}")
        if not 0 < self.error_rate < 1:
            raise ValueError(f"error_rate must be in (0, 1), got {self.error_rate}")

    @property
    def target_url(self) -> str:
        """The full URL the load test hits."""
        return self.base_url.rstrip("/") + self.endpoint

    @property
    def total_s(self) -> int:
        """Total ramp + hold + ramp-down seconds (k6 duration)."""
        return self.ramp_up_s + self.hold_s + self.ramp_down_s
