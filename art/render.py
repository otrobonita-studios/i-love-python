"""Heart art for the UI (pure Python -> SVG -> NiceGUI)."""

from nicegui import events, ui

from art import curve_copy, hero_copy, podcast_copy, theme
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


def render_download_badge() -> None:
    """Small round badge at the heart's top-right corner: real download.

    A plain link to a Content-Disposition: attachment response -- the
    browser downloads generated/downloads/heart_curve.py, it doesn't
    navigate away. No JS fetch trick, no fake click handler.
    """
    badge = ui.link("", art_links.STANDALONE_HREF).classes("ilp-dl-badge")
    badge.tooltip("Download source — pure Python, runs standalone")
    with badge:
        ui.icon("download")


def render_curve_lab() -> None:
    """Parameter t + sample count as real, bound Quasar sliders; live x/y."""
    import math

    state = {"t": 0.0, "n": 64}
    with ui.element("div").classes("ilp-curve-wrap w-full max-w-md"):
        drawing = ui.element("div").classes("w-full")
        render_download_badge()

    def paint() -> None:
        drawing.clear()
        n = max(8, int(state["n"]))
        pts = heart_points(n)
        pt = heart_point(state["t"])
        with drawing:
            ui.html(lab_svg(pts, state["t"]))
            ui.label(f"t = {state['t']:.2f}   x = {pt.x:.2f}   y = {pt.y:.2f}").classes("ilp-mono")

    def bind_slider(
        label: str,
        key: str,
        *,
        min_v: float,
        max_v: float,
        step: float,
        value: float,
        display: str,
        caption: str = "",
    ) -> None:
        with ui.element("div").classes("ilp-slider-card"):
            with ui.row().classes("ilp-slider-row"):
                ui.label(label).classes("ilp-slider-label")
                value_label = ui.label(display.format(value)).classes("ilp-slider-value")

            def on_change(e: events.ValueChangeEventArguments[float | None]) -> None:
                state[key] = float(e.value or 0.0)
                value_label.set_text(display.format(state[key]))
                paint()

            ui.slider(min=min_v, max=max_v, step=step, value=value, on_change=on_change).props(
                "color=accent thumb-color=dark"
            ).classes("ilp-slider")
            if caption:
                ui.label(caption).classes("ilp-slider-caption")

    bind_slider(
        "Parameter t",
        "t",
        min_v=0,
        max_v=round(2 * math.pi, 2),
        step=0.01,
        value=0,
        display="{:.2f} rad",
    )
    bind_slider(
        "Samples",
        "n",
        min_v=8,
        max_v=240,
        step=1,
        value=64,
        display="{:.0f}",
        caption=(
            "Fewer points, a faceted valentine. More points, a smooth curve. "
            "heart_points() needs at least three."
        ),
    )
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


def render_curve_section() -> None:
    """Curve page: essay + the same lab."""
    with ui.element("section").classes("ilp-letter"):
        ui.label(curve_copy.TITLE).classes("ilp-letter-title")
        ui.label(curve_copy.FORMULA).classes("ilp-mono")
        render_curve_essay()
        render_curve_lab()


def render_podcast_player(episode: podcast_copy.Episode) -> None:
    """One episode: real <audio> element, red play button, live progress.

    ui.audio() is the actual element (native controls hidden). While
    playing, a short poll reads its real currentTime/duration via
    ui.run_javascript() + getHtmlElement() -- the numbers on screen come
    from the browser's own playback state, never a fabricated duration.
    Click-to-seek isn't wired yet (the underlying event wiring wants a
    proper live-browser check before it ships); play/pause and the live
    progress bar are real.
    """
    state = {"duration": 0.0, "playing": False}
    player = ui.audio(episode.href, controls=False)

    def fmt(seconds: float) -> str:
        total = max(0, int(seconds))
        return f"{total // 60}:{total % 60:02d}"

    def set_progress(fraction: float) -> None:
        pct = max(0.0, min(1.0, fraction)) * 100
        fill.style(f"width:{pct:.2f}%")
        thumb.style(f"left:{pct:.2f}%")

    with ui.element("div").classes("ilp-player-card"), ui.row().classes("ilp-player-row"):
        play_btn = ui.button(icon="play_arrow").props("round unelevated").classes("ilp-player-play")
        with ui.column().classes("ilp-player-body gap-0"):
            ui.label(episode.title).classes("ilp-player-title")
            ui.label(episode.byline).classes("ilp-player-byline")
            track = ui.element("div").classes("ilp-player-track")
            with track:
                fill = ui.element("div").classes("ilp-player-fill")
                thumb = ui.element("div").classes("ilp-player-thumb")
            with ui.row().classes("ilp-player-times"):
                current_label = ui.label("0:00").classes("ilp-player-time")
                duration_label = ui.label("--:--").classes("ilp-player-time")

    async def refresh() -> None:
        result = await ui.run_javascript(
            f'(() => {{ const a = getHtmlElement("{player.id}"); '
            "return [a.currentTime || 0, a.duration || 0]; })()"
        )
        current = float(result[0])
        duration = float(result[1])
        if duration and duration == duration:  # guards NaN before metadata loads
            state["duration"] = duration
            duration_label.set_text(fmt(duration))
            set_progress(current / duration)
        current_label.set_text(fmt(current))

    async def toggle_play() -> None:
        if state["playing"]:
            player.pause()
            state["playing"] = False
        else:
            player.play()
            state["playing"] = True
        play_btn.props(f"icon={'pause' if state['playing'] else 'play_arrow'}")
        await refresh()

    async def tick() -> None:
        if state["playing"]:
            await refresh()

    play_btn.on_click(toggle_play)
    ui.timer(0.3, tick)
    ui.timer(0.6, refresh, once=True)


def render_podcast_section() -> None:
    """Kicker, two-line headline, lede, and the real player -- one per episode."""
    from html import escape

    with ui.element("section").classes("ilp-letter"):
        ui.label(podcast_copy.KICKER).classes("ilp-letter-kicker")
        ui.html(
            f"{escape(podcast_copy.TITLE_LINE_1)}<br>{escape(podcast_copy.TITLE_LINE_2)}"
        ).classes("ilp-letter-title")
        ui.label(podcast_copy.LEDE).classes("ilp-lede")
        for episode in podcast_copy.EPISODES:
            render_podcast_player(episode)


def render_chrome_links() -> None:
    """Architectural map, podcast, and GitHub — the three chrome links."""
    with ui.row().classes("ilp-links"):
        for link in art_links.chrome_links():
            ui.link(link.label, link.href, new_tab=link.new_tab).classes("ilp-link").props(
                "rel=noopener noreferrer"
            )


def register_routes() -> None:
    """Serve the generated architectural map and standalone script; quiet Chrome DevTools probe."""
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

    @app.get(art_links.STANDALONE_HREF)
    def standalone_curve_script() -> Response:
        path = art_links.standalone_script_file()
        if not path.is_file():
            return PlainTextResponse(
                "Standalone script not generated. Run: python -m art.standalone_lab",
                status_code=404,
            )
        return FileResponse(path, media_type="text/x-python", filename="heart_curve.py")

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
