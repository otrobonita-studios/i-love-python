"""Visual tokens shared by the app and the wiring diagram.

Python is the source of truth. The diagram interpolates these into :root;
the NiceGUI app injects the same values via ui.add_css. There is no shared
.css file — lang_audit would treat a hand-authored stylesheet as source.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    """One theme: paper, type, hairlines, and the two accents."""

    bg: str
    surface: str
    surface_2: str
    ink: str
    ink_soft: str
    ink_faint: str
    line: str
    line_soft: str
    accent: str
    accent_soft: str
    accent_2: str
    accent_2_soft: str


# Same hex values as scripts/wiring_diagram.py HEAD_EXTRA. Keep them in lockstep.
LIGHT = Palette(
    bg="#f5f6f8",
    surface="#ffffff",
    surface_2="#eaecf1",
    ink="#14171f",
    ink_soft="#565e6d",
    ink_faint="#8890a0",
    line="#d7dbe3",
    line_soft="#e7e9ee",
    accent="#3552d6",
    accent_soft="#e4e9fb",
    accent_2="#e2593f",
    accent_2_soft="#fbe4de",
)

FONT_HREF = (
    "https://fonts.googleapis.com/css2?family=Archivo:wght@700;800"
    "&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400"
    "&family=IBM+Plex+Mono:wght@400;500"
    "&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400"
    "&display=swap"
)

# Landing / letter paper (docs/spec-love.md §1.5). App chrome stays LIGHT.
PAPER = "#F4EEE4"
LETTER_SURFACE = "#FBF7F0"
LETTER_INK = "#161412"
HEART_RED = "#EE1C25"


def font_links() -> str:
    """<link> tags that load Archivo, IBM Plex, and Newsreader."""
    return (
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link rel="stylesheet" href="{FONT_HREF}">'
    )


def root_css(palette: Palette = LIGHT) -> str:
    """App chrome: paper, type, flattened cards, instrument tabs."""
    p = palette
    return f"""
:root {{
  --bg: {p.bg};
  --surface: {p.surface};
  --surface-2: {p.surface_2};
  --ink: {p.ink};
  --ink-soft: {p.ink_soft};
  --ink-faint: {p.ink_faint};
  --line: {p.line};
  --line-soft: {p.line_soft};
  --accent: {p.accent};
  --accent-soft: {p.accent_soft};
  --accent-2: {p.accent_2};
  --accent-2-soft: {p.accent_2_soft};
}}
html, body, #app, .q-layout, .q-page, .nicegui-content {{
  background: var(--bg) !important;
  color: var(--ink);
  font-family: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif;
}}
.ilp-landing {{
  padding: 2.5rem 1.5rem 1.25rem;
  gap: 0.5rem;
  border-bottom: 1px solid var(--line);
  background: {PAPER};
}}
.ilp-caption {{
  font-style: italic;
  color: var(--ink-soft);
  font-size: 1.125rem;
  margin: 0;
}}
.ilp-tagline {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  color: var(--ink-faint);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-size: 1rem;
  margin: 0;
}}
.ilp-links {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.5rem 1.5rem;
  margin: 0.35rem 0 0;
}}
.ilp-links a.ilp-link,
.ilp-link {{
  color: var(--accent) !important;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 1rem;
  text-decoration: none;
}}
.ilp-links a.ilp-link:hover,
.ilp-link:hover {{
  color: var(--accent-2) !important;
  text-decoration: underline;
}}
.q-header {{
  background: var(--surface) !important;
  color: var(--ink) !important;
  box-shadow: none !important;
  border-bottom: 1px solid var(--line);
}}
.q-footer {{
  background: var(--surface) !important;
  color: var(--ink-faint) !important;
  box-shadow: none !important;
  border-top: 1px solid var(--line);
}}
.q-tabs {{
  background: var(--surface);
  border-bottom: 1px solid var(--line);
}}
.q-tab {{
  color: var(--ink-soft) !important;
  /* Quasar uppercases the whole tab; that turns "monitoring" into a
     missing ligature plus an empty 24x24 box beside the real glyph. */
  text-transform: none;
}}
.q-tab .q-tab__label {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}}
.q-tab--active {{
  color: var(--accent) !important;
}}
.q-tab__indicator {{
  background: var(--accent) !important;
  height: 2px;
}}
/* Ligature icons must use Google's Material Icons metrics, not Plex /
   uppercase / letter-spacing, and not Quasar's inline-flex + ::before
   1em boxes (those draw the glyph beside an empty 24x24 square). */
