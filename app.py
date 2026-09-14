"""I love py - the app.

A demo that proves its own quality: every number on the screen is
produced by real tools running on this codebase, and the load test is
executed for real. Nothing is simulated; where something cannot run
(no network, no k6 binary) the UI says exactly that.
"""

from nicegui import app, ui

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
    with ui.column().classes("w-full items-center ilp-landing"):
        art_render.render_logo(size="w-40")
        ui.label("Rendered by the code you're about to inspect.").classes("ilp-caption")
        ui.label("a Python app that proves its own quality").classes("ilp-tagline")
        art_render.render_chrome_links()

    with ui.tabs().classes("w-full") as tabs:
        quality_tab = ui.tab("Quality", icon="monitoring")
        review_tab = ui.tab("Review", icon="groups")
        explain_tab = ui.tab("Explain", icon="translate")
        git_tab = ui.tab("Git discipline", icon="commit")
        load_tab = ui.tab("Load test", icon="speed")

    with ui.tab_panels(tabs, value=quality_tab).classes("w-full p-6"):
        with ui.tab_panel(quality_tab):
            panel_render.build_panel()
        with ui.tab_panel(review_tab):
            review_render.build_review()
        with ui.tab_panel(explain_tab):
            explain_render.build_explain_tab()
        with ui.tab_panel(git_tab):
            git_render.build_git_tab()
        with ui.tab_panel(load_tab):
            loadtest_render.build_loadtest_tab()

    with ui.footer().classes("items-center justify-center gap-3 py-3 flex-wrap"):
        ui.label("Otrobonita AI Labs — Jesper Karlsson")
        art_render.render_chrome_links()
        ui.label("pure Python, no fakes").classes("ilp-mono")


ui.run(
    title="I love py - quality you can see",
    port=APP_PORT,
    reload=False,
    show=False,
    uvicorn_logging_level="warning",
)
