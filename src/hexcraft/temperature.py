"""Color temperature: Kelvin (CCT) ↔ Color.

Forward direction uses Tanner Helland's piecewise approximation, accurate to a
few percent in [1000, 40000] K - fine for visualization, dimming, and warm/
cool simulation. Use ICC-aware tools for color-critical photography.

Inverse direction (color → CCT) uses McCamy's cubic approximation in CIE xy
chromaticity, most accurate roughly 2000–25000 K. CCT is only meaningful near
the blackbody (Planckian) locus, so ``None`` is returned when the color's
distance from it (Duv, in CIE 1960 uv) exceeds 0.05, or when the estimate
falls outside 1000–25000 K.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .color import Color


def kelvin_to_rgb(temperature: float) -> tuple[float, float, float]:
    """Approximate sRGB (gamma-encoded, 0..1) for a blackbody at ``temperature`` K."""
    t = max(1000.0, min(40000.0, temperature)) / 100.0

    r = 255.0 if t <= 66.0 else 329.698727446 * ((t - 60.0) ** -0.1332047592)
    if t <= 66.0:
        g = 99.4708025861 * math.log(t) - 161.1195681661
    else:
        g = 288.1221695283 * ((t - 60.0) ** -0.0755148492)
    if t >= 66.0:
        b = 255.0
    elif t <= 19.0:
        b = 0.0
    else:
        b = 138.5177312231 * math.log(t - 10.0) - 305.0447927307

    return (
        max(0.0, min(255.0, r)) / 255.0,
        max(0.0, min(255.0, g)) / 255.0,
        max(0.0, min(255.0, b)) / 255.0,
    )


# CCT is conventionally undefined beyond this distance from the Planckian locus.
_MAX_DUV = 0.05


def _planckian_xy(t: float) -> tuple[float, float]:
    """CIE 1931 xy of a blackbody at ``t`` K (Kim et al. 2002 cubic spline, 1667–25000 K)."""
    t = max(1667.0, min(25000.0, t))
    if t <= 4000.0:
        x = -0.2661239e9 / t**3 - 0.2343589e6 / t**2 + 0.8776956e3 / t + 0.179910
    else:
        x = -3.0258469e9 / t**3 + 2.1070379e6 / t**2 + 0.2226347e3 / t + 0.240390
    if t <= 2222.0:
        y = -1.1063814 * x**3 - 1.34811020 * x**2 + 2.18555832 * x - 0.20219683
    elif t <= 4000.0:
        y = -0.9549476 * x**3 - 1.37418593 * x**2 + 2.09137015 * x - 0.16748867
    else:
        y = 3.0817580 * x**3 - 5.87338670 * x**2 + 3.75112997 * x - 0.37001483
    return x, y


def _uv(x: float, y: float) -> tuple[float, float]:
    """CIE 1931 xy → CIE 1960 uv."""
    d = -2.0 * x + 12.0 * y + 3.0
    return 4.0 * x / d, 6.0 * y / d


def rgb_to_kelvin(c: Color) -> float | None:
    """Approximate CCT (K) from a color via McCamy's formula.

    Returns ``None`` when CCT is undefined: black, colors farther than Duv 0.05
    from the blackbody locus (saturated colors), or estimates outside 1000–25000 K.
    """
    X, Y, Z = c.xyz
    s = X + Y + Z
    if s <= 0.0:
        return None
    x = X / s
    y = Y / s
    denom = y - 0.1858
    if abs(denom) < 1e-9:
        return None
    n = (x - 0.3320) / denom
    cct = -449.0 * n**3 + 3525.0 * n**2 - 6823.3 * n + 5520.33
    if cct < 1000.0 or cct > 25000.0:
        return None
    u, v = _uv(x, y)
    lu, lv = _uv(*_planckian_xy(cct))
    if math.hypot(u - lu, v - lv) > _MAX_DUV:
        return None
    return cct