.q-icon,
.material-icons {{
  font-family: "Material Icons" !important;
  font-weight: normal;
  font-style: normal;
  font-feature-settings: "liga" 1;
  -webkit-font-feature-settings: "liga" 1;
  font-variant-ligatures: common-ligatures;
  letter-spacing: 0 !important;
  text-transform: none !important;
  line-height: 1 !important;
  display: inline-block !important;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  /* Quasar size= sets font-size only. Without a 1em box, a flex row
     sizes the icon to the ligature *name* ("monitoring"), so the glyph
     sits in the corner of a wide empty square. */
  width: 1em !important;
  height: 1em !important;
  min-width: 1em !important;
  max-width: 1em !important;
  overflow: hidden !important;
  flex: 0 0 1em;
  vertical-align: middle;
  text-align: center;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}}
.q-icon.material-icons::before,
.q-icon.material-icons::after {{
  content: none !important;
  display: none !important;
  width: 0 !important;
  height: 0 !important;
}}
.q-card {{
  background: var(--surface) !important;
  box-shadow: none !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
}}
.q-tab-panels {{
  background: transparent !important;
}}
.ilp-lede {{
  color: var(--ink-soft);
  line-height: 1.55;
  max-width: 72ch;
}}
.ilp-mono {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
}}
/* Ask-git transcript: ink on paper. Nested q-cards cannot go dark —
   .q-card forces --surface, which kills light-on-dark utility colors. */
.ilp-console-step {{
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.85rem 1rem;
  background: var(--surface-2);
  border: 1px solid var(--line);
  border-radius: 10px;
  color: var(--ink);
}}
.ilp-console-you {{
  color: var(--ink);
}}
.ilp-console-cmd {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  color: var(--accent);
}}
.ilp-console-out {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  color: var(--ink);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin: 0;
  white-space: pre-wrap;
  overflow: auto;
  max-height: 12rem;
  width: 100%;
}}
.ilp-console-why {{
  color: var(--ink-soft);
}}
.ilp-lockup {{
  position: relative;
  width: 10rem;
  aspect-ratio: 1;
}}
.ilp-letters {{
  width: 100%;
  display: block;
}}
.ilp-heart-overlay {{
  position: absolute;
  left: calc(39% + 10px);
  top: 14.4%;
  width: 44%;
  cursor: pointer;
  line-height: 0;
}}
.ilp-heart {{
  width: 100%;
  height: auto;
  display: block;
  transform-origin: 50% 50%;
  animation: ilp-heart-beat 1.35s ease-in-out 1.9s 8 forwards;
}}
.ilp-heart-path {{
  fill-opacity: 0;
  animation: ilp-heart-draw 1.35s ease-out forwards,
             ilp-heart-fill 0.55s ease-out 1.35s forwards;
}}
@keyframes ilp-heart-draw {{
  to {{ stroke-dashoffset: 0; }}
}}
@keyframes ilp-heart-fill {{
  from {{ fill-opacity: 0; }}
  to {{ fill-opacity: 1; }}
}}
@keyframes ilp-heart-beat {{
  0%, 100% {{ transform: scale(1); }}
  15% {{ transform: scale(1.045); }}
  30% {{ transform: scale(1); }}
  45% {{ transform: scale(1.03); }}
  60% {{ transform: scale(1); }}
}}
@media (prefers-reduced-motion: reduce) {{
  .ilp-heart, .ilp-heart-path {{
    animation: none;
  }}
  .ilp-heart-path {{
    fill-opacity: 1;
    stroke-dashoffset: 0;
  }}
}}
.ilp-letter {{
  width: 100%;
  max-width: 62ch;
  margin: 0 auto;
  padding: 2rem 1.5rem 2.5rem;
  background: {LETTER_SURFACE};
  color: {LETTER_INK};
  font-family: Newsreader, Palatino, "Palatino Linotype", "Iowan Old Style", serif;
  font-size: 1.08rem;
  line-height: 1.7;
}}
.ilp-letter-kicker {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 1rem;
  color: var(--ink-soft);
  margin: 0 0 0.5rem;
}}
.ilp-letter-title {{
  font-family: Newsreader, Palatino, "Palatino Linotype", serif;
  font-size: 2rem;
  font-weight: 600;
  margin: 0 0 1.25rem;
}}
.ilp-letter p {{
  margin: 0 0 1em;
}}
.ilp-letter code {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.95em;
}}
.ilp-this-row {{
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
}}
.ilp-this-well {{
  flex: 1 1 auto;
  min-width: 0;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0.65rem 1rem;
}}
.ilp-this-row .q-btn {{
  flex: 0 0 auto;
}}
.ilp-zen-out {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  white-space: pre-wrap;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: {LETTER_INK};
}}
.ilp-this-caption {{
  color: var(--ink-soft);
  margin: 0;
}}
.ilp-kind {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  color: var(--ink-soft);
}}
"""
