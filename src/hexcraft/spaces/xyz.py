"""CIE XYZ (D65) ↔ linear sRGB.

Matrices from IEC 61966-2-1 with sRGB primaries and D65 white point.
"""

from __future__ import annotations

D65_WHITE: tuple[float, float, float] = (0.9504559270516717, 1.0, 1.0890577507598784)

_M_RGB_TO_XYZ: tuple[tuple[float, float, float], ...] = (
    (0.4123907992659595, 0.3575843393838780, 0.1804807884018343),
    (0.2126390058715104, 0.7151686787677559, 0.0721923153607337),
    (0.0193308187155918, 0.1191947797946259, 0.9505321522496608),
)

_M_XYZ_TO_RGB: tuple[tuple[float, float, float], ...] = (
    (3.2409699419045226, -1.5373831775700939, -0.4986107602930034),
    (-0.9692436362808796, 1.8759675015077202, 0.0415550574071756),
    (0.0556300796969936, -0.2039769588889765, 1.0569715142428784),
)


def _mul(m: tuple[tuple[float, float, float], ...], v: tuple[float, float, float]) -> tuple[float, float, float]:
    a, b, c = v
    return (
        m[0][0] * a + m[0][1] * b + m[0][2] * c,
        m[1][0] * a + m[1][1] * b + m[1][2] * c,
        m[2][0] * a + m[2][1] * b + m[2][2] * c,
    )


def linear_rgb_to_xyz(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert linear sRGB to CIE XYZ (D65 reference white)."""
    return _mul(_M_RGB_TO_XYZ, rgb)


def xyz_to_linear_rgb(xyz: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert CIE XYZ (D65) to linear sRGB."""
    return _mul(_M_XYZ_TO_RGB, xyz)
