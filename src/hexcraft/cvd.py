"""Color vision deficiency simulation and daltonization.

Simulation uses the Machado/Oliveira/Fernandes (2009) physiologically-based
matrices applied in linear sRGB. Daltonization uses the Fidaner/Lin/Ozguven
error-redistribution scheme.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .color import Color

CVDType = Literal["protanopia", "deuteranopia", "tritanopia"]


_MATRICES_FULL: dict[str, tuple[tuple[float, float, float], ...]] = {
    "protanopia": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deuteranopia": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    "tritanopia": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}

_DALTONIZE_SHIFT: dict[str, tuple[tuple[float, float, float], ...]] = {
    "protanopia": ((0.0, 0.0, 0.0), (0.7, 1.0, 0.0), (0.7, 0.0, 1.0)),
    "deuteranopia": ((0.0, 0.0, 0.0), (0.7, 1.0, 0.0), (0.7, 0.0, 1.0)),
    "tritanopia": ((1.0, 0.0, 0.7), (0.0, 1.0, 0.7), (0.0, 0.0, 0.0)),
}


def _mul(m: tuple[tuple[float, float, float], ...], v: tuple[float, float, float]) -> tuple[float, float, float]:
    a, b, c = v
    return (
        m[0][0] * a + m[0][1] * b + m[0][2] * c,
        m[1][0] * a + m[1][1] * b + m[1][2] * c,
        m[2][0] * a + m[2][1] * b + m[2][2] * c,
    )


def _interp_identity(m: tuple[tuple[float, float, float], ...], severity: float) -> tuple[tuple[float, float, float], ...]:
    """Lerp between identity matrix (0.0) and full-CVD matrix (1.0)."""
    s = max(0.0, min(1.0, severity))
    return tuple(
        tuple(
            (1.0 - s) * (1.0 if i == j else 0.0) + s * m[i][j]
            for j in range(3)
        )
        for i in range(3)
    )  # type: ignore[return-value]


def simulate(c: Color, kind: CVDType, severity: float = 1.0) -> Color:
    """Simulate how ``c`` appears to a viewer with ``kind`` CVD.

    ``severity`` ∈ [0, 1] interpolates from normal vision to full dichromacy.
    """
    from .color import Color
    if kind not in _MATRICES_FULL:
        raise ValueError(f"unknown CVD type: {kind!r}")
    m = _interp_identity(_MATRICES_FULL[kind], severity)
    r, g, b = _mul(m, c.linear_rgb)
    return Color.from_linear_rgb(r, g, b, c.alpha)


def daltonize(c: Color, kind: CVDType) -> Color:
    """Adjust ``c`` so a CVD viewer can distinguish what they would otherwise miss.

    Computes the error between the original and its CVD-simulated appearance,
    then redistributes that error onto channels the viewer can still perceive.
    """
    from .color import Color
    if kind not in _DALTONIZE_SHIFT:
        raise ValueError(f"unknown CVD type: {kind!r}")
    sim = simulate(c, kind, severity=1.0)
    er = c._lr - sim._lr
    eg = c._lg - sim._lg
    eb = c._lb - sim._lb
    sr, sg, sb = _mul(_DALTONIZE_SHIFT[kind], (er, eg, eb))
    return Color.from_linear_rgb(c._lr + sr, c._lg + sg, c._lb + sb, c.alpha)
