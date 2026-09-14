"""Unit tests for art/logo.py (the Python-generated I ❤ PY wordmark)."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from itertools import pairwise

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
    assert len(paths) == 4
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


def test_nav_mark_svg_is_the_full_wordmark() -> None:
    svg = logo.nav_mark_svg()
    root = ET.fromstring(svg)
    assert root.get("aria-label") == "I love PY"
    assert root.find(f"{SVG_NS}title") is not None
    assert len(root.findall(f"{SVG_NS}path")) == 4
    assert logo.HEART.fill in svg
    assert "var(--color-surface)" not in svg
    assert "#FBFBFB" not in svg


def test_letters_svg_omits_the_glaser_heart() -> None:
    svg = logo.letters_svg()
    root = ET.fromstring(svg)
    paths = root.findall(f"{SVG_NS}path")
    assert len(paths) == 3
    assert logo.HEART.fill not in svg
    assert logo.logo_svg().count("<path") == 4


def test_glyph_roster() -> None:
    fills = [glyph.fill for glyph in logo.GLYPHS]
    assert fills.count("#EE1C25") == 1  # exactly one heart
    assert fills.count("#000000") == 3  # I, P, Y
    assert logo.P_COUNTER not in logo.GLYPHS
    assert logo.P_COUNTER not in logo.LETTER_GLYPHS


def test_offset_path_translates_polyline_points() -> None:
    assert logo._offset_path("M0,0 L10,-5 Z", 150, 70) == "M150,70 L160,65 Z"


def _evenodd_contains(d: str, x: float, y: float) -> bool:
    """True if (x, y) is painted under SVG fill-rule=evenodd."""
    inside = False
    current: list[tuple[int, int]] = []
    subpaths: list[list[tuple[int, int]]] = []
    for cmd, xs, ys in logo._POINT.findall(d):
        if cmd == "M" and current:
            subpaths.append(current)
            current = []
        current.append((int(xs), int(ys)))
    if current:
        subpaths.append(current)
    for poly in subpaths:
        closed = [*poly, poly[0]]
        for (x1, y1), (x2, y2) in pairwise(closed):
            if (y1 > y) != (y2 > y):
                x_at = (x2 - x1) * (y - y1) / (y2 - y1) + x1
                if x < x_at:
                    inside = not inside
    return inside


def test_p_counter_is_cut_out_of_the_p() -> None:
    # The bowl is a hole in P (evenodd), not a white object painted on top.
    p = next(
        path
        for path in _root().findall(f"{SVG_NS}path")
        if path.get("transform") == f"translate({logo.LETTER_P.x},{logo.LETTER_P.y})"
    )
    hole_origin = f"M{logo.P_COUNTER.x - logo.LETTER_P.x},{logo.P_COUNTER.y - logo.LETTER_P.y}"
    assert p.get("fill-rule") == "evenodd"
    assert p.get("fill") == logo.LETTER_P.fill
    assert p.get("d", "").startswith(logo.LETTER_P.d)
    assert hole_origin in (p.get("d") or "")
    assert "#FBFBFB" not in logo.logo_svg()
    assert "#FBFBFB" not in logo.letters_svg()
    assert "#FBFBFB" not in logo.nav_mark_svg()
    hole_x = (logo.P_COUNTER.x - logo.LETTER_P.x) + 40
    hole_y = (logo.P_COUNTER.y - logo.LETTER_P.y) + 50
    assert _evenodd_contains(logo.LETTER_P.d, hole_x, hole_y) is True
    assert _evenodd_contains(p.get("d") or "", hole_x, hole_y) is False
    assert _evenodd_contains(p.get("d") or "", 50, 200) is True


def test_render_module_exposes_the_wordmark() -> None:
    assert art_render.logo_svg() == logo.logo_svg()
