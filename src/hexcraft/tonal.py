"""Tonal palette generation: Material You and Tailwind-style scales.

Both build on OKLCh: hold the source's hue (and chroma, gamut-permitting)
constant while stepping perceptual lightness. This is the same approach
Material's HCT system and modern design systems use.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .color import Color

MATERIAL_TONES: tuple[int, ...] = (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100)

TAILWIND_STOPS: tuple[int, ...] = (50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950)
_TAILWIND_LIGHTNESS: tuple[float, ...] = (
    0.97,  # 50
    0.93,  # 100
    0.85,  # 200
    0.74,  # 300
    0.62,  # 400
    0.50,  # 500
    0.42,  # 600
    0.34,  # 700
    0.27,  # 800
    0.20,  # 900
    0.14,  # 950
)
_TAILWIND_CHROMA_FALLOFF: tuple[float, ...] = (
    0.30, 0.45, 0.65, 0.85, 0.95, 1.00, 0.95, 0.85, 0.70, 0.55, 0.45,
)


def _gamut_clip_oklch(L: float, C: float, h: float, alpha: float) -> Color:
    """Build a Color at given OKLCh coordinates, mapped into sRGB gamut."""
    from .color import Color as _C
    from .gamut import map_to_gamut
    if L <= 0.0:
        return _C.from_linear_rgb(0.0, 0.0, 0.0, alpha)
    if L >= 1.0:
        return _C.from_linear_rgb(1.0, 1.0, 1.0, alpha)
    raw = _C.from_oklch(L, C, h, alpha)
    return map_to_gamut(raw)


def material_tonal_palette(c: Color) -> dict[int, Color]:
    """Material You-style tonal palette from a source color.

    Returns 13 colors keyed by tone (0–100). Hue is preserved; chroma is taken
    from the source and clamped per-tone to remain in sRGB gamut.
    """
    _, C, h = c.oklch
    return {tone: _gamut_clip_oklch(tone / 100.0, C, h, c.alpha) for tone in MATERIAL_TONES}


def tailwind_scale(c: Color) -> dict[int, Color]:
    """Tailwind-style 50–950 scale from a source color.

    Returns 11 colors keyed by Tailwind stop. The 500 step targets the source's
    chroma; flanking steps reduce chroma toward the extremes for legibility.
    """
    _, C, h = c.oklch
    return {
        stop: _gamut_clip_oklch(L, C * mul, h, c.alpha)
        for stop, L, mul in zip(TAILWIND_STOPS, _TAILWIND_LIGHTNESS, _TAILWIND_CHROMA_FALLOFF, strict=True)
    }
