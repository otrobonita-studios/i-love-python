"""Unit tests for the parametric heart."""

import math
import xml.etree.ElementTree as ET

from art.heart import heart_point, heart_points, svg_path, to_svg


def test_heart_point_at_zero_is_five() -> None:
    point = heart_point(0.0)
    assert point.x == 0.0
    assert point.y == 5.0


def test_symmetry_across_vertical_axis() -> None:
    # The heart is symmetric about the y-axis: x(-t) = -x(t), y(-t) = y(t).
    for t in (0.3, 1.1, 2.4, 4.9):
        a = heart_point(t)
        b = heart_point(-t)
        assert abs(b.x + a.x) < 1e-9
        assert abs(b.y - a.y) < 1e-9


def test_curve_is_periodic() -> None:
    a = heart_point(0.0)
    b = heart_point(2.0 * math.pi)
    assert abs(a.x - b.x) < 1e-9
    assert abs(a.y - b.y) < 1e-9


def test_points_are_finite_and_counted() -> None:
    points = heart_points(100)
    assert len(points) == 100
    assert all(math.isfinite(p.x) and math.isfinite(p.y) for p in points)


def test_too_few_points_rejected() -> None:
    for n in (0, 1, 2):
        try:
            heart_points(n)
        except ValueError:
            pass
        else:
            raise AssertionError(f"heart_points({n}) should raise ValueError")


def test_svg_is_valid_xml_with_path() -> None:
    svg = to_svg(heart_points(64))
    root = ET.fromstring(svg)
    assert root.tag.endswith("svg")
    path = root.find("{http://www.w3.org/2000/svg}path")
    assert path is not None
    assert path.get("d", "").startswith("M ")


def test_svg_path_empty_for_empty_points() -> None:
    assert svg_path([]) == ""


def test_to_svg_empty_points_gives_placeholder() -> None:
    svg = to_svg([])
    ET.fromstring(svg)
    assert "width" in svg
