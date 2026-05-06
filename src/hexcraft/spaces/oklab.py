"""OKLab and OKLCh (Björn Ottosson, 2020).

Operates from linear sRGB. OKLab L is roughly perceptual; values for sRGB
in-gamut colors fall in [0, 1]. h is in degrees [0, 360).
"""

from __future__ import annotations

import math

_M1: tuple[tuple[float, float, float], ...] = (
    (0.4122214708, 0.5363325363, 0.0514459929),
    (0.2119034982, 0.6806995451, 0.1073969566),
    (0.0883024619, 0.2817188376, 0.6299787005),
)
_M2: tuple[tuple[float, float, float], ...] = (
    (0.2104542553, 0.7936177850, -0.0040720468),
    (1.9779984951, -2.4285922050, 0.4505937099),
    (0.0259040371, 0.7827717662, -0.8086757660),
)

_M2_INV: tuple[tuple[float, float, float], ...] = (
    (1.0, 0.3963377774, 0.2158037573),
    (1.0, -0.1055613458, -0.0638541728),
    (1.0, -0.0894841775, -1.2914855480),
)
_M1_INV: tuple[tuple[float, float, float], ...] = (
    (4.0767416621, -3.3077115913, 0.2309699292),
    (-1.2684380046, 2.6097574011, -0.3413193965),
    (-0.0041960863, -0.7034186147, 1.7076147010),
)


def _mul(m: tuple[tuple[float, float, float], ...], v: tuple[float, float, float]) -> tuple[float, float, float]:
    a, b, c = v
    return (
        m[0][0] * a + m[0][1] * b + m[0][2] * c,
        m[1][0] * a + m[1][1] * b + m[1][2] * c,
        m[2][0] * a + m[2][1] * b + m[2][2] * c,
    )


def _cbrt(x: float) -> float:
    return math.copysign(abs(x) ** (1.0 / 3.0), x)


def linear_rgb_to_oklab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert linear sRGB to OKLab. L is roughly perceptual; in-gamut L in [0, 1]."""
    lms = _mul(_M1, rgb)
    lms_ = (_cbrt(lms[0]), _cbrt(lms[1]), _cbrt(lms[2]))
    return _mul(_M2, lms_)


def oklab_to_linear_rgb(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert OKLab to linear sRGB. May produce out-of-gamut values."""
    lms_ = _mul(_M2_INV, lab)
    lms = (lms_[0] ** 3, lms_[1] ** 3, lms_[2] ** 3)
    return _mul(_M1_INV, lms)


def oklab_to_oklch(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert OKLab to OKLCh (polar form). h is in degrees [0, 360)."""
    L, a, b = lab
    c = math.hypot(a, b)
    h = math.degrees(math.atan2(b, a))
    if h < 0.0:
        h += 360.0
    return (L, c, h)


def oklch_to_oklab(lch: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert OKLCh (polar form) to OKLab."""
    L, c, h = lch
    rad = math.radians(h)
    return (L, c * math.cos(rad), c * math.sin(rad))
