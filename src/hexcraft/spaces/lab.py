"""CIE Lab (D65) and CIE LCh.

Standard CIE 1976 L*a*b* transformation. h is in degrees [0, 360).
"""

from __future__ import annotations

import math

from .xyz import D65_WHITE

_DELTA = 6.0 / 29.0
_DELTA3 = _DELTA**3
_THREE_DELTA2 = 3.0 * _DELTA**2


def _f(t: float) -> float:
    if t > _DELTA3:
        return t ** (1.0 / 3.0)
    return t / _THREE_DELTA2 + 4.0 / 29.0


def _f_inv(t: float) -> float:
    if t > _DELTA:
        return t**3
    return _THREE_DELTA2 * (t - 4.0 / 29.0)


def xyz_to_lab(xyz: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert CIE XYZ (D65) to CIE L*a*b*. L in [0, 100]."""
    x, y, z = xyz
    xn, yn, zn = D65_WHITE
    fx, fy, fz = _f(x / xn), _f(y / yn), _f(z / zn)
    return (116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz))


def lab_to_xyz(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert CIE L*a*b* to CIE XYZ (D65 reference white)."""
    L, a, b = lab
    xn, yn, zn = D65_WHITE
    fy = (L + 16.0) / 116.0
    fx = fy + a / 500.0
    fz = fy - b / 200.0
    return (xn * _f_inv(fx), yn * _f_inv(fy), zn * _f_inv(fz))


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
