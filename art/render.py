"""Heart art for the UI (pure Python -> SVG -> NiceGUI)."""

from nicegui import ui

from art import links as art_links
from art import logo as art_logo
from art import theme
from art.heart import heart_points, to_svg

HEART_POINTS = 240


def render_heart(max_width: str = "max-w-64") -> None:
    """Draw the procedural heart. The SVG is generated in Python at runtime."""
    ui.html(to_svg(heart_points(HEART_POINTS))).classes(f"w-full {max_width}")


def apply_theme() -> None:
    """Load the wiring-diagram fonts, tokens, and Quasar overrides."""
    ui.add_head_html(theme.font_links())
    ui.add_css(theme.root_css())
    ui.colors(
        primary=theme.LIGHT.accent,
        secondary=theme.LIGHT.accent_2,
        accent=theme.LIGHT.accent,
        dark=theme.LIGHT.ink,
        positive="#15803d",
        negative="#b91c1c",
        info=theme.LIGHT.accent,
        warning="#b45309",
    )


def render_logo(size: str = "h-10 w-10") -> None:
    """Draw the I ❤ PY wordmark. The SVG is generated in Python at runtime."""
    ui.html(art_logo.logo_svg()).classes(f"shrink-0 {size}")


def render_chrome_links() -> None:
    """Architectural map, podcast, and GitHub — the three chrome links."""
    with ui.row().classes("ilp-links"):
        for link in art_links.chrome_links():
            ui.link(link.label, link.href, new_tab=link.new_tab).classes("ilp-link").props(
                "rel=noopener noreferrer"
            )


def register_routes() -> None:
    """Serve the generated architectural map; quiet Chrome DevTools probe."""
    from fastapi.responses import FileResponse, PlainTextResponse
    from nicegui import app
    from starlette.responses import Response

    @app.get(art_links.WIRING_HREF)
    def architectural_map() -> Response:
        path = art_links.wiring_diagram_file()
        if not path.is_file():
            return PlainTextResponse(
                "Architectural map not generated. Run: python -m scripts.wiring_diagram",
                status_code=404,
            )
        return FileResponse(path, media_type="text/html; charset=utf-8")

    @app.get("/.well-known/appspecific/com.chrome.devtools.json")
    def chrome_devtools_probe() -> Response:
        # Chrome DevTools always requests this; empty 204 avoids a 404 log line.
        return Response(status_code=204)


def logo_svg() -> str:
    """Return the raw wordmark SVG string (used by the UI and tests)."""
    return art_logo.logo_svg()


def heart_svg() -> str:
    """Return the raw SVG string (used by the UI and tests)."""
    return to_svg(heart_points(HEART_POINTS))
