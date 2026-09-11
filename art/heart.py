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
    y = 13.0 * math.cos(t) - 5.0 * math.cos(2.0 * t) - 2.0 * math.cos(3.0 * t)
    return HeartPoint(x=x, y=y)


def heart_points(n: int = 240) -> list[HeartPoint]:
    """Sample the heart curve at n points over one full period [0, 2*pi)."""
    if n < 3:
        raise ValueError("need at least 3 points to draw a heart")
    return [heart_point(2.0 * math.pi * i / n) for i in range(n)]


def svg_path(points: list[HeartPoint], scale: float = 12.0, origin_y: float = 0.0) -> str:
    """Turn heart points into an SVG path d-attribute (SVG y grows downward)."""
    if not points:
        return ""

    def project(point: HeartPoint) -> str:
        return f"{point.x * scale:.2f} {origin_y - point.y * scale:.2f}"

    parts = [f"M {project(points[0])}"]
    parts += [f"L {project(point)}" for point in points[1:]]
    parts.append("Z")
    return " ".join(parts)


def to_svg(
    points: list[HeartPoint],
    scale: float = 12.0,
    fill: str = "#ff4d6d",
) -> str:
    """Render the heart as a standalone, self-contained SVG string."""
    if not points:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"></svg>'
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    half_w = (max(xs) - min(xs)) / 2.0 * scale + 8.0
    half_h = (max(ys) - min(ys)) / 2.0 * scale + 8.0
    width = round(2 * half_w)
    height = round(2 * half_h)
    path = svg_path(points, scale=scale, origin_y=half_h - (max(ys) + min(ys)) / 2.0 * scale)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">'
        f'<path d="{path}" fill="{fill}" stroke="#ff758f" stroke-width="1.5"/>'
        f"</svg>"
    )
