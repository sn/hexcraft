"""Display-P3 ↔ XYZ (D65) and ↔ linear sRGB.

P3 uses sRGB transfer functions and DCI-P3 primaries with D65 white.
"""

from __future__ import annotations

from .srgb import decode as _decode_gamma
from .srgb import encode as _encode_gamma

_M_P3_TO_XYZ: tuple[tuple[float, float, float], ...] = (
    (0.4865709486482162, 0.26566769316909306, 0.1982172852343625),
    (0.2289745640697488, 0.6917385218365064, 0.079286914093745),
    (0.0000000000000000, 0.04511338185890264, 1.043944368900976),
)
_M_XYZ_TO_P3: tuple[tuple[float, float, float], ...] = (
    (2.4934969119414255, -0.9313836179191236, -0.40271078445071684),
    (-0.8294889695615747, 1.7626640603183465, 0.023624685841943587),
    (0.03584583024378433, -0.07617238926804171, 0.9568845240076872),
)


def _mul(m: tuple[tuple[float, float, float], ...], v: tuple[float, float, float]) -> tuple[float, float, float]:
    a, b, c = v
    return (
        m[0][0] * a + m[0][1] * b + m[0][2] * c,
        m[1][0] * a + m[1][1] * b + m[1][2] * c,
        m[2][0] * a + m[2][1] * b + m[2][2] * c,
    )


def linear_p3_to_xyz(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert linear Display-P3 to CIE XYZ (D65 reference white)."""
    return _mul(_M_P3_TO_XYZ, rgb)


def xyz_to_linear_p3(xyz: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert CIE XYZ (D65) to linear Display-P3."""
    return _mul(_M_XYZ_TO_P3, xyz)


def p3_decode(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Gamma-encoded Display-P3 → linear Display-P3."""
    return (_decode_gamma(rgb[0]), _decode_gamma(rgb[1]), _decode_gamma(rgb[2]))


def p3_encode(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Linear Display-P3 → gamma-encoded Display-P3."""
    return (_encode_gamma(rgb[0]), _encode_gamma(rgb[1]), _encode_gamma(rgb[2]))
