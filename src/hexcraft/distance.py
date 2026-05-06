"""Color difference (deltaE).

- ``76``: CIE76 - Euclidean in Lab. Fast, only roughly perceptual.
- ``94``: CIE94 - graphics-arts variant, weights chroma/hue separately.
- ``2000``: CIEDE2000 - current CIE recommendation.
- ``cmc``: CMC(l:c) - textile-industry standard, default l=2, c=1 (acceptability).
- ``ok``: Euclidean in OKLab - fast and well-behaved across the visible gamut.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from .color import Color


def closest_from(
    target: Color,
    palette: list[Color],
    *,
    method: Literal["76", "94", "2000", "cmc", "ok"] = "2000",
) -> Color:
    """Return the palette entry with smallest ΔE from ``target``.

    Use ``method="ok"`` for fast image-scale matching, ``"2000"`` for highest
    perceptual accuracy. Raises ``ValueError`` on empty palette.
    """
    if not palette:
        raise ValueError("palette must contain at least one color")
    return min(palette, key=lambda c: delta_e(target, c, method=method))


def closest_n_from(
    target: Color,
    palette: list[Color],
    *,
    n: int = 5,
    method: Literal["76", "94", "2000", "cmc", "ok"] = "2000",
) -> list[Color]:
    """Return the ``n`` palette entries closest to ``target`` by ΔE."""
    return sorted(palette, key=lambda c: delta_e(target, c, method=method))[:n]


def delta_e(a: Color, b: Color, *, method: Literal["76", "94", "2000", "cmc", "ok"] = "2000") -> float:
    """Color difference between ``a`` and ``b``.

    ``method``:
      - ``"76"``   CIE76 - Euclidean distance in Lab. Fast, only roughly perceptual.
      - ``"94"``   CIE94 - graphic-arts variant weighting chroma and hue.
      - ``"2000"`` CIEDE2000 - current CIE recommendation (default).
      - ``"cmc"``  CMC(l:c) at l=2 c=1 (textile acceptability).
      - ``"ok"``   Euclidean distance in OKLab - fast modern alternative.

    Rough thresholds for CIEDE2000: <1 imperceptible, 1–2 perceptible to a
    trained eye, >5 clearly different.
    """
    if method == "76":
        return _de76(a, b)
    if method == "94":
        return _de94(a, b)
    if method == "2000":
        return _de2000(a, b)
    if method == "cmc":
        return _de_cmc(a, b)
    if method == "ok":
        return _de_ok(a, b)
    raise ValueError(f"unknown method: {method!r}")


def _de76(a: Color, b: Color) -> float:
    L1, a1, b1 = a.lab
    L2, a2, b2 = b.lab
    return math.sqrt((L1 - L2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)


def _de_ok(a: Color, b: Color) -> float:
    L1, a1, b1 = a.oklab
    L2, a2, b2 = b.oklab
    return math.sqrt((L1 - L2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2)


def _de94(a: Color, b: Color, *, kL: float = 1.0, K1: float = 0.045, K2: float = 0.015) -> float:
    """CIE94 (graphic-arts weighting)."""
    L1, a1, b1 = a.lab
    L2, a2, b2 = b.lab
    dL = L1 - L2
    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    dC = C1 - C2
    da = a1 - a2
    db = b1 - b2
    dH2 = max(0.0, da * da + db * db - dC * dC)
    Sl = 1.0
    Sc = 1.0 + K1 * C1
    Sh = 1.0 + K2 * C1
    return math.sqrt((dL / (kL * Sl)) ** 2 + (dC / Sc) ** 2 + dH2 / (Sh ** 2))


def _de_cmc(a: Color, b: Color, *, l: float = 2.0, c_factor: float = 1.0) -> float:
    """CMC(l:c). Defaults l=2 c=1 (acceptability); use l=1 c=1 for perceptibility."""
    L1, a1, b1 = a.lab
    L2, a2, b2 = b.lab
    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    dL = L1 - L2
    dC = C1 - C2
    da = a1 - a2
    db = b1 - b2
    dH2 = max(0.0, da * da + db * db - dC * dC)

    Sl = 0.511 if L1 < 16.0 else (0.040975 * L1) / (1.0 + 0.01765 * L1)
    Sc = (0.0638 * C1) / (1.0 + 0.0131 * C1) + 0.638

    h1 = math.degrees(math.atan2(b1, a1)) % 360.0
    if 164.0 <= h1 <= 345.0:
        T = 0.56 + abs(0.2 * math.cos(math.radians(h1 + 168.0)))
    else:
        T = 0.36 + abs(0.4 * math.cos(math.radians(h1 + 35.0)))
    F = math.sqrt((C1**4) / (C1**4 + 1900.0))
    Sh = Sc * (F * T + 1.0 - F)

    return math.sqrt((dL / (l * Sl)) ** 2 + (dC / (c_factor * Sc)) ** 2 + dH2 / (Sh ** 2))


def _de2000(a: Color, b: Color, *, kL: float = 1.0, kC: float = 1.0, kH: float = 1.0) -> float:
    L1, a1, b1 = a.lab
    L2, a2, b2 = b.lab

    C1 = math.hypot(a1, b1)
    C2 = math.hypot(a2, b2)
    Cb = (C1 + C2) / 2.0

    G = 0.5 * (1.0 - math.sqrt((Cb**7) / (Cb**7 + 25.0**7)))
    a1p = (1.0 + G) * a1
    a2p = (1.0 + G) * a2

    C1p = math.hypot(a1p, b1)
    C2p = math.hypot(a2p, b2)

    h1p = math.degrees(math.atan2(b1, a1p)) % 360.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360.0

    dLp = L2 - L1
    dCp = C2p - C1p

    if C1p * C2p == 0.0:
        dhp = 0.0
    else:
        diff = h2p - h1p
        if diff > 180.0:
            diff -= 360.0
        elif diff < -180.0:
            diff += 360.0
        dhp = diff
    dHp = 2.0 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp) / 2.0)

    Lbp = (L1 + L2) / 2.0
    Cbp = (C1p + C2p) / 2.0

    if C1p * C2p == 0.0:
        hbp = h1p + h2p
    else:
        diff_abs = abs(h1p - h2p)
        if diff_abs <= 180.0:
            hbp = (h1p + h2p) / 2.0
        elif (h1p + h2p) < 360.0:
            hbp = (h1p + h2p + 360.0) / 2.0
        else:
            hbp = (h1p + h2p - 360.0) / 2.0

    T = (
        1.0
        - 0.17 * math.cos(math.radians(hbp - 30.0))
        + 0.24 * math.cos(math.radians(2.0 * hbp))
        + 0.32 * math.cos(math.radians(3.0 * hbp + 6.0))
        - 0.20 * math.cos(math.radians(4.0 * hbp - 63.0))
    )

    dTheta = 30.0 * math.exp(-(((hbp - 275.0) / 25.0) ** 2))
    Rc = 2.0 * math.sqrt((Cbp**7) / (Cbp**7 + 25.0**7))
    Sl = 1.0 + (0.015 * (Lbp - 50.0) ** 2) / math.sqrt(20.0 + (Lbp - 50.0) ** 2)
    Sc = 1.0 + 0.045 * Cbp
    Sh = 1.0 + 0.015 * Cbp * T
    Rt = -math.sin(math.radians(2.0 * dTheta)) * Rc

    return math.sqrt(
        (dLp / (kL * Sl)) ** 2
        + (dCp / (kC * Sc)) ** 2
        + (dHp / (kH * Sh)) ** 2
        + Rt * (dCp / (kC * Sc)) * (dHp / (kH * Sh))
    )
