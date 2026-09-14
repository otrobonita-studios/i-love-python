"""A parametric heart, drawn with pure Python math.

The classic curve, sampled and turned into SVG:

    x(t) = 16 * sin(t)^3
    y(t) = 13*cos(t) - 5*cos(2t) - 2*cos(3t) - cos(4t)

Everything downstream (landing page, layout, tests) derives from heart_point().
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class HeartPoint:
    """One point on the heart curve, in math coordinates (y up)."""

    x: float
    y: float


def heart_point(t: float) -> HeartPoint:
    """Evaluate the parametric heart at parameter t (radians)."""
    x = 16.0 * math.sin(t) ** 3
    y = 13.0 * math.cos(t) - 5.0 * math.cos(2.0 * t) - 2.0 * math.cos(3.0 * t) - math.cos(4.0 * t)
    return HeartPoint(x=x, y=y)


def heart_points(n: int = 240) -> list[HeartPoint]:
    """Sample the heart curve at n points over one full period [0, 2*pi)."""
    if n < 3:
        raise ValueError("need at least 3 points to draw a heart")
    return [heart_point(2.0 * math.pi * i / n) for i in range(n)]


@dataclass(frozen=True)
class HeartProjection:
    """SVG mapping: X = origin_x + x * scale, Y = origin_y - y * scale."""

    origin_x: float
    origin_y: float
    width: float
    height: float
    scale: float
    padding: float

    def xy(self, point: HeartPoint) -> tuple[float, float]:
        """Project one math-space point into the viewBox."""
        return (self.origin_x + point.x * self.scale, self.origin_y - point.y * self.scale)


def project(
    points: list[HeartPoint],
    *,
    scale: float = 12.0,
    padding: float = 8.0,
) -> HeartProjection:
    """Choose origin and viewBox so every sampled point sits inside the box."""
    if not points:
        raise ValueError("need points to project")
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = (max_x - min_x) * scale + 2.0 * padding
    height = (max_y - min_y) * scale + 2.0 * padding
    origin_x = padding - min_x * scale
    origin_y = padding + max_y * scale
    return HeartProjection(origin_x, origin_y, width, height, scale, padding)


def svg_path(
    points: list[HeartPoint],
    scale: float = 12.0,
    origin_y: float = 0.0,
    origin_x: float = 0.0,
) -> str:
    """Turn heart points into an SVG path d-attribute (SVG y grows downward)."""
    if not points:
        return ""

    def xy(point: HeartPoint) -> str:
        return f"{origin_x + point.x * scale:.2f} {origin_y - point.y * scale:.2f}"

    parts = [f"M {xy(points[0])}"]
    parts += [f"L {xy(point)}" for point in points[1:]]
    parts.append("Z")
    return " ".join(parts)


HEART_RED = "#EE1C25"


def overlay_svg(points: list[HeartPoint], *, scale: float = 12.0) -> str:
    """Parametric heart for the landing lockup. ViewBox contains the curve."""
    if not points:
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"></svg>'
    proj = project(points, scale=scale)
    path = svg_path(points, scale=proj.scale, origin_x=proj.origin_x, origin_y=proj.origin_y)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" class="ilp-heart" '
        f'viewBox="0 0 {proj.width:.2f} {proj.height:.2f}" role="img" '
        f'aria-label="parametric heart">'
        f'<path class="ilp-heart-path" d="{path}" fill="{HEART_RED}" '
        f'stroke="{HEART_RED}" stroke-width="1.2" pathLength="1" '
        f'stroke-dasharray="1" stroke-dashoffset="1"/>'
        f"</svg>"
    )


def lab_svg(points: list[HeartPoint], t: float, *, scale: float = 12.0) -> str:
    """Curve plus the point at t — for the heart experiment."""
    if not points:
        return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"></svg>'
    proj = project(points, scale=scale)
    path = svg_path(points, scale=proj.scale, origin_x=proj.origin_x, origin_y=proj.origin_y)
    px, py = proj.xy(heart_point(t))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {proj.width:.2f} {proj.height:.2f}" '
        f'class="ilp-lab-svg" role="img" aria-label="parametric heart experiment">'
        f'<path d="{path}" fill="none" stroke="{HEART_RED}" stroke-width="2"/>'
        f'<circle cx="{px:.2f}" cy="{py:.2f}" r="5" fill="{HEART_RED}"/>'
        f"</svg>"
    )


def to_svg(
    points: list[HeartPoint],
    scale: float = 12.0,
    fill: str = HEART_RED,
) -> str:
    """Render the heart as a standalone, self-contained SVG string."""
    if not points:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"></svg>'
    proj = project(points, scale=scale)
    path = svg_path(points, scale=proj.scale, origin_x=proj.origin_x, origin_y=proj.origin_y)
    width = round(proj.width)
    height = round(proj.height)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">'
        f'<path d="{path}" fill="{fill}" stroke="#ff758f" stroke-width="1.5"/>'
        f"</svg>"
    )
