"""Public curve essay. Canonical copy only — no CLI notes."""

from __future__ import annotations

NY_HREF = "https://en.wikipedia.org/wiki/I_Love_New_York"
GLASER_HREF = "https://en.wikipedia.org/wiki/Milton_Glaser"
TITLE = "How Python thinks of its heart"
FORMULA = "x = 16 sin³ t    y = 13 cos t − 5 cos 2t − 2 cos 3t − cos 4t"


def typeset_html(text: str) -> str:
    """Link I ❤ NY and Milton Glaser. No CLI notes."""
    import re
    from html import escape

    tokens = (
        (
            "Milton Glaser",
            f'<a class="ilp-link" href="{GLASER_HREF}" target="_blank" '
            f'rel="noopener noreferrer">Milton Glaser</a>',
        ),
        (
            "I ❤ NY",
            f'<a class="ilp-link" href="{NY_HREF}" target="_blank" '
            f'rel="noopener noreferrer">I ❤ NY</a>',
        ),
    )
    pattern = "(" + "|".join(re.escape(word) for word, _ in tokens) + ")"
    repl = dict(tokens)
    out: list[str] = []
    for part in re.split(pattern, text):
        if not part:
            continue
        out.append(repl[part] if part in repl else escape(part))
    return "".join(out)


PARAGRAPHS: tuple[str, ...] = (
    "Python will draw you a whole interface without leaving the language. That is a real gift: one runtime, one voice, the browser as a guest. What it does not have is React’s ocean of libraries, or the ease of a component you install and forget.",
    "So you choose Python on purpose. When the UI is light. When a conversation does most of the work — a chat, a letter, a panel that tells the truth — and the page is a room for that, not an application. This heart is that kind of UI.",
    "You’ve seen I ❤ NY your whole life: a serif I, a fat red heart, two letters underneath. In 1977 a New York designer named Milton Glaser sketched it with a crayon in the back of a cab. The doodle outlived the man. Almost nobody can name him. Almost everybody can draw the mark.",
    "This one rhymes with it — I ❤ PY — but it is not a tracing and it is not clip-art. It is sampled from a closed parametric curve, the same function the tests lock down. Drag t. Watch the point walk the outline. Math you can feel — in the language that drew it. Python on a string!",
)
