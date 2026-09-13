"""Review tab: three deterministic personas reviewing real commits.

The diff being reviewed comes from this repository's real git history.
The verdicts come from rule-based analysis of that diff - no LLM, no
simulated approval.
"""

from nicegui import ui

from explain.translator import explain_diff
from review import personas, store

TONE_STYLE = {
    personas.TONE_OK: ("check_circle", "bg-green-100 text-green-800"),
    personas.TONE_CAUTION: ("warning", "bg-amber-100 text-amber-800"),
    personas.TONE_BLOCK: ("block", "bg-red-100 text-red-800"),
}
TONE_WORD = {
    personas.TONE_OK: "approves",
    personas.TONE_CAUTION: "cautions",
    personas.TONE_BLOCK: "blocks",
}


def _tone_badge(tone: str) -> None:
    icon, style = TONE_STYLE.get(tone, ("help", "bg-gray-100"))
    with ui.row().classes("items-center gap-1"):
        ui.icon(icon).classes("text-base")
        ui.label(TONE_WORD.get(tone, tone)).classes(
            f"rounded px-2 py-0.5 text-xs font-bold {style}"
        )


def _render_review(review: personas.Review, diff: str, content: ui.column) -> None:
    content.clear()
    with content:
        with ui.row().classes("items-center gap-3 w-full"):
            _tone_badge(review.consensus_tone)
            ui.label(review.consensus_note).classes("text-sm font-semibold")

        with ui.grid(columns=3).classes("w-full gap-3"):
            for verdict in review.verdicts:
                with ui.card().classes("w-full p-3 gap-2"):
                    with ui.row().classes("items-center justify-between w-full"):
                        ui.label(verdict.persona).classes("font-bold")
                        _tone_badge(verdict.tone)
                    ui.label(verdict.note).classes("text-xs text-gray-700")

        with ui.card().classes("w-full p-3 gap-2"):
            ui.label("Plain-English explanation of this diff").classes("font-semibold text-sm")
            for bullet in explain_diff(diff):
                with ui.row().classes("gap-2 items-start"):
                    ui.icon("minimize").classes("text-sm text-gray-400 mt-0.5")
                    ui.label(bullet).classes("text-xs")

        with ui.expansion("Raw diff - what the panel actually reviewed").classes("w-full"):
            ui.code(diff, language="diff").classes("text-xs max-h-96")


def build_review() -> None:
    commits = store.list_commits()
    with ui.card().classes("w-full p-4 gap-3"):
        with ui.row().classes("items-center gap-2"):
            ui.icon("groups").classes("text-2xl")
            ui.label("Review panel").classes("text-lg font-bold")
        ui.label(
            "Purist, Skeptic and Pragmatist review a real commit from this repo's history. "
            "Deterministic rules over the actual diff - no AI pretending."
        ).classes("text-xs text-gray-500")

        with ui.row().classes("items-center gap-2 w-full"):
            options = {commit.sha: f"{commit.sha}  {commit.subject}" for commit in commits}
            selector = ui.select(options, value=next(iter(options)), label="commit").classes(
                "flex-grow"
            )

        with ui.column().classes("w-full gap-3") as content:
            pass

        def _run_review(sha: str, target: ui.column) -> None:
            target.clear()
            with target:
                ui.spinner(size="md")
                ui.label("Pulling the real diff and consulting the panel...").classes("text-xs")
            diff = store.commit_diff(sha)
            review = personas.review_diff(diff, sha)
            _render_review(review, diff, target)

        with ui.row().classes("gap-2"):
            ui.button(
                "Review with the panel",
                on_click=lambda: _run_review(selector.value, content),
                icon="gavel",
            ).props("outline dense")

        ui.timer(0.4, lambda: _run_review(selector.value, content), once=True)
