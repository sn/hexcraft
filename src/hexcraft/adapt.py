"""Chromatic adaptation: convert XYZ between white points.

Bradford and CAT16 cone-response transforms. Use when crossing illuminants
(e.g., D65 ↔ D50 for ICC profile work).
"""

from __future__ import annotations

from typing import Literal

WhitePoint = tuple[float, float, float]

D65: WhitePoint = (0.9504559270516717, 1.0, 1.0890577507598784)
D50: WhitePoint = (0.9642956764295677, 1.0, 0.8251046025104602)
D55: WhitePoint = (0.9568, 1.0, 0.9214)
D75: WhitePoint = (0.9495, 1.0, 1.2266)
A: WhitePoint = (1.0985, 1.0, 0.3558)


_BRADFORD: tuple[tuple[float, float, float], ...] = (
    (0.8951000, 0.2664000, -0.1614000),
    (-0.7502000, 1.7135000, 0.0367000),
    (0.0389000, -0.0685000, 1.0296000),
)
_BRADFORD_INV: tuple[tuple[float, float, float], ...] = (
    (0.9869929, -0.1470543, 0.1599627),
    (0.4323053, 0.5183603, 0.0492912),
    (-0.0085287, 0.0400428, 0.9684867),
)

_CAT16: tuple[tuple[float, float, float], ...] = (
    (0.401288, 0.650173, -0.051461),
    (-0.250268, 1.204414, 0.045854),
    (-0.002079, 0.048952, 0.953127),
)
_CAT16_INV: tuple[tuple[float, float, float], ...] = (
    (1.86206786, -1.01125463, 0.14918677),
    (0.38752654, 0.62144744, -0.00897398),
    (-0.01584150, -0.03412294, 1.04996444),
)


def _mul(m: tuple[tuple[float, float, float], ...], v: tuple[float, float, float]) -> tuple[float, float, float]:
    a, b, c = v
    return (
        m[0][0] * a + m[0][1] * b + m[0][2] * c,
        m[1][0] * a + m[1][1] * b + m[1][2] * c,
        m[2][0] * a + m[2][1] * b + m[2][2] * c,
    )


def adapt(
    xyz: tuple[float, float, float],
    src: WhitePoint,
    dst: WhitePoint,
    *,
    method: Literal["bradford", "cat16", "xyz"] = "bradford",
) -> tuple[float, float, float]:
    """Adapt XYZ from ``src`` white point to ``dst``.

    ``method`` selects the cone-response space:
      - ``"bradford"`` (default, widely used in ICC v4 profiles)
      - ``"cat16"`` (used by CIECAM16)
      - ``"xyz"`` (a.k.a. von Kries with XYZ scaling — simplest, least accurate)
    """
    if method == "xyz":
        sx = dst[0] / src[0]
        sy = dst[1] / src[1]
        sz = dst[2] / src[2]
        return (xyz[0] * sx, xyz[1] * sy, xyz[2] * sz)
    if method == "bradford":
        m, m_inv = _BRADFORD, _BRADFORD_INV
    elif method == "cat16":
        m, m_inv = _CAT16, _CAT16_INV
    else:
        raise ValueError(f"unknown adaptation method: {method!r}")
    src_lms = _mul(m, src)
    dst_lms = _mul(m, dst)
    sx = dst_lms[0] / src_lms[0]
    sy = dst_lms[1] / src_lms[1]
    sz = dst_lms[2] / src_lms[2]
    lms = _mul(m, xyz)
    scaled = (lms[0] * sx, lms[1] * sy, lms[2] * sz)
    return _mul(m_inv, scaled)
