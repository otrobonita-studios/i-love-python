"""Property-based tests for the heart geometry."""

import math
import xml.etree.ElementTree as ET

from hypothesis import given, settings
from hypothesis.strategies import floats, integers

from art.heart import heart_point, heart_points, to_svg

T = floats(min_value=0.0, max_value=2 * math.pi, allow_nan=False, allow_infinity=False)


@settings(max_examples=200)
@given(t=T)
def test_points_are_always_finite(t: float) -> None:
    point = heart_point(t)
    assert math.isfinite(point.x)
    assert math.isfinite(point.y)


@settings(max_examples=200)
@given(t=floats(min_value=-math.pi, max_value=math.pi, allow_nan=False, allow_infinity=False))
def test_mirror_symmetry_about_y_axis(t: float) -> None:
    # x is odd in t, y is even in t: symmetry about the vertical axis.
    a = heart_point(t)
    b = heart_point(-t)
    assert abs(b.x + a.x) < 1e-6
    assert abs(b.y - a.y) < 1e-6


@settings(max_examples=50)
@given(n=integers(min_value=3, max_value=500))
def test_sampling_count(n: int) -> None:
    points = heart_points(n)
    assert len(points) == n
    # The curve is periodic: t=0 and t=2*pi land on the same point.
    a = heart_point(0.0)
    b = heart_point(2.0 * math.pi)
    assert abs(a.x - b.x) < 1e-9
    assert abs(a.y - b.y) < 1e-9


@settings(max_examples=25)
@given(n=integers(min_value=3, max_value=120))
def test_svg_is_well_formed_xml(n: int) -> None:
    svg = to_svg(heart_points(n))
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    assert root.get("width") and root.get("height")
