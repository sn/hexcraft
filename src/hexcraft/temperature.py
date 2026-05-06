"""Color temperature: Kelvin (CCT) ↔ Color.

Forward direction uses Tanner Helland's piecewise approximation, accurate to a
few percent in [1000, 40000] K - fine for visualization, dimming, and warm/
cool simulation. Use ICC-aware tools for color-critical photography.

Inverse direction (color → CCT) uses McCamy's cubic approximation in CIE xy
chromaticity. Valid roughly 2000–25000 K. Returns ``None`` for chromaticities
outside the Planckian-locus envelope where CCT is undefined.
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


def rgb_to_kelvin(c: Color) -> float | None:
    """Approximate CCT (K) from a color via McCamy's formula. ``None`` if undefined."""
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
    if cct < 1000.0 or cct > 40000.0:
        return None
    return cct
