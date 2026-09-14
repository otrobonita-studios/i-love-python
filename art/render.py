"""Heart art for the UI (pure Python -> SVG -> NiceGUI)."""

from nicegui import ui

from art import curve_copy, hero_copy, theme
from art import links as art_links
from art import logo as art_logo
from art.heart import heart_point, heart_points, lab_svg, overlay_svg, to_svg

HEART_POINTS = 240


def render_heart(max_width: str = "max-w-64") -> None:
    """Draw the procedural heart. The SVG is generated in Python at runtime."""
    ui.html(to_svg(heart_points(HEART_POINTS))).classes(f"w-full {max_width}")


def apply_theme() -> None:
    """Load the wiring-diagram fonts, tokens, and Quasar overrides."""
    ui.add_head_html(theme.font_links())
    ui.add_css(theme.root_css())
    ui.colors(
        primary=theme.INK,
        secondary=theme.MUTED,
        accent=theme.HEART_RED,
        dark=theme.INK,
        positive="#15803d",
        negative="#b91c1c",
        info=theme.INK,
        warning="#b45309",
    )


def render_logo(size: str = "h-10 w-10") -> None:
    """Draw the I ❤ PY wordmark. The SVG is generated in Python at runtime."""
    ui.html(art_logo.logo_svg()).classes(f"shrink-0 {size}")


def render_lockup(size: str = "") -> None:
    """I + PY letters with the parametric heart overlaid (draw, 8 beats, stop)."""
    classes = "ilp-lockup" + (f" {size}" if size else "")
    with ui.element("div").classes(classes):
        ui.html(art_logo.letters_svg()).classes("ilp-letters")
        overlay = ui.element("div").classes("ilp-heart-overlay")

        def paint_heart() -> None:
            overlay.clear()
            with overlay:
                ui.html(overlay_svg(heart_points(HEART_POINTS)))

        paint_heart()
        overlay.on("click", lambda _e: paint_heart())


def render_nav() -> None:
    """Sticky bar: centered max-w-6xl, mark left, sections + GitHub right."""
    with ui.element("header").classes("ilp-nav"):  # noqa: SIM117 — inner bar must nest
        with ui.element("div").classes("ilp-nav-inner"):
            with ui.link("", "/").classes("ilp-nav-mark"):
                ui.html(art_logo.nav_mark_svg())
                ui.label("Back to top").classes("ilp-sr-only")
            links = ui.element("nav").classes("ilp-nav-links")
            links.props("aria-label=Sections")
            with links:
                for name, href in art_links.NAV_ITEMS:
                    ui.link(name, href).classes("ilp-nav-item")
                ui.link("GitHub", art_links.REPO_HREF, new_tab=True).classes(
                    "ilp-nav-github"
                ).props("rel=noreferrer")
            ui.button(
                icon="menu",
                on_click=lambda: links.classes(toggle="ilp-nav-open"),
            ).props('flat round dense aria-label="Open menu"').classes("ilp-nav-burger")


def render_curve_lab() -> None:
    """t + samples as native range inputs; live x/y."""
    import math

    state = {"t": 0.0, "n": 64}
    drawing = ui.element("div").classes("w-full max-w-md")

    def paint() -> None:
        drawing.clear()
        n = max(8, int(state["n"]))
        pts = heart_points(n)
        pt = heart_point(state["t"])
        with drawing:
            ui.html(lab_svg(pts, state["t"]))
            ui.label(f"t = {state['t']:.2f}   x = {pt.x:.2f}   y = {pt.y:.2f}").classes("ilp-mono")

    def bind_range(key: str, min_v: float, max_v: float, step: float, value: float) -> None:
        el = ui.element("input").classes("w-full")
        el.props(f"type=range min={min_v} max={max_v} step={step} value={value}")

        def on_input(e: object) -> None:
            raw = getattr(e, "args", 0)
            if isinstance(raw, list):
                raw = raw[0] if raw else 0
            state[key] = float(raw)
            paint()

        el.on("input", on_input)

    ui.label("t").classes("ilp-mono")
    bind_range("t", 0, round(2 * math.pi, 2), 0.01, 0)
    ui.label("samples").classes("ilp-mono")
    bind_range("n", 8, 240, 1, 64)
    paint()


def render_curve_essay() -> None:
    """Canonical public essay only — no CLI notes."""
    for paragraph in curve_copy.PARAGRAPHS:
        ui.html(f"<p>{curve_copy.typeset_html(paragraph)}</p>", sanitize=False)


def render_hero() -> None:
    """First viewport: large lockup, caption, formula, ink button."""
    dialog = ui.dialog()
    with dialog, ui.element("div").classes("ilp-letter").style("min-width:min(36rem,90vw)"):
        ui.label(curve_copy.TITLE).classes("ilp-letter-title")
        ui.label(curve_copy.FORMULA).classes("ilp-mono")
        render_curve_essay()
        render_curve_lab()

    with ui.element("section").classes("ilp-hero w-full").props("id=hero"):
        ui.label(hero_copy.STUDIO_KICKER).classes("ilp-studio-kicker")
        render_lockup()
        ui.label(hero_copy.CAPTION).classes("ilp-caption")
        ui.label(hero_copy.MUTED).classes("ilp-muted")
        formula = ui.element("button").classes("ilp-formula")
        with formula:
            ui.label(hero_copy.FORMULA_LABEL)
            ui.label(hero_copy.FORMULA)
        formula.on("click", dialog.open)
        ui.link(hero_copy.READ_LETTER, "/letter").classes("ilp-btn-ink")
        ui.label(hero_copy.CLICK_HEART).classes("ilp-click-hint")


def render_curve_section() -> None:
    """Curve page: essay + the same lab."""
    with ui.element("section").classes("ilp-letter"):
        ui.label(curve_copy.TITLE).classes("ilp-letter-title")
        ui.label(curve_copy.FORMULA).classes("ilp-mono")
        render_curve_essay()
        render_curve_lab()


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
