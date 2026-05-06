"""Parse color strings into normalized component tuples.

Returns a `Parsed` namedtuple of (space, components, alpha). The Color class
calls `parse()` and converts based on `space`.

Supported syntax:
- #rgb, #rgba, #rrggbb, #rrggbbaa
- rgb(r, g, b) / rgb(r g b / a) / rgba(...)
- hsl(h, s%, l%) / hsl(h s% l% / a) / hsla(...)
- hwb(h w% b% / a)
- lab(L a b / a)        - L in % or [0..100], a/b numeric or %
- lch(L c h / a)        - L in % or [0..100], c numeric or %, h deg
- oklab(L a b / a)      - L in % or [0..1], a/b numeric or % (-0.4..0.4)
- oklch(L c h / a)      - L in % or [0..1], c numeric or % (0..0.4), h deg
- color(srgb r g b / a) - also srgb-linear, display-p3, rec2020 (limited)
- CSS named colors
"""

from __future__ import annotations

import re
from typing import NamedTuple

from .named import lookup as _lookup_name


class Parsed(NamedTuple):
    """Result of parsing a color string.

    ``space`` is the source color space ('srgb', 'hsl', 'oklch', etc.);
    ``components`` are its three numeric values in their natural units; and
    ``alpha`` is the alpha channel in [0, 1].
    """

    space: str
    components: tuple[float, float, float]
    alpha: float


_HEX_RE = re.compile(r"^#([0-9a-fA-F]{3,8})$")
_FUNC_RE = re.compile(r"^([a-zA-Z-]+)\(([^)]*)\)$")
_NUM_RE = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?(%|deg|rad|turn|grad)?$")


class ColorParseError(ValueError):
    """Raised when a color string cannot be interpreted."""


def _parse_hex(s: str) -> Parsed:
    m = _HEX_RE.match(s)
    if not m:
        raise ColorParseError(f"invalid hex: {s!r}")
    h = m.group(1)
    n = len(h)
    if n == 3:
        r, g, b = (int(c * 2, 16) for c in h)
        a = 255
    elif n == 4:
        r, g, b, a = (int(c * 2, 16) for c in h)
    elif n == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        a = 255
    elif n == 8:
        r, g, b, a = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16)
    else:
        raise ColorParseError(f"invalid hex length: #{h}")
    return Parsed("srgb", (r / 255.0, g / 255.0, b / 255.0), a / 255.0)


def _split_args(arg_str: str) -> tuple[list[str], str | None]:
    """Split into positional args and optional alpha after a `/`."""
    if "/" in arg_str:
        left, _, right = arg_str.partition("/")
        return _tokens(left), right.strip() or None
    if "," in arg_str:
        parts = [p.strip() for p in arg_str.split(",")]
        if len(parts) == 4:
            return parts[:3], parts[3]
        return parts, None
    return _tokens(arg_str), None


def _tokens(s: str) -> list[str]:
    return [p for p in re.split(r"[\s,]+", s.strip()) if p]


def _num(token: str, *, percent_scale: float = 1.0) -> float:
    token = token.strip()
    if token in ("none",):
        return 0.0
    if token.endswith("%"):
        return float(token[:-1]) / 100.0 * percent_scale
    if token.endswith("deg"):
        return float(token[:-3])
    if token.endswith("rad"):
        from math import degrees
        return degrees(float(token[:-3]))
    if token.endswith("turn"):
        return float(token[:-4]) * 360.0
    if token.endswith("grad"):
        return float(token[:-4]) * 0.9
    return float(token)


def _alpha(token: str | None) -> float:
    if token is None:
        return 1.0
    t = token.strip()
    if t.endswith("%"):
        return max(0.0, min(1.0, float(t[:-1]) / 100.0))
    return max(0.0, min(1.0, float(t)))


def _rgb_component(token: str) -> float:
    """rgb() per CSS: 0-255 number or 0-100%."""
    if token.endswith("%"):
        return float(token[:-1]) / 100.0
    return float(token) / 255.0


def _parse_rgb(args: str) -> Parsed:
    parts, alpha = _split_args(args)
    if len(parts) != 3:
        raise ColorParseError(f"rgb() expects 3 components, got {len(parts)}")
    r, g, b = (_rgb_component(p) for p in parts)
    return Parsed("srgb", (r, g, b), _alpha(alpha))


def _parse_hsl(args: str) -> Parsed:
    parts, alpha = _split_args(args)
    if len(parts) != 3:
        raise ColorParseError(f"hsl() expects 3 components, got {len(parts)}")
    h = _num(parts[0])
    s = _num(parts[1]) if "%" in parts[1] else _num(parts[1]) / 100.0
    L = _num(parts[2]) if "%" in parts[2] else _num(parts[2]) / 100.0
    return Parsed("hsl", (h, s, L), _alpha(alpha))


