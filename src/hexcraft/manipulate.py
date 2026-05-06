"""Color manipulation: mixing, blending, interpolation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .color import Color


_HUE_SPACES = {"hsl", "hsv", "hwb", "lch", "oklch"}


def _shortest_hue(h1: float, h2: float, t: float) -> float:
    diff = ((h2 - h1 + 540.0) % 360.0) - 180.0
    return (h1 + diff * t) % 360.0


def mix(a: Color, b: Color, t: float = 0.5,
        *, space: Literal["srgb", "linear-rgb", "hsl", "hsv", "hwb", "lab", "lch", "oklab", "oklch"] = "oklab") -> Color:
    """Mix two colors. ``t`` is the weight of ``b`` (0 → a, 1 → b)."""
    from .color import Color
    t = max(0.0, min(1.0, t))
    if t == 0.0:
        return a
    if t == 1.0:
        return b
    if space == "linear-rgb":
        ar, ag, ab = a.linear_rgb
        br, bg, bb = b.linear_rgb
        return Color.from_linear_rgb(_lerp(ar, br, t), _lerp(ag, bg, t), _lerp(ab, bb, t), _lerp(a.alpha, b.alpha, t))
    if space == "srgb":
        ar, ag, ab = a.srgb
        br, bg, bb = b.srgb
        return Color.from_rgb(_lerp(ar, br, t), _lerp(ag, bg, t), _lerp(ab, bb, t), _lerp(a.alpha, b.alpha, t))
    if space == "oklab":
        a1, a2, a3 = a.oklab
        b1, b2, b3 = b.oklab
        return Color.from_oklab(_lerp(a1, b1, t), _lerp(a2, b2, t), _lerp(a3, b3, t), _lerp(a.alpha, b.alpha, t))
    if space == "oklch":
        L1, c1, h1 = a.oklch
        L2, c2, h2 = b.oklch
        return Color.from_oklch(_lerp(L1, L2, t), _lerp(c1, c2, t), _shortest_hue(h1, h2, t), _lerp(a.alpha, b.alpha, t))
    if space == "lab":
        L1, a1, b1 = a.lab
        L2, a2, b2 = b.lab
        return Color.from_lab(_lerp(L1, L2, t), _lerp(a1, a2, t), _lerp(b1, b2, t), _lerp(a.alpha, b.alpha, t))
    if space == "lch":
        L1, c1, h1 = a.lch
        L2, c2, h2 = b.lch
        return Color.from_lch(_lerp(L1, L2, t), _lerp(c1, c2, t), _shortest_hue(h1, h2, t), _lerp(a.alpha, b.alpha, t))
    if space == "hsl":
        h1, s1, L1 = a.hsl
        h2, s2, L2 = b.hsl
        return Color.from_hsl(_shortest_hue(h1, h2, t), _lerp(s1, s2, t), _lerp(L1, L2, t), _lerp(a.alpha, b.alpha, t))
    if space == "hsv":
        h1, s1, v1 = a.hsv
        h2, s2, v2 = b.hsv
        return Color.from_hsv(_shortest_hue(h1, h2, t), _lerp(s1, s2, t), _lerp(v1, v2, t), _lerp(a.alpha, b.alpha, t))
    if space == "hwb":
        h1, w1, b1 = a.hwb
        h2, w2, b2 = b.hwb
        return Color.from_hwb(_shortest_hue(h1, h2, t), _lerp(w1, w2, t), _lerp(b1, b2, t), _lerp(a.alpha, b.alpha, t))
    raise ValueError(f"unknown mixing space: {space}")


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def blend(bg: Color, fg: Color) -> Color:
    """Alpha composite ``fg`` over ``bg`` in linear sRGB (Porter-Duff over)."""
    from .color import Color
    af, ab = fg.alpha, bg.alpha
    out_a = af + ab * (1.0 - af)
    if out_a == 0.0:
        return Color.from_linear_rgb(0.0, 0.0, 0.0, 0.0)
    fr, fg_, fb = fg.linear_rgb
    br, bg_, bb = bg.linear_rgb
    out_r = (fr * af + br * ab * (1.0 - af)) / out_a
    out_g = (fg_ * af + bg_ * ab * (1.0 - af)) / out_a
    out_b = (fb * af + bb * ab * (1.0 - af)) / out_a
    return Color.from_linear_rgb(out_r, out_g, out_b, out_a)
