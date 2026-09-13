"""Heart art for the UI (pure Python -> SVG -> NiceGUI)."""

from nicegui import ui

from art import logo as art_logo
from art.heart import heart_points, to_svg

HEART_POINTS = 240


def render_heart(max_width: str = "max-w-64") -> None:
    """Draw the procedural heart. The SVG is generated in Python at runtime."""
    ui.html(to_svg(heart_points(HEART_POINTS))).classes(f"w-full {max_width}")


def render_logo(size: str = "h-10 w-10") -> None:
    """Draw the I ❤ PY wordmark. The SVG is generated in Python at runtime."""
    ui.html(art_logo.logo_svg()).classes(f"shrink-0 {size}")


def logo_svg() -> str:
    """Return the raw wordmark SVG string (used by the UI and tests)."""
    return art_logo.logo_svg()


def heart_svg() -> str:
    """Return the raw SVG string (used by the UI and tests)."""
    return to_svg(heart_points(HEART_POINTS))
