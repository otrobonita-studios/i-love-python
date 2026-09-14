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

# Page tokens from docs/spec-love.md §10.2. LIGHT stays the wiring-diagram palette.
PAPER = "#F4EEE4"
SURFACE = "#FBF7F0"
SURFACE_2 = "#EFE8DB"
INK = "#161412"
MUTED = "#6B645A"
SUBTLE = "#8A8378"
HEART_RED = "#EE1C25"
HAIR = "rgba(22,20,18,0.06)"
LETTER_SURFACE = SURFACE
LETTER_INK = INK


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
  --color-surface: {PAPER};
}}
html, body, #app, .q-layout, .q-page, .nicegui-content {{
  background: {PAPER} !important;
  color: {INK} !important;
  font-family: Newsreader, Palatino, "Palatino Linotype", "Iowan Old Style", ui-serif, serif;
}}
a, a.ilp-link, .nicegui-link {{
  color: {INK} !important;
  text-decoration: none;
}}
a:hover, a.ilp-link:hover, .nicegui-link:hover {{
  color: {INK} !important;
  text-decoration: underline;
}}
.nicegui-content {{
  align-items: stretch !important;
  width: 100%;
}}
.ilp-hero {{
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.85rem;
  padding: 2.5rem 1.5rem 3rem;
  background: transparent;
  border: none;
}}
.ilp-studio-kicker {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  font-size: 0.85rem;
  color: {SUBTLE};
  margin: 0 0 1.25rem;
}}
.ilp-caption {{
  font-style: normal;
  font-family: Newsreader, Palatino, "Palatino Linotype", ui-serif, serif;
  color: {INK};
  font-size: 1.65rem;
  line-height: 1.3;
  margin: 1.25rem 0 0;
  max-width: 22em;
}}
.ilp-muted {{
  color: {MUTED};
  font-size: 1.125rem;
  line-height: 1.5;
  max-width: 28em;
  margin: 0.25rem 0 0;
}}
.ilp-formula {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  color: {SUBTLE};
  background: transparent;
  border: none;
  cursor: pointer;
  text-align: center;
  line-height: 1.45;
  margin: 1rem 0 0.5rem;
  padding: 0;
}}
.ilp-formula:hover {{
  text-decoration: underline;
}}
.ilp-btn-ink {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 3rem;
  padding: 0 1.4rem;
  margin-top: 0.75rem;
  background: {INK} !important;
  color: {PAPER} !important;
  border-radius: 8px;
  text-decoration: none !important;
  font-family: Newsreader, Palatino, ui-serif, serif;
  font-size: 1.05rem;
}}
.ilp-btn-ink:hover {{
  text-decoration: none !important;
  opacity: 0.92;
}}
.ilp-click-hint {{
  color: {SUBTLE};
  font-size: 1rem;
  margin: 0.4rem 0 0;
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
  background: {SURFACE} !important;
  box-shadow: none !important;
  border: 1px solid {HAIR} !important;
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
  width: min(26rem, 78vw);
  max-width: 460px;
  min-width: 280px;
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
  max-width: 40rem;
  margin: 0 auto;
  padding: 3rem 1.5rem 4rem;
  background: transparent;
  color: {INK};
  font-family: Newsreader, Palatino, "Palatino Linotype", "Iowan Old Style", ui-serif, serif;
  font-size: 1.08rem;
  line-height: 1.7;
}}
.ilp-letter-kicker {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 0.9rem;
  color: {SUBTLE};
  margin: 0 0 0.5rem;
}}
.ilp-letter-title {{
  font-family: Newsreader, Palatino, "Palatino Linotype", ui-serif, serif;
  font-size: 2.6rem;
  font-weight: 600;
  line-height: 1.15;
  margin: 0 0 1.5rem;
}}
.ilp-letter p {{
  margin: 0 0 1em;
}}
.ilp-code {{
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 0.95em;
  white-space: nowrap;
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
  background: {SURFACE_2};
  border: 1px solid {HAIR};
  border-radius: 8px;
  padding: 0.65rem 1rem;
}}
.ilp-this-row .q-btn {{
  flex: 0 0 auto;
  background: {HEART_RED} !important;
  color: #fff !important;
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
  color: {MUTED};
}}
.ilp-nav {{
  position: sticky;
  top: 0;
  z-index: 40;
  width: 100%;
  background: {PAPER};
  border-bottom: 1px solid {HAIR};
}}
.ilp-nav-inner {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  height: 4rem;
  max-width: 72rem;
  margin: 0 auto;
  padding: 0 1rem;
}}
@media (min-width: 640px) {{
  .ilp-nav-inner {{
    padding: 0 1.5rem;
  }}
}}
.ilp-nav-mark {{
  display: flex;
  align-items: center;
  flex-shrink: 0;
}}
.ilp-nav-mark svg {{
  display: block;
  width: 2.5rem;
  height: 2.5rem;
}}
.ilp-sr-only {{
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}}
.ilp-nav-links {{
  display: none;
  align-items: center;
  gap: 0.25rem;
  font-family: Newsreader, Palatino, ui-serif, serif;
}}
@media (min-width: 1024px) {{
  .ilp-nav-links {{
    display: flex;
  }}
}}
.ilp-nav-item {{
  color: {MUTED} !important;
  text-decoration: none !important;
  font-size: 0.875rem;
  padding: 0.5rem 0.625rem;
  border-radius: 6px;
}}
.ilp-nav-item:hover {{
  color: {INK} !important;
  text-decoration: none !important;
}}
.ilp-nav-github {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 2.25rem;
  margin-left: 0.5rem;
  padding: 0 0.75rem;
  border: 1px solid {HAIR};
  border-radius: 6px;
  color: {INK} !important;
  text-decoration: none !important;
  font-size: 0.875rem;
  background: transparent;
}}
.ilp-nav-github:hover {{
  text-decoration: none !important;
  background: {SURFACE_2};
}}
.ilp-nav-burger {{
  display: inline-flex;
  margin-left: auto;
}}
@media (min-width: 1024px) {{
  .ilp-nav-burger {{
    display: none;
  }}
}}
@media (max-width: 1023px) {{
  .ilp-nav-links.ilp-nav-open {{
    display: flex;
    flex-direction: column;
    align-items: stretch;
    position: absolute;
    top: 4rem;
    left: 0;
    right: 0;
    background: {PAPER};
    padding: 1rem 1.25rem 1.25rem;
    border-bottom: 1px solid {HAIR};
  }}
}}
.ilp-section {{
  width: 100%;
  max-width: 72rem;
  margin: 0 auto;
  padding: 3rem 1.5rem 4rem;
}}
.ilp-q-card {{
  background: {SURFACE} !important;
  border: 1px solid {HAIR} !important;
  box-shadow: none !important;
}}
"""
