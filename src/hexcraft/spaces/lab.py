"""CIE Lab and CIE LCh.

Standard CIE 1976 L*a*b* transformation. h is in degrees [0, 360). The Python
API uses a D65 reference white; CSS ``lab()``/``lch()`` are D50-relative, so the
``css_*`` helpers adapt XYZ with Bradford between the two white points.
"""

from __future__ import annotations

import math

from ..adapt import D50, adapt
from .xyz import D65_WHITE

_DELTA = 6.0 / 29.0
_DELTA3 = _DELTA**3
_THREE_DELTA2 = 3.0 * _DELTA**2


def _f(t: float) -> float:
    if t > _DELTA3:
        return float(t ** (1.0 / 3.0))
    return t / _THREE_DELTA2 + 4.0 / 29.0


def _f_inv(t: float) -> float:
    if t > _DELTA:
        return t**3
    return _THREE_DELTA2 * (t - 4.0 / 29.0)


def xyz_to_lab(
    xyz: tuple[float, float, float], white: tuple[float, float, float] = D65_WHITE
) -> tuple[float, float, float]:
    """Convert CIE XYZ to CIE L*a*b* relative to ``white`` (default D65). L in [0, 100]."""
    x, y, z = xyz
    xn, yn, zn = white
    fx, fy, fz = _f(x / xn), _f(y / yn), _f(z / zn)
    return (116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz))


def lab_to_xyz(
    lab: tuple[float, float, float], white: tuple[float, float, float] = D65_WHITE
) -> tuple[float, float, float]:
    """Convert CIE L*a*b* to CIE XYZ relative to ``white`` (default D65)."""
    L, a, b = lab
    xn, yn, zn = white
    fy = (L + 16.0) / 116.0
    fx = fy + a / 500.0
    fz = fy - b / 200.0
    return (xn * _f_inv(fx), yn * _f_inv(fy), zn * _f_inv(fz))


def xyz_to_css_lab(xyz: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert CIE XYZ (D65) to CSS ``lab()`` components (D50-relative L*a*b*)."""
    return xyz_to_lab(adapt(xyz, D65_WHITE, D50), white=D50)


def css_lab_to_xyz(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert CSS ``lab()`` components (D50-relative L*a*b*) to CIE XYZ (D65)."""
    return adapt(lab_to_xyz(lab, white=D50), D50, D65_WHITE)


def lab_to_lch(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert L*a*b* to L*C*h* (polar form). h is in degrees [0, 360)."""
    L, a, b = lab
    c = math.hypot(a, b)
    h = math.degrees(math.atan2(b, a))
    if h < 0.0:
        h += 360.0
    return (L, c, h)


def lch_to_lab(lch: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert L*C*h* (polar form) to L*a*b*."""
    L, c, h = lch
    rad = math.radians(h)
    return (L, c * math.cos(rad), c * math.sin(rad))
