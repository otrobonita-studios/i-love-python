"""House letter of introduction. Canonical copy — do not paraphrase."""

from __future__ import annotations

from dataclasses import dataclass


def typeset_html(text: str) -> str:
    """Turn `backticks` into code. No Markdown emphasis."""
    import re
    from html import escape

    parts = re.split(r"`([^`]+)`", text)
    out: list[str] = []
    for index, part in enumerate(parts):
        if index % 2:
            out.append(f'<code class="ilp-code">{escape(part)}</code>')
        else:
            out.append(escape(part))
    return "".join(out)


KICKER = "A letter of introduction"
TITLE = "I would like you to meet the house."
SIGN_OFF = ("Yours,", "Jesper", "Otrobonita AI Labs")
PLAN_HEADING = "Six rooms. One language. Nobody skips a floor."
STACK = ("browser", "app.py", "render.py", "logic", "real tools")

PARAGRAPHS: tuple[str, ...] = (
    "Dear colleague —",
    "I am writing to introduce you to a house I have come to trust. I have lived in many codebases. Some of them were charming. Some of them were traps with good furniture. This one is neither a cathedral nor a studio apartment. It is a small house with six rooms and a rule so simple you can say it at the door: every request walks downstairs, and nobody skips a floor.",
    "The front door is the browser. Behind it sits a concierge — `app.py` — who only points. It does not cook. It does not argue. It does not keep secrets in its pockets.",
    "One floor down, the rooms are furnished by thin views — `render.py`. They lay the table. They do not do the math, they do not go outside, they do not decide what is true.",
    "Below that, the people who actually know things. Logic. Pure Python. You can ask them questions without starting the house, without the network, without a browser. That is how you know they are honest: they work in daylight.",
    "And at the cellar door: real tools. ruff, mypy, pytest, git, the load runner. Not portraits of tools. The tools themselves. If one is missing, the house says so. It will not pretend a pass.",
    "I recommend this arrangement without reservation, and I will tell you why: when something breaks, you know which floor to walk to. When someone new arrives, you can give them this letter instead of a week of folklore.",
    "The six rooms are enclosed below, so you are not lost. Landing is the first impression. Quality is the medical chart — you have already met the instruments. Explain is the friend who translates. Review is three colleagues who never quite agree. Git is how you ask the house about its own past. Load is Python writing a letter in another dialect, sending it out, and reading the reply — and always naming who spoke.",
    "One language built the house. Everything else is generated, headed, and named. That is not a slogan. It is the lock on the cellar door.",
    "Walk through. The rooms will introduce themselves.",
)


@dataclass(frozen=True)
class Room:
    """One room on the enclosed floor plan."""

    number: str
    name: str
    line: str
    path: str
    href: str


ROOMS: tuple[Room, ...] = (
    Room(
        "01",
        "Landing",
        "The first impression. A heart of sine and cosine, a wordmark Python owns. No clip-art in a drawer.",
        "art/heart.py",
        "#",
    ),
    Room(
        "02",
        "Quality",
        "The medical chart. Eight real instruments, read aloud. If one is missing, the house says so — never a fake pass.",
        "panel/telemetry.py",
        "#quality",
    ),
    Room(
        "03",
        "Explain",
        "The friend who translates. What changed, why it matters, what could go wrong — in the language you already speak. No network.",
        "explain/translator.py",
        "#explain",
    ),
    Room(
        "04",
        "Review",
        "Three colleagues who never quite agree. They read real diffs. The raw patch is one door away if you want to argue.",
        "review/personas.py",
        "#review",
    ),
    Room(
        "05",
        "Git",
        "Ask the house about its own past. log, show, blame — a conversation, not decoration. Beside it, a hallway of how not to live.",
        "git_discipline/console.py",
        "#git",
    ),
    Room(
        "06",
        "Load",
        "Python writes a letter in another dialect, sends it out, and reads the reply. The speaker is always named.",
        "loadtest/spec.py",
        "#load",
    ),
)
