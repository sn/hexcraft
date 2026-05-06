"""Perceptual colormaps for data visualization.

Sequential maps (viridis/magma/plasma/inferno/cividis/turbo) are perceptually
uniform — equal steps in the colormap correspond to equal perceptual changes,
which preserves data structure when reproduced in greyscale or to color-blind
viewers. Diverging maps (RdBu, BrBG, Spectral) emphasize a center value;
qualitative maps (tab10, set1) provide categorical distinguishability.

Each map is exposed as a function of a scalar t ∈ [0, 1] returning a
``Color``, and as a callable that accepts ``n`` to produce ``n`` evenly
spaced colors. Stops are interpolated in OKLab for perceptual smoothness.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .color import Color


# Sequential maps — purple/blue → yellow/cream, perceptually uniform.
_VIRIDIS = (
    "#440154", "#482577", "#3f4788", "#33638d", "#2a788e", "#21908c",
    "#22a884", "#44bf70", "#7ad151", "#bddf26", "#fde725",
)
_MAGMA = (
    "#000004", "#180f3d", "#440f76", "#721f81", "#9f2f7f", "#cd4071",
    "#f1605d", "#fd9668", "#feca8d", "#fcfdbf", "#fcfdbf",
)
_PLASMA = (
    "#0d0887", "#41049d", "#6a00a8", "#8f0da4", "#b12a90", "#cc4778",
    "#e16462", "#f1844b", "#fca636", "#fbcd2a", "#f0f921",
)
_INFERNO = (
    "#000004", "#160b39", "#420a68", "#6a176e", "#932667", "#bc3754",
    "#dd513a", "#f3771a", "#fca50a", "#f6d746", "#fcffa4",
)
_CIVIDIS = (
    "#00224e", "#123570", "#3b496c", "#575d6d", "#707173", "#8a8678",
    "#a59c74", "#c3b369", "#e0cb59", "#f7e94d", "#ffea46",
)
_TURBO = (
    "#30123b", "#4145ab", "#4675ed", "#39a2fc", "#1bcfd4", "#24eca6",
    "#61fc6c", "#a4fc3b", "#d1e834", "#f3c63a", "#fb8022",
)

# Diverging — anchored on a neutral midpoint.
_RDBU = (
    "#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7", "#f7f7f7",
    "#d1e5f0", "#92c5de", "#4393c3", "#2166ac", "#053061",
)
_BRBG = (
    "#543005", "#8c510a", "#bf812d", "#dfc27d", "#f6e8c3", "#f5f5f5",
    "#c7eae5", "#80cdc1", "#35978f", "#01665e", "#003c30",
)
_SPECTRAL = (
    "#9e0142", "#d53e4f", "#f46d43", "#fdae61", "#fee08b", "#ffffbf",
    "#e6f598", "#abdda4", "#66c2a5", "#3288bd", "#5e4fa2",
)

# Qualitative — categorical distinguishability.
_TAB10 = (
    "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
    "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
)
_SET1 = (
    "#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00",
    "#ffff33", "#a65628", "#f781bf", "#999999",
)


def _make_continuous(stops: tuple[str, ...]) -> Callable[[float], Color]:
    """Return ``f(t)`` that samples the given stops in OKLab."""
    def f(t: float) -> Color:
        from .color import Color
        from .manipulate import mix
        t = max(0.0, min(1.0, t))
        if len(stops) == 1:
            return Color(stops[0])
        pos = t * (len(stops) - 1)
        idx = min(int(pos), len(stops) - 2)
        local = pos - idx
        return mix(Color(stops[idx]), Color(stops[idx + 1]), local, space="oklab")
    return f


def _sample_n(stops: tuple[str, ...], n: int) -> list[Color]:
    if n < 1:
        return []
    f = _make_continuous(stops)
    if n == 1:
        return [f(0.5)]
    return [f(i / (n - 1)) for i in range(n)]


def _qualitative(stops: tuple[str, ...]) -> Callable[[int], list[Color]]:
    def f(n: int | None = None) -> list[Color]:
        from .color import Color
        if n is None:
            return [Color(s) for s in stops]
        if n <= len(stops):
            return [Color(s) for s in stops[:n]]
        out = [Color(s) for s in stops]
        f_cont = _make_continuous(stops)
        out.extend(f_cont(i / (n - 1)) for i in range(len(stops), n))
        return out
    return f


class _ColormapNS:
    """Lazy access to colormaps with both ``map(t)`` and ``map.colors(n)`` styles."""

    def __init__(self, name: str, stops: tuple[str, ...], qualitative: bool = False) -> None:
        self.name = name
        self.stops = stops
        self.qualitative = qualitative
        self._continuous = _make_continuous(stops) if not qualitative else None

    def __call__(self, t: float) -> Color:
        if self.qualitative:
            from .color import Color
            i = int(round(t * (len(self.stops) - 1)))
            return Color(self.stops[i])
        return self._continuous(t)  # type: ignore[misc]

    def colors(self, n: int | None = None) -> list[Color]:
        """Return ``n`` evenly spaced colors from this map.

        For sequential/diverging maps ``n`` defaults to 256. For qualitative
        maps it defaults to the natural number of stops; passing ``n`` larger
        than that extends with interpolated entries.
        """
        if self.qualitative:
            return _qualitative(self.stops)(n)
        return _sample_n(self.stops, n if n is not None else 256)


viridis = _ColormapNS("viridis", _VIRIDIS)
magma = _ColormapNS("magma", _MAGMA)
plasma = _ColormapNS("plasma", _PLASMA)
inferno = _ColormapNS("inferno", _INFERNO)
cividis = _ColormapNS("cividis", _CIVIDIS)
turbo = _ColormapNS("turbo", _TURBO)
rdbu = _ColormapNS("RdBu", _RDBU)
brbg = _ColormapNS("BrBG", _BRBG)
spectral = _ColormapNS("Spectral", _SPECTRAL)
tab10 = _ColormapNS("tab10", _TAB10, qualitative=True)
set1 = _ColormapNS("Set1", _SET1, qualitative=True)


SEQUENTIAL_MAPS: dict[str, _ColormapNS] = {
    "viridis": viridis,
    "magma": magma,
    "plasma": plasma,
    "inferno": inferno,
    "cividis": cividis,
    "turbo": turbo,
}
DIVERGING_MAPS: dict[str, _ColormapNS] = {
    "RdBu": rdbu,
    "BrBG": brbg,
    "Spectral": spectral,
}
QUALITATIVE_MAPS: dict[str, _ColormapNS] = {
    "tab10": tab10,
    "Set1": set1,
}
ALL_MAPS: dict[str, _ColormapNS] = {**SEQUENTIAL_MAPS, **DIVERGING_MAPS, **QUALITATIVE_MAPS}


def colormap(name: str) -> _ColormapNS:
    """Look up a colormap by name (case-sensitive: 'viridis', 'RdBu', 'tab10', ...)."""
    if name not in ALL_MAPS:
        raise ValueError(f"unknown colormap {name!r}; available: {sorted(ALL_MAPS)}")
    return ALL_MAPS[name]
