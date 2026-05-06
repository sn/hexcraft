"""sRGB transfer functions: gamma-encoded sRGB ↔ linear sRGB.

IEC 61966-2-1:1999. Operates on scalars in [0, 1] (values outside this range
are passed through to support wide-gamut/HDR pipelines).
"""

from __future__ import annotations


def encode(c: float) -> float:
    """Apply the sRGB transfer function: linear → gamma-encoded sRGB."""
    if c < 0.0:
        return -encode(-c)
    if c <= 0.0031308:
        return 12.92 * c
    return 1.055 * (c ** (1.0 / 2.4)) - 0.055


def decode(c: float) -> float:
    """Reverse the sRGB transfer function: gamma-encoded sRGB → linear."""
    if c < 0.0:
        return -decode(-c)
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def encode_rgb(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Encode all three components from linear sRGB to gamma sRGB."""
    r, g, b = rgb
    return encode(r), encode(g), encode(b)


def decode_rgb(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Decode all three components from gamma sRGB to linear sRGB."""
    r, g, b = rgb
    return decode(r), decode(g), decode(b)