def _parse_hwb(args: str) -> Parsed:
    parts, alpha = _split_args(args)
    if len(parts) != 3:
        raise ColorParseError(f"hwb() expects 3 components, got {len(parts)}")
    h = _num(parts[0])
    w = _num(parts[1]) if "%" in parts[1] else _num(parts[1]) / 100.0
    bl = _num(parts[2]) if "%" in parts[2] else _num(parts[2]) / 100.0
    return Parsed("hwb", (h, w, bl), _alpha(alpha))


def _parse_lab(args: str) -> Parsed:
    parts, alpha = _split_args(args)
    if len(parts) != 3:
        raise ColorParseError("lab() expects 3 components")
    L = float(parts[0][:-1]) if parts[0].endswith("%") else float(parts[0])
    a = float(parts[1][:-1]) * 1.25 if parts[1].endswith("%") else float(parts[1])
    b = float(parts[2][:-1]) * 1.25 if parts[2].endswith("%") else float(parts[2])
    return Parsed("lab", (L, a, b), _alpha(alpha))


def _parse_lch(args: str) -> Parsed:
    parts, alpha = _split_args(args)
    if len(parts) != 3:
        raise ColorParseError("lch() expects 3 components")
    L = float(parts[0][:-1]) if parts[0].endswith("%") else float(parts[0])
    c = float(parts[1][:-1]) * 1.5 if parts[1].endswith("%") else float(parts[1])
    h = _num(parts[2])
    return Parsed("lch", (L, c, h), _alpha(alpha))


def _parse_oklab(args: str) -> Parsed:
    parts, alpha = _split_args(args)
    if len(parts) != 3:
        raise ColorParseError("oklab() expects 3 components")
    L = float(parts[0][:-1]) / 100.0 if parts[0].endswith("%") else float(parts[0])
    a = float(parts[1][:-1]) * 0.004 if parts[1].endswith("%") else float(parts[1])
    b = float(parts[2][:-1]) * 0.004 if parts[2].endswith("%") else float(parts[2])
    return Parsed("oklab", (L, a, b), _alpha(alpha))


def _parse_oklch(args: str) -> Parsed:
    parts, alpha = _split_args(args)
    if len(parts) != 3:
        raise ColorParseError("oklch() expects 3 components")
    L = float(parts[0][:-1]) / 100.0 if parts[0].endswith("%") else float(parts[0])
    c = float(parts[1][:-1]) * 0.004 if parts[1].endswith("%") else float(parts[1])
    h = _num(parts[2])
    return Parsed("oklch", (L, c, h), _alpha(alpha))


_COLOR_SPACE_KEYS = {
    "srgb": "srgb",
    "srgb-linear": "linear-rgb",
    "display-p3": "p3",
    "p3": "p3",
    "xyz-d65": "xyz",
    "xyz": "xyz",
}


def _parse_color_func(args: str) -> Parsed:
    parts, alpha = _split_args(args)
    if not parts:
        raise ColorParseError("color() missing space")
    key = parts[0].lower()
    space = _COLOR_SPACE_KEYS.get(key)
    if space is None:
        raise ColorParseError(f"unsupported color() space: {key}")
    comps = parts[1:]
    if len(comps) != 3:
        raise ColorParseError(f"color({key}) expects 3 components, got {len(comps)}")
    vals = tuple(_num(c) if not c.endswith("%") else float(c[:-1]) / 100.0 for c in comps)
    return Parsed(space, (vals[0], vals[1], vals[2]), _alpha(alpha))


def parse(s: str) -> Parsed:
    """Parse any CSS Color 4 syntax or named color into a ``Parsed`` tuple.

    Accepts hex (``#rgb``/``#rgba``/``#rrggbb``/``#rrggbbaa``), function
    notations (``rgb()``, ``hsl()``, ``hwb()``, ``lab()``, ``lch()``,
    ``oklab()``, ``oklch()``, ``color(...)``), and any of the 148 CSS named
    colors. Raises ``ColorParseError`` on invalid input.
    """
    s = s.strip()
    if not s:
        raise ColorParseError("empty color string")
    if s.startswith("#"):
        return _parse_hex(s)
    m = _FUNC_RE.match(s)
    if m:
        fn = m.group(1).lower()
        args = m.group(2)
        if fn in ("rgb", "rgba"):
            return _parse_rgb(args)
        if fn in ("hsl", "hsla"):
            return _parse_hsl(args)
        if fn == "hwb":
            return _parse_hwb(args)
        if fn == "lab":
            return _parse_lab(args)
        if fn == "lch":
            return _parse_lch(args)
        if fn == "oklab":
            return _parse_oklab(args)
        if fn == "oklch":
            return _parse_oklch(args)
        if fn == "color":
            return _parse_color_func(args)
        raise ColorParseError(f"unknown color function: {fn}")
    named = _lookup_name(s)
    if named is not None:
        r, g, b, a = named
        return Parsed("srgb", (r, g, b), a)
    raise ColorParseError(f"could not parse color: {s!r}")
