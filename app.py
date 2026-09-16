"""I love py - the app.

A demo that proves its own quality: every number on the screen is
produced by real tools running on this codebase, and the load test is
executed for real. Nothing is simulated; where something cannot run
(no network, no k6 binary) the UI says exactly that.
"""

from nicegui import app, ui

from art import favicon as art_favicon
from art import heart_api
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
heart_api.register_routes()


def chrome() -> None:
    """Shared shell: theme + top menu. Each view is its own route."""
    art_render.apply_theme()
    art_render.render_nav()


@ui.page("/")
def index() -> None:
    chrome()
    art_render.render_hero()


@ui.page("/letter")
def letter_page() -> None:
    chrome()
    explain_render.build_letter()


@ui.page("/curve")
def curve_page() -> None:
    chrome()
    art_render.render_curve_section()


@ui.page("/quality")
def quality_page() -> None:
    chrome()
    with ui.element("section").classes("ilp-section"):
        panel_render.build_panel()


@ui.page("/explain")
def explain_page() -> None:
    chrome()
    with ui.element("section").classes("ilp-section"):
        explain_render.build_explain_tab()


@ui.page("/review")
def review_page() -> None:
    chrome()
    with ui.element("section").classes("ilp-section"):
        review_render.build_review()


@ui.page("/git")
def git_page() -> None:
    chrome()
    with ui.element("section").classes("ilp-section"):
        git_render.build_git_tab()


@ui.page("/load")
def load_page() -> None:
    chrome()
    with ui.element("section").classes("ilp-section"):
        loadtest_render.build_loadtest_tab()


@ui.page("/listen")
def listen_page() -> None:
    chrome()
    art_render.render_podcast_section()


ui.run(
    title="I❤PY",
    port=APP_PORT,
    reload=False,
    show=False,
    uvicorn_logging_level="warning",
    favicon=art_favicon.FAVICON_PATH,
)
