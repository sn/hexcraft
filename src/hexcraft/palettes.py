"""Palette generation: harmonies and scales."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from .manipulate import mix as _mix

if TYPE_CHECKING:
    from .color import Color


def complementary(c: Color) -> list[Color]:
    """Return ``[c, c rotated 180°]`` — the color and its complement."""
    return [c, c.rotate(180.0)]


def analogous(c: Color, *, count: int = 3, spread: float = 30.0) -> list[Color]:
    """``count`` colors centered on ``c``, spaced by ``spread`` degrees of hue."""
    if count < 1:
        return []
    half = (count - 1) / 2.0
    return [c.rotate((i - half) * spread) for i in range(count)]


def triadic(c: Color) -> list[Color]:
    """Three colors evenly spaced 120° apart in hue."""
    return [c, c.rotate(120.0), c.rotate(240.0)]


def tetradic(c: Color) -> list[Color]:
    """Four colors evenly spaced 90° apart in hue."""
    return [c, c.rotate(90.0), c.rotate(180.0), c.rotate(270.0)]


def split_complementary(c: Color, *, spread: float = 30.0) -> list[Color]:
    """Three colors: the base plus the two flanking its complement at ±``spread`` degrees."""
    return [c, c.rotate(180.0 - spread), c.rotate(180.0 + spread)]


def square(c: Color) -> list[Color]:
    """Alias for ``tetradic`` — four hues 90° apart."""
    return tetradic(c)


def monochromatic(c: Color, *, count: int = 5) -> list[Color]:
    """Lightness ramp around the input, evenly spaced in OKLab L."""
    if count < 1:
        return []
    if count == 1:
        return [c]
    L, ch, h = c.oklch
    from .color import Color as _C
    Ls = [i / (count - 1) for i in range(count)]
    return [_C.from_oklch(t, ch, h, c.alpha) for t in Ls]


def shades(c: Color, *, count: int = 5) -> list[Color]:
    """Steps from the color toward black."""
    from .color import Color as _C
    black = _C("#000000")
    return [_mix(c, black, i / (count - 1) if count > 1 else 0, space="oklab") for i in range(count)]


def tints(c: Color, *, count: int = 5) -> list[Color]:
    """Steps from the color toward white."""
    from .color import Color as _C
    white = _C("#ffffff")
    return [_mix(c, white, i / (count - 1) if count > 1 else 0, space="oklab") for i in range(count)]


def tones(c: Color, *, count: int = 5) -> list[Color]:
    """Steps from the color toward neutral gray of equal lightness."""
    from .color import Color as _C
    L, _, _ = c.oklch
    gray = _C.from_oklch(L, 0.0, 0.0)
    return [_mix(c, gray, i / (count - 1) if count > 1 else 0, space="oklab") for i in range(count)]


def scale(start: Color, end: Color, *, steps: int = 10,
          space: Literal["srgb", "linear-rgb", "lab", "lch", "oklab", "oklch"] = "oklab") -> list[Color]:
    """Interpolated scale between two colors with ``steps`` samples (inclusive)."""
    if steps < 2:
        return [start, end][:max(steps, 0)]
    return [_mix(start, end, i / (steps - 1), space=space) for i in range(steps)]


def stops(colors: list[Color], *, steps: int = 10,
          space: Literal["srgb", "linear-rgb", "lab", "lch", "oklab", "oklch"] = "oklab") -> list[Color]:
    """Multi-stop gradient through ``colors`` sampled at ``steps`` points."""
    if not colors:
        return []
    if len(colors) == 1 or steps <= 1:
        return [colors[0]] * max(steps, 1)
    out: list[Color] = []
    segments = len(colors) - 1
    for i in range(steps):
        t = i / (steps - 1)
        pos = t * segments
        idx = min(int(pos), segments - 1)
        local_t = pos - idx
        out.append(_mix(colors[idx], colors[idx + 1], local_t, space=space))
    return out
