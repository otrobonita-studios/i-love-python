"""An HTTP endpoint that returns the heart as SVG, and returns nothing else.

The geometry is not reimplemented here. art.heart already samples the curve
and, importantly, derives the viewBox from the sampled points rather than from
hardcoded bounds — so the box always contains the curve, whatever the caller
asks for. This module only parses a query string, clamps it, and sets headers.

Everything it serves is SVG, including errors. An <img> tag handed a JSON error
object shows a broken-image icon and explains nothing; the status code carries
the verdict for whatever reads headers, and the body carries it for whatever
renders.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

from art.heart import HEART_RED, heart_point, heart_points, project, svg_path

SVG_MEDIA_TYPE = "image/svg+xml; charset=utf-8"
# The response is a pure function of the query string, so a different picture
# always has a different URL and this can be cached indefinitely.
CACHE_CONTROL = "public, max-age=31536000, immutable"

SAMPLES_MIN = 3
SAMPLES_MAX = 2000
SAMPLES_DEFAULT = 240
SCALE_MIN = 1.0
SCALE_MAX = 80.0
SCALE_DEFAULT = 12.0
MAX_COLOUR_LENGTH = 32
_HEX_LENGTHS = frozenset({3, 6, 8})


@dataclass(frozen=True)
class HeartRequest:
    """Validated, clamped inputs. Constructing one cannot fail."""

    t: float | None = None
    samples: int = SAMPLES_DEFAULT
    scale: float = SCALE_DEFAULT
    stroke: str = HEART_RED
    background: str = "none"

    @property
    def cache_key(self) -> str:
        fields = (self.t, self.samples, self.scale, self.stroke, self.background)
        return "|".join(str(field) for field in fields)


def clamp(value: float, low: float, high: float) -> float:
    """Pull a number back inside its range instead of refusing it."""
    return max(low, min(high, value))


def is_safe_colour(value: str) -> bool:
    """Accept only what can be dropped into an SVG attribute unescaped.

    A colour ends up inside an attribute, so an unchecked one is markup
    injection: `red" onload="…` would break out. Rather than escape and hope,
    the permitted shapes are enumerated — #rgb, #rrggbb, #rrggbbaa, a bare CSS
    keyword, or none.
    """
    text = value.strip()
    if not text or len(text) > MAX_COLOUR_LENGTH:
        return False
    if text.startswith("#"):
        body = text[1:]
        return len(body) in _HEX_LENGTHS and all(c in "0123456789abcdefABCDEF" for c in body)
    return text.replace("-", "").isalpha()


def etag_for(request: HeartRequest) -> str:
    """A strong ETag, which the rendering being deterministic makes honest."""
    digest = hashlib.sha256(request.cache_key.encode("utf-8")).hexdigest()[:16]
    return f'"{digest}"'


def render(request: HeartRequest) -> str:
    """Draw the curve, and the point at t when one was asked for."""
    points = heart_points(request.samples)
    proj = project(points, scale=request.scale)
    path = svg_path(points, scale=proj.scale, origin_x=proj.origin_x, origin_y=proj.origin_y)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {proj.width:.2f} {proj.height:.2f}" '
        f'width="{proj.width:.0f}" height="{proj.height:.0f}" '
        f'role="img" aria-label="parametric heart">',
        "<title>x = 16*sin(t)^3, y = 13*cos(t) - 5*cos(2t) - 2*cos(3t) - cos(4t)</title>",
    ]
    if request.background != "none":
        parts.append(
            f'<rect width="{proj.width:.2f}" height="{proj.height:.2f}" '
            f'fill="{request.background}"/>'
        )
    parts.append(
        f'<path d="{path}" fill="none" stroke="{request.stroke}" '
        f'stroke-width="2" stroke-linejoin="round"/>'
    )
    if request.t is not None:
        px, py = proj.xy(heart_point(request.t))
        parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="5" fill="{request.stroke}"/>')
    parts.append("</svg>")
    return "".join(parts)


def render_error(message: str) -> str:
    """An error an <img> tag can actually display."""
    safe = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")[:120]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 80" '
        'width="320" height="80" role="img" aria-label="error">'
        '<rect width="320" height="80" fill="#1b1512"/>'
        '<text x="160" y="44" text-anchor="middle" font-family="ui-monospace,monospace" '
        f'font-size="12" fill="{HEART_RED}">{safe}</text></svg>'
    )


def build_request(
    *,
    t: float | None,
    samples: int,
    scale: float,
    stroke: str,
    background: str,
) -> tuple[HeartRequest | None, str]:
    """Validate raw inputs. Returns the request, or None and a reason.

    Numbers are clamped and colours are rejected. A caller asking for five
    million samples wants a picture, and the cap is what protects the server;
    a colour has no sensible nearest-valid value and cannot be clamped safely.
    """
    if t is not None and not math.isfinite(t):
        return None, "t must be a finite number"
    if not is_safe_colour(stroke):
        return None, "stroke must be a hex colour or CSS keyword"
    if not is_safe_colour(background):
        return None, "background must be a hex colour, keyword or none"
    return (
        HeartRequest(
            t=t,
            samples=int(clamp(samples, SAMPLES_MIN, SAMPLES_MAX)),
            scale=clamp(scale, SCALE_MIN, SCALE_MAX),
            stroke=stroke.strip(),
            background=background.strip(),
        ),
        "",
    )


def register_routes() -> None:
    """Serve the heart as SVG. Everything this route returns is SVG."""
    from nicegui import app
    from starlette.requests import Request
    from starlette.responses import Response

    @app.get("/api/heart.svg")
    def heart_svg(
        request: Request,
        t: float | None = None,
        samples: int = SAMPLES_DEFAULT,
        scale: float = SCALE_DEFAULT,
        stroke: str = HEART_RED,
        background: str = "none",
    ) -> Response:
        heart_request, reason = build_request(
            t=t, samples=samples, scale=scale, stroke=stroke, background=background
        )
        if heart_request is None:
            return Response(
                content=render_error(reason),
                media_type=SVG_MEDIA_TYPE,
                status_code=400,
            )

        etag = etag_for(heart_request)
        headers = {"ETag": etag, "Cache-Control": CACHE_CONTROL}
        if request.headers.get("if-none-match") == etag:
            return Response(status_code=304, headers=headers)
        return Response(
            content=render(heart_request),
            media_type=SVG_MEDIA_TYPE,
            headers=headers,
        )
