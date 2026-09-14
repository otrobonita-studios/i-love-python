"""I love py - the app.

A demo that proves its own quality: every number on the screen is
produced by real tools running on this codebase, and the load test is
executed for real. Nothing is simulated; where something cannot run
(no network, no k6 binary) the UI says exactly that.
"""

from nicegui import app, ui

from art import links as art_links
from art import render as art_render
from explain import render as explain_render
from git_discipline import render as git_render
from loadtest import render as loadtest_render
from panel import render as panel_render
from review import render as review_render

APP_PORT = 8321


@app.get("/api/health")
def health() -> dict[str, str]:
    """The endpoint the load test hammers. Fast, honest, real."""
    return {"ok": "true", "service": "i-love-python", "heart": "real"}


panel_render.register_api()
art_render.register_routes()


@ui.page("/")
def index() -> None:
    art_render.apply_theme()
    art_render.render_nav()
    art_render.render_hero()
    explain_render.build_letter()
    art_render.render_curve_section()
    with ui.element("section").classes("ilp-section").props("id=quality"):
        panel_render.build_panel()
    with ui.element("section").classes("ilp-section").props("id=explain"):
        explain_render.build_explain_tab()
    explain_render.build_intro()
    with ui.element("section").classes("ilp-section").props("id=review"):
        review_render.build_review()
    with ui.element("section").classes("ilp-section").props("id=git"):
        git_render.build_git_tab()
    with ui.element("section").classes("ilp-section").props("id=load"):
        loadtest_render.build_loadtest_tab()
    with ui.element("section").classes("ilp-letter").props("id=listen"):
        ui.label("Listen").classes("ilp-letter-title")
        ui.link("Podcast", art_links.PODCAST_HREF, new_tab=True).classes("ilp-nav-item").props(
            "rel=noopener noreferrer"
        )


ui.run(
    title="I❤PY",
    port=APP_PORT,
    reload=False,
    show=False,
    uvicorn_logging_level="warning",
)
