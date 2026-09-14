"""Tests for art/theme.py (wiring-diagram tokens, no NiceGUI)."""

from art.theme import FONT_HREF, LIGHT, PAPER, font_links, root_css


def test_light_palette_matches_the_wiring_diagram() -> None:
    assert LIGHT.bg == "#f5f6f8"
    assert LIGHT.ink == "#14171f"
    assert LIGHT.accent == "#3552d6"
    assert LIGHT.accent_2 == "#e2593f"


def test_root_css_emits_custom_properties_and_chrome() -> None:
    css = root_css()
    assert "--ink: #14171f" in css
    assert "--accent: #3552d6" in css
    assert ".ilp-landing" in css
    assert ".ilp-caption" in css
    assert ".ilp-links" in css
    assert ".ilp-link" in css
    assert "IBM Plex Sans" in css
    assert "Archivo" in FONT_HREF
    assert "Newsreader" in FONT_HREF
    assert PAPER in css
    assert ".ilp-letter" in css
    assert "ilp-heart-beat 1.35s ease-in-out 1.9s 8 forwards" in css
    assert ".q-tab .q-tab__label" in css
    assert "Material Icons" in css


def test_tab_uppercase_is_label_only() -> None:
    css = root_css()
    tab_block = css.split(".q-tab {", 1)[1].split(".q-tab .q-tab__label", 1)[0]
    label_block = css.split(".q-tab .q-tab__label {", 1)[1].split("}", 1)[0]
    assert "text-transform: none" in tab_block
    assert "text-transform: uppercase" in label_block
    assert "letter-spacing: 0.1em" in label_block


def test_material_icons_use_ligature_metrics_not_flex_boxes() -> None:
    css = root_css()
    assert 'font-feature-settings: "liga" 1' in css
    assert "display: inline-block !important" in css
    assert "overflow: hidden !important" in css
    assert "letter-spacing: 0 !important" in css
    assert "text-transform: none !important" in css
    assert "width: 1em !important" in css
    assert "min-width: 1em !important" in css
    assert "max-width: 1em !important" in css
    assert ".q-icon.material-icons::before" in css
    assert "content: none !important" in css
    assert "display: inline-flex" not in css


def test_font_links_load_plex_and_archivo() -> None:
    html = font_links()
    assert "fonts.googleapis.com" in html
    assert "IBM+Plex+Sans" in html
    assert "Archivo" in html
    assert "Newsreader" in html
    assert FONT_HREF in html


def test_console_step_uses_ink_on_paper() -> None:
    css = root_css()
    assert ".ilp-console-step" in css
    assert ".ilp-console-you" in css
    assert ".ilp-console-cmd" in css
    assert ".ilp-console-out" in css
    assert ".ilp-console-why" in css
    step = css.split(".ilp-console-step {", 1)[1].split("}", 1)[0]
    you = css.split(".ilp-console-you {", 1)[1].split("}", 1)[0]
    cmd = css.split(".ilp-console-cmd {", 1)[1].split("}", 1)[0]
    out = css.split(".ilp-console-out {", 1)[1].split("}", 1)[0]
    why = css.split(".ilp-console-why {", 1)[1].split("}", 1)[0]
    assert "background: var(--surface-2)" in step
    assert "color: var(--ink)" in you
    assert "color: var(--accent)" in cmd
    assert "color: var(--ink)" in out
    assert "background: var(--surface)" in out
    assert "color: var(--ink-soft)" in why
    assert "gray-300" not in css
    assert "sky-300" not in css


def test_css_is_deterministic() -> None:
    assert root_css() == root_css()
