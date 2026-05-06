"""Render Color values to CSS strings."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .color import Color


def _fmt(n: float, places: int = 4) -> str:
    s = f"{n:.{places}f}".rstrip("0").rstrip(".")
    return s or "0"


def format_css(c: Color, fmt: Literal["hex", "rgb", "hsl", "hwb", "lab", "lch", "oklab", "oklch"] = "hex") -> str:
    """Render ``c`` as a CSS string in the requested format.

    ``fmt`` selects the syntax: ``hex`` (default), ``rgb``, ``hsl``, ``hwb``,
    ``lab``, ``lch``, ``oklab``, or ``oklch``. Alpha is included only when
    less than 1.0.
    """
    a = c.alpha
    if fmt == "hex":
        return c.hex
    if fmt == "rgb":
        r, g, b = c.rgb
        if a >= 1.0:
            return f"rgb({r}, {g}, {b})"
        return f"rgba({r}, {g}, {b}, {_fmt(a)})"
    if fmt == "hsl":
        h, s, L = c.hsl
        body = f"{_fmt(h, 2)} {_fmt(s * 100, 2)}% {_fmt(L * 100, 2)}%"
        return f"hsl({body} / {_fmt(a)})" if a < 1.0 else f"hsl({body})"
    if fmt == "hwb":
        h, w, bl = c.hwb
        body = f"{_fmt(h, 2)} {_fmt(w * 100, 2)}% {_fmt(bl * 100, 2)}%"
        return f"hwb({body} / {_fmt(a)})" if a < 1.0 else f"hwb({body})"
    if fmt == "lab":
        L, A, B = c.lab
        body = f"{_fmt(L)}% {_fmt(A)} {_fmt(B)}"
        return f"lab({body} / {_fmt(a)})" if a < 1.0 else f"lab({body})"
    if fmt == "lch":
        L, C, H = c.lch
        body = f"{_fmt(L)}% {_fmt(C)} {_fmt(H)}"
        return f"lch({body} / {_fmt(a)})" if a < 1.0 else f"lch({body})"
    if fmt == "oklab":
        L, A, B = c.oklab
        body = f"{_fmt(L)} {_fmt(A)} {_fmt(B)}"
        return f"oklab({body} / {_fmt(a)})" if a < 1.0 else f"oklab({body})"
    if fmt == "oklch":
        L, C, H = c.oklch
        body = f"{_fmt(L)} {_fmt(C)} {_fmt(H)}"
        return f"oklch({body} / {_fmt(a)})" if a < 1.0 else f"oklch({body})"
    raise ValueError(f"unknown format: {fmt}")
