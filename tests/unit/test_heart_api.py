"""Unit tests for the heart SVG endpoint.

Everything worth asserting lives in the pure layer — parsing, clamping,
markup and the ETag. register_routes only wires those to Starlette, so the
tests need no server and no network.
"""

import xml.etree.ElementTree as ET

from art.heart import HEART_RED
from art.heart_api import (
    SAMPLES_MAX,
    SAMPLES_MIN,
    SCALE_MAX,
    SCALE_MIN,
    HeartRequest,
    build_request,
    clamp,
    etag_for,
    is_safe_colour,
    render,
    render_error,
)

SVG_NS = "{http://www.w3.org/2000/svg}"


def _valid(**overrides: object) -> HeartRequest:
    args: dict[str, object] = {
        "t": None,
        "samples": 240,
        "scale": 12.0,
        "stroke": HEART_RED,
        "background": "none",
    }
    args.update(overrides)
    request, reason = build_request(**args)  # type: ignore[arg-type]
    assert request is not None, reason
    return request


def test_rendered_svg_is_well_formed() -> None:
    ET.fromstring(render(_valid(t=1.0)))
    ET.fromstring(render_error("bad <input> & things"))


def test_error_svg_escapes_its_message() -> None:
    svg = render_error('<script>alert("x")</script>')
    assert "<script>" not in svg
    ET.fromstring(svg)


def test_dot_appears_only_when_t_is_given() -> None:
    assert "<circle" not in render(_valid())
    assert "<circle" in render(_valid(t=0.0))


def test_every_sampled_point_lands_inside_the_viewbox() -> None:
    # project() derives the box from the points, so this holds for any inputs.
    # The bound is not retyped here — it is read back off the rendered markup.
    for samples in (3, 17, 240, SAMPLES_MAX):
        root = ET.fromstring(render(_valid(samples=samples, t=5.3751234)))
        _, _, width, height = (float(v) for v in (root.get("viewBox") or "").split())
        for element in root.iter():
            if element.tag == f"{SVG_NS}path":
                coords = (element.get("d") or "").replace("M", "").replace("L", "")
                coords = coords.replace("Z", "").split()
                numbers = [float(value) for value in coords]
                xs, ys = numbers[0::2], numbers[1::2]
                assert min(xs) >= -1e-6 and max(xs) <= width + 1e-6
                assert min(ys) >= -1e-6 and max(ys) <= height + 1e-6


def test_the_lobes_reach_higher_than_the_cusp() -> None:
    # t = 0 gives y = 5, which reads like the maximum and is not: it is the
    # notch between the lobes. The lobes rise to y ~= 11.92 at t ~= 5.3751.
    # Anything that derives a viewBox from the formula by eye clips the top.
    from art.heart import heart_point

    assert abs(heart_point(0.0).y - 5.0) < 1e-9
    assert heart_point(5.3751234).y > 11.92


def test_colour_allowlist_rejects_attribute_injection() -> None:
    for good in ("#fff", HEART_RED, "#e8253cff", "red", "none", "rebeccapurple"):
        assert is_safe_colour(good), good
    for bad in ('red" onload="x', "url(#a)", "#12345", "", "#ggg", "a" * 40):
        assert not is_safe_colour(bad), bad


def test_bad_colour_is_refused_with_a_reason() -> None:
    request, reason = build_request(
        t=None, samples=240, scale=12.0, stroke='red" onload="x', background="none"
    )
    assert request is None
    assert "stroke" in reason


def test_non_finite_t_is_refused() -> None:
    request, reason = build_request(
        t=float("inf"), samples=240, scale=12.0, stroke=HEART_RED, background="none"
    )
    assert request is None
    assert "finite" in reason


def test_numbers_are_clamped_not_refused() -> None:
    assert _valid(samples=10_000_000).samples == SAMPLES_MAX
    assert _valid(samples=-5).samples == SAMPLES_MIN
    assert _valid(scale=1e9).scale == SCALE_MAX
    assert _valid(scale=-1.0).scale == SCALE_MIN
    assert clamp(5.0, 1.0, 10.0) == 5.0


def test_rendering_is_deterministic() -> None:
    request = _valid(t=2.5, samples=180)
    assert render(request) == render(request)


def test_etag_tracks_every_field() -> None:
    base = _valid(t=1.0)
    assert etag_for(base) == etag_for(_valid(t=1.0))
    for other in (
        _valid(t=1.01),
        _valid(t=1.0, samples=241),
        _valid(t=1.0, scale=13.0),
        _valid(t=1.0, stroke="#000"),
        _valid(t=1.0, background="#fff"),
    ):
        assert etag_for(base) != etag_for(other)
