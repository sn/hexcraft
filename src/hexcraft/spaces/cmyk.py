"""Naive sRGB ↔ CMYK conversion.

CMYK is fundamentally device-dependent: the same C/M/Y/K percentages produce
different inks on different presses, papers, and substrates. Real print
workflows go through ICC profiles (e.g. SWOP, FOGRA, GRACoL). This module
implements the algebraic device-independent CMYK that web tools commonly use,
which is fine for *display* preview but should not be trusted as the value
sent to a printing press.
"""

from __future__ import annotations


def srgb_to_cmyk(rgb: tuple[float, float, float]) -> tuple[float, float, float, float]:
    """Naive CMYK from gamma-encoded sRGB. All values in [0, 1]."""
    r, g, b = rgb
    k = 1.0 - max(r, g, b)
    if k >= 1.0 - 1e-9:
        return (0.0, 0.0, 0.0, 1.0)
    denom = 1.0 - k
    c = (1.0 - r - k) / denom
    m = (1.0 - g - k) / denom
    y = (1.0 - b - k) / denom
    return (c, m, y, k)


def cmyk_to_srgb(cmyk: tuple[float, float, float, float]) -> tuple[float, float, float]:
    """Naive CMYK → gamma-encoded sRGB. Inverse of ``srgb_to_cmyk``."""
    c, m, y, k = cmyk
    r = (1.0 - c) * (1.0 - k)
    g = (1.0 - m) * (1.0 - k)
    b = (1.0 - y) * (1.0 - k)
    return (r, g, b)
