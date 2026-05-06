"""High-level accessibility helpers built on contrast metrics."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from .contrast import wcag_ratio

if TYPE_CHECKING:
    from .color import Color

Direction = Literal["lighten", "darken", "auto"]


def find_accessible_pair(
    base: Color,
    against: Color,
    *,
    ratio: float = 4.5,
    direction: Direction = "auto",
) -> Color | None:
    """Return a color close to ``base`` that contrasts with ``against`` at ≥ ratio.

    Walks OKLCh lightness up or down from ``base`` until WCAG contrast against
    ``against`` meets or exceeds ``ratio``. Hue and chroma are preserved.
    Returns ``None`` if no in-gamut color along the lightness axis qualifies.

    direction:
      - ``"lighten"``: search only toward white
      - ``"darken"``: search only toward black
      - ``"auto"``: try both and return whichever needs the smaller lightness shift
    """
    from .color import Color
    from .gamut import map_to_gamut

    if wcag_ratio(base, against) >= ratio:
        return base

    L0, C, h = base.oklch
    a = base.alpha

    def _try(step: float) -> tuple[Color, float] | None:
        lo, hi = (L0, 1.0) if step > 0 else (0.0, L0)
        for _ in range(60):
            mid = (lo + hi) / 2.0
            cand = map_to_gamut(Color.from_oklch(mid, C, h, a))
            if wcag_ratio(cand, against) >= ratio:
                if step > 0:
                    hi = mid
                else:
                    lo = mid
            else:
                if step > 0:
                    lo = mid
                else:
                    hi = mid
        edge = hi if step > 0 else lo
        cand = map_to_gamut(Color.from_oklch(edge, C, h, a))
        if wcag_ratio(cand, against) >= ratio:
            return cand, abs(edge - L0)
        return None

    candidates = []
    if direction in ("lighten", "auto"):
        result = _try(+1.0)
        if result is not None:
            candidates.append(result)
    if direction in ("darken", "auto"):
        result = _try(-1.0)
        if result is not None:
            candidates.append(result)

    if not candidates:
        return None
    candidates.sort(key=lambda x: x[1])
    return candidates[0][0]


def best_text_color(bg: Color, *, palette: list[Color] | None = None) -> Color:
    """Pick the best foreground from ``palette`` (default: black/white) for ``bg``."""
    from .color import Color
    options = palette if palette is not None else [Color("#000000"), Color("#ffffff")]
    return max(options, key=lambda c: wcag_ratio(c, bg))
