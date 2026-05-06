"""hexcraft — the complete color library for Python."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version as _pkg_version

from . import colormaps
from .accessibility import best_text_color, find_accessible_pair
from .adapt import D50, D55, D65, D75, A, adapt
from .color import Color
from .colormaps import (
    ALL_MAPS,
    DIVERGING_MAPS,
    QUALITATIVE_MAPS,
    SEQUENTIAL_MAPS,
    brbg,
    cividis,
    colormap,
    inferno,
    magma,
    plasma,
    rdbu,
    set1,
    spectral,
    tab10,
    turbo,
    viridis,
)
from .contrast import apca_lc, passes_wcag, wcag_ratio
from .cvd import daltonize, simulate
from .distance import closest_from, closest_n_from, delta_e
from .gamut import clip, map_to_gamut
from .manipulate import blend, mix
from .palettes import (
    analogous,
    complementary,
    monochromatic,
    scale,
    shades,
    split_complementary,
    square,
    stops,
    tetradic,
    tints,
    tones,
    triadic,
)
from .parsers import ColorParseError, parse
from .temperature import kelvin_to_rgb, rgb_to_kelvin
from .tonal import (
    MATERIAL_TONES,
    TAILWIND_STOPS,
    material_tonal_palette,
    tailwind_scale,
)

try:
    __version__ = _pkg_version("hexcraft")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

__all__ = [
    "A",
    "ALL_MAPS",
    "Color",
    "ColorParseError",
    "D50",
    "D55",
    "D65",
    "D75",
    "DIVERGING_MAPS",
    "MATERIAL_TONES",
    "QUALITATIVE_MAPS",
    "SEQUENTIAL_MAPS",
    "TAILWIND_STOPS",
    "__version__",
    "adapt",
    "analogous",
    "apca_lc",
    "best_text_color",
    "blend",
    "brbg",
    "cividis",
    "clip",
    "closest_from",
    "closest_n_from",
    "colormap",
    "colormaps",
    "complementary",
    "daltonize",
    "delta_e",
    "find_accessible_pair",
    "inferno",
    "kelvin_to_rgb",
    "magma",
    "map_to_gamut",
    "material_tonal_palette",
    "mix",
    "monochromatic",
    "parse",
    "passes_wcag",
    "plasma",
    "rdbu",
    "rgb_to_kelvin",
    "scale",
    "set1",
    "shades",
    "simulate",
    "spectral",
    "split_complementary",
    "square",
    "stops",
    "tab10",
    "tailwind_scale",
    "tetradic",
    "tints",
    "tones",
    "triadic",
    "turbo",
    "viridis",
    "wcag_ratio",
]


def color(value: str | Color | tuple[float, ...]) -> Color:
    """Convenience constructor: ``hexcraft.color("oklch(0.7 0.2 30)")``."""
    return Color(value)
