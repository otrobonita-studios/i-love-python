"""Unit tests for art/logo.py (the Python-generated I ❤ PY wordmark)."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from art import logo
from art import render as art_render

SVG_NS = "{http://www.w3.org/2000/svg}"


def _root() -> ET.Element:
    return ET.fromstring(logo.logo_svg())


def test_logo_svg_is_wellformed_svg() -> None:
    root = _root()
    assert root.tag == f"{SVG_NS}svg"
    assert root.get("viewBox") == logo.VIEW_BOX
    paths = root.findall(f"{SVG_NS}path")
    assert len(paths) == 5
    for path in paths:
        assert path.get("d", "").startswith("M0,0")
        assert path.get("d", "").endswith("Z")
        assert path.get("fill")
        assert path.get("transform", "").startswith("translate(")


def test_logo_carries_no_third_party_provenance() -> None:
    # The reference export had an Anthropic C2PA manifest; ours must not.
    text = logo.logo_svg().lower()
    assert "c2pa" not in text
    assert "metadata" not in text
    assert "anthropic" not in text


def test_logo_is_deterministic() -> None:
    assert logo.logo_svg() == logo.logo_svg()


def test_letters_svg_omits_the_glaser_heart() -> None:
    svg = logo.letters_svg()
    root = ET.fromstring(svg)
    paths = root.findall(f"{SVG_NS}path")
    assert len(paths) == 4
    assert logo.HEART.fill not in svg
    assert logo.logo_svg().count("<path") == 5


def test_glyph_roster() -> None:
    fills = [glyph.fill for glyph in logo.GLYPHS]
    assert fills.count("#EE1C25") == 1  # exactly one heart
    assert fills.count("#000000") == 3  # I, P, Y
    assert fills.count("#FBFBFB") == 1  # P's counter


def test_p_counter_paints_last_on_top_of_p() -> None:
    # Document order is paint order; the off-white counter must be last.
    fills = [path.get("fill") for path in _root().findall(f"{SVG_NS}path")]
    assert fills[-1] == "#FBFBFB"
    assert "#000000" in fills[:-1]


def test_render_module_exposes_the_wordmark() -> None:
    assert art_render.logo_svg() == logo.logo_svg()
