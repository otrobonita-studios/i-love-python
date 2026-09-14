"""Canonical love-letter copy. Do not paraphrase."""

from __future__ import annotations

KICKER = "A letter, not a dashboard"
TITLE = "For the love of the inaccessible"
NUMPY_HREF = "https://numpy.org/"
SCIPY_HREF = "https://scipy.org/"
IDLE_CAPTION = "One line. The rest of the philosophy is in the output."
ZEN_CAPTION = (
    "this.py — the letter that shipped with the language. Rot13 in the source, "
    "plain English on the way out."
)
INLINE_CODE = (
    "npm install",
    "package.json",
    "__init__.py",
    "const",
    "venv",
    "def",
)
TOOL_MENTIONS = (
    "ruff",
    "mypy",
    "radon",
    "pytest",
    "bandit",
)


def typeset_html(text: str, *, link_tools: bool = False) -> str:
    """HTML for one paragraph. No Markdown — underscores in __init__.py stay."""
    import re
    from html import escape

    from explain import glossary

    tokens: list[tuple[str, str]] = [
        (
            "NumPy",
            f'<a class="ilp-link" href="{NUMPY_HREF}" target="_blank" '
            f'rel="noopener noreferrer">NumPy</a>',
        ),
        (
            "SciPy",
            f'<a class="ilp-link" href="{SCIPY_HREF}" target="_blank" '
            f'rel="noopener noreferrer">SciPy</a>',
        ),
    ]
    if link_tools:
        for mention, tool_name in glossary.MENTION_TO_TOOL.items():
            href = f"#{glossary.tool_anchor(tool_name)}"
            tokens.append((mention, f'<a class="ilp-link" href="{href}">{escape(mention)}</a>'))
    for word in INLINE_CODE:
        tokens.append((word, f'<code class="ilp-code">{escape(word)}</code>'))
    tokens.sort(key=lambda item: len(item[0]), reverse=True)
    pattern = "(" + "|".join(re.escape(word) for word, _ in tokens) + ")"
    repl = dict(tokens)
    out: list[str] = []
    for part in re.split(pattern, text):
        if not part:
            continue
        out.append(repl[part] if part in repl else escape(part))
    return "".join(out)


PARAGRAPHS: tuple[str, ...] = (
    "I guess everyone has been there. A potential love affair across the room, seemingly impossible to reach, or even to get a short talk with. Is that feeling the first sign of something true, or just the pull of what won't come close?",
    "I tried. But the outfit was hard to read, and that made the whole thing harder still. Or was it only playing hard to catch? This species had simply renamed everything I knew. No const, no npm install, no package.json. Instead: def, venv, __init__.py, and whitespace that means something. Not by intent, but by indentation.",
    "And it lived on the server, while I lived in the browser. A complicated wall to tear down.",
    "Years passed. I stayed in the browser. I'm a local guy after all.",
    "That backend language kept surfacing anyway — always somewhere adjacent, never quite mine.",
    "Then the models arrived. The agents, the orchestration frameworks, the whole new layer. Python-native, all of it.",
    "And suddenly there was a beautiful way in — to the inner soul of that particular accent. Because that's what it turned out to be: an accent. Different names for things I already knew. Not a different way of thinking. Just a different way of saying it. Probably one of the most uncomplicated tools for a purpose it was never designed for: simulating human thinking, reasoning, learning, and problem-solving. I just had to treat it — as a human.",
    "As a real partner. Understand the philosophy and you won't be afraid anymore: readability as an explicit design value, a shallow on-ramp, one obvious way to do it. And those same traits — plus a knack for wrapping fast C code — turned out to be exactly what scientific computing needed: NumPy, SciPy, and all the ML frameworks that followed.",
    "So I dropped the excuses and asked it out properly.",
    "What you'll find in this repo is, most people would say, anything but romantic. It's the opposite of a honeymoon. It's testing the relationship before it ruins the investment you're about to make — looking under the hood, finding the limits of a Python-only stack, and checking how good the tools really are when you ask them to prove it.",
    "That is a kind of love letter. Just not a soft one — and not an original one either. The best one was already written, and code has always been reused. So if you only ever write one line of Python, write this one:",
)

CLOSING = "The rest in the repo is not for the faint-hearted: ruff, mypy, radon, pytest and even a bandit. Dig in — especially if you know this thing better than I do."
