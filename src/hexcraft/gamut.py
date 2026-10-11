"""Gamut mapping.

Bisect chroma in OKLCh, keeping lightness and hue, until the color fits the
target gamut, then clip away any residual error. This is a simplified form of
the CSS Color 4 algorithm: it omits the "clip if within a JND" shortcut, so it
can return slightly less chroma than a browser would.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .color import Color


_EPSILON = 0.0001


def _in_srgb_gamut(c: Color, tol: float = _EPSILON) -> bool:
    return all(-tol <= x <= 1.0 + tol for x in c.linear_rgb)


def map_to_gamut(c: Color, *, space: Literal["srgb"] = "srgb") -> Color:
    """Reduce OKLCh chroma until ``c`` is in ``space``'s gamut, preserving L and h."""
    from .color import Color as _C

    if space != "srgb":
        raise NotImplementedError(f"gamut mapping for {space} not implemented")

    if _in_srgb_gamut(c):
        return c

    L, _, h = c.oklch
    if L >= 1.0:
        return _C("#ffffff").with_alpha(c.alpha)
    if L <= 0.0:
        return _C("#000000").with_alpha(c.alpha)

    L0, C0, _ = c.oklch
    lo = 0.0
    hi = C0
    candidate = _C.from_oklch(L0, hi, h, c.alpha)
    while hi - lo > _EPSILON:
        mid = (lo + hi) / 2.0
        candidate = _C.from_oklch(L0, mid, h, c.alpha)
        if _in_srgb_gamut(candidate):
            lo = mid
        else:
            hi = mid

    candidate = _C.from_oklch(L0, lo, h, c.alpha)
    r, g, b = candidate.linear_rgb
    r = max(0.0, min(1.0, r))
    g = max(0.0, min(1.0, g))
    b = max(0.0, min(1.0, b))
    return _C.from_linear_rgb(r, g, b, c.alpha)


def clip(c: Color) -> Color:
    """Component-wise clip linear sRGB to [0, 1]."""
    from .color import Color as _C
    r, g, b = c.linear_rgb
    return _C.from_linear_rgb(
        max(0.0, min(1.0, r)),
        max(0.0, min(1.0, g)),
        max(0.0, min(1.0, b)),
        c.alpha,
    )
