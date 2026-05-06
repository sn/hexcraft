"""The Color class — central, immutable, fluent.

Internal canonical: linear sRGB + alpha. Components may fall outside [0, 1] to
preserve wide-gamut and HDR colors; gamut mapping is applied at output time.
"""

from __future__ import annotations

import math
from typing import Literal, Self

from . import named, parsers
from .spaces import cmyk as _cmyk
from .spaces import hsl, hsv, hwb, lab, oklab, srgb, xyz
from .spaces import p3 as _p3

Space = Literal[
    "srgb", "linear-rgb", "hsl", "hsv", "hwb",
    "lab", "lch", "oklab", "oklch", "xyz",
]


class Color:
    """An immutable color value.

    Construct via:
        Color("red") / Color("#ff0000") / Color("oklch(0.7 0.2 30)")
        Color.from_rgb(255, 0, 0)
        Color.from_oklch(0.628, 0.258, 29.2)

    Read components as properties (returns tuples in human-friendly units):
        c.hex, c.rgb, c.hsl, c.lab, c.oklch, ...
    """

    __slots__ = ("_lr", "_lg", "_lb", "_a")

    def __init__(self, value: str | Color | tuple[float, ...]) -> None:
        if isinstance(value, Color):
            self._lr, self._lg, self._lb, self._a = value._lr, value._lg, value._lb, value._a
            return
        if isinstance(value, str):
            r, g, b, a = _from_parsed(parsers.parse(value))
            object.__setattr__(self, "_lr", r)
            object.__setattr__(self, "_lg", g)
            object.__setattr__(self, "_lb", b)
            object.__setattr__(self, "_a", a)
            return
        if isinstance(value, tuple) and len(value) in (3, 4):
            return self.__init__(Color.from_rgb(*value))  # type: ignore[misc]
        raise TypeError(f"cannot construct Color from {type(value).__name__}")

    @classmethod
    def _from_linear(cls, r: float, g: float, b: float, a: float = 1.0) -> Self:
        obj = cls.__new__(cls)
        obj._lr, obj._lg, obj._lb, obj._a = r, g, b, a
        return obj

    # ── Constructors ──────────────────────────────────────────────────────

    @classmethod
    def from_rgb(cls, r: float, g: float, b: float, a: float = 1.0) -> Self:
        """Construct from gamma-encoded sRGB. Accepts 0–1 floats or 0–255 numbers."""
        if r > 1.0 or g > 1.0 or b > 1.0:
            r, g, b = r / 255.0, g / 255.0, b / 255.0
        lr, lg, lb = srgb.decode_rgb((r, g, b))
        return cls._from_linear(lr, lg, lb, a)

    @classmethod
    def from_hex(cls, value: str) -> Self:
        """Construct from a hex string, with or without a leading ``#``."""
        return cls.parse(value if value.startswith("#") else f"#{value}")

    @classmethod
    def from_linear_rgb(cls, r: float, g: float, b: float, a: float = 1.0) -> Self:
        """Construct directly from linear sRGB values (no gamma decoding)."""
        return cls._from_linear(r, g, b, a)

    @classmethod
    def from_hsl(cls, h: float, s: float, l: float, a: float = 1.0) -> Self:
        """Construct from HSL: hue in degrees, saturation and lightness in [0, 1]."""
        return cls.from_rgb(*hsl.hsl_to_srgb((h, s, l)), a=a)

    @classmethod
    def from_hsv(cls, h: float, s: float, v: float, a: float = 1.0) -> Self:
        """Construct from HSV: hue in degrees, saturation and value in [0, 1]."""
        return cls.from_rgb(*hsv.hsv_to_srgb((h, s, v)), a=a)

    @classmethod
    def from_hwb(cls, h: float, w: float, b: float, a: float = 1.0) -> Self:
        """Construct from HWB: hue in degrees, whiteness and blackness in [0, 1]."""
        return cls.from_rgb(*hwb.hwb_to_srgb((h, w, b)), a=a)

    @classmethod
    def from_lab(cls, L: float, a_: float, b: float, alpha: float = 1.0) -> Self:
        """Construct from CIE L*a*b*. L in [0, 100], a/b roughly in [-128, 128]."""
        x, y, z = lab.lab_to_xyz((L, a_, b))
        lr, lg, lb = xyz.xyz_to_linear_rgb((x, y, z))
        return cls._from_linear(lr, lg, lb, alpha)

    @classmethod
    def from_lch(cls, L: float, c: float, h: float, a: float = 1.0) -> Self:
        """Construct from CIE LCh (polar Lab). L in [0, 100], h in degrees."""
        return cls.from_lab(*lab.lch_to_lab((L, c, h)), alpha=a)

    @classmethod
    def from_oklab(cls, L: float, a_: float, b: float, alpha: float = 1.0) -> Self:
        """Construct from OKLab. L in [0, 1], a/b roughly in [-0.4, 0.4]."""
        lr, lg, lb = oklab.oklab_to_linear_rgb((L, a_, b))
        return cls._from_linear(lr, lg, lb, alpha)

    @classmethod
    def from_oklch(cls, L: float, c: float, h: float, a: float = 1.0) -> Self:
        """Construct from OKLCh (polar OKLab). L in [0, 1], c in [0, ~0.4], h in degrees."""
        return cls.from_oklab(*oklab.oklch_to_oklab((L, c, h)), alpha=a)

    @classmethod
    def from_xyz(cls, x: float, y: float, z: float, a: float = 1.0) -> Self:
        """Construct from CIE XYZ tristimulus values (D65 reference white)."""
        lr, lg, lb = xyz.xyz_to_linear_rgb((x, y, z))
        return cls._from_linear(lr, lg, lb, a)

    @classmethod
    def from_p3(cls, r: float, g: float, b: float, a: float = 1.0, *, gamma: bool = True) -> Self:
        """Construct from Display-P3. ``gamma=True`` treats inputs as gamma-encoded."""
        lin = _p3.p3_decode((r, g, b)) if gamma else (r, g, b)
        x, y, z = _p3.linear_p3_to_xyz(lin)
        lr, lg, lb = xyz.xyz_to_linear_rgb((x, y, z))
        return cls._from_linear(lr, lg, lb, a)

    @classmethod
    def from_cmyk(cls, c: float, m: float, y: float, k: float, a: float = 1.0) -> Self:
        """Naive CMYK → sRGB. Not color-accurate without an ICC profile."""
        return cls.from_rgb(*_cmyk.cmyk_to_srgb((c, m, y, k)), a=a)

    @classmethod
    def from_kelvin(cls, temperature: float, a: float = 1.0) -> Self:
        """Approximate sRGB color of a blackbody at the given temperature in K."""
        from .temperature import kelvin_to_rgb
        return cls.from_rgb(*kelvin_to_rgb(temperature), a=a)

    @classmethod
    def parse(cls, s: str) -> Self:
        """Parse any CSS Color 4 string or named color. Equivalent to ``Color(s)``."""
        return cls(s)

    # ── Component accessors ───────────────────────────────────────────────

    @property
    def alpha(self) -> float:
        """Alpha channel in [0, 1]."""
        return self._a

    @property
    def linear_rgb(self) -> tuple[float, float, float]:
        """Linear sRGB components. May be outside [0, 1] for wide-gamut colors."""
        return (self._lr, self._lg, self._lb)

    @property
    def srgb(self) -> tuple[float, float, float]:
        """Gamma-encoded sRGB in [0, 1] (clamped to gamut)."""
        r, g, b = srgb.encode_rgb(self.linear_rgb)
        return (max(0.0, min(1.0, r)), max(0.0, min(1.0, g)), max(0.0, min(1.0, b)))

    @property
    def srgb_unclamped(self) -> tuple[float, float, float]:
        """Gamma-encoded sRGB without clamping (may be outside [0, 1])."""
        return srgb.encode_rgb(self.linear_rgb)

    @property
    def rgb(self) -> tuple[int, int, int]:
        """Integer sRGB triple in [0, 255]."""
        r, g, b = self.srgb
        return (round(r * 255), round(g * 255), round(b * 255))

    @property
    def rgba(self) -> tuple[int, int, int, float]:
        """Integer sRGB triple plus alpha as a float."""
        r, g, b = self.rgb
        return (r, g, b, self._a)

    @property
    def hex(self) -> str:
        """``#rrggbb`` or ``#rrggbbaa`` (when alpha < 1)."""
        r, g, b = self.rgb
        if self._a >= 1.0:
            return f"#{r:02x}{g:02x}{b:02x}"
        a = round(self._a * 255)
        return f"#{r:02x}{g:02x}{b:02x}{a:02x}"

    @property
    def hsl(self) -> tuple[float, float, float]:
        """``(hue°, saturation, lightness)`` with s/l in [0, 1]."""
        return hsl.srgb_to_hsl(self.srgb)

    @property
    def hsv(self) -> tuple[float, float, float]:
        """``(hue°, saturation, value)`` with s/v in [0, 1]."""
        return hsv.srgb_to_hsv(self.srgb)

    @property
    def hwb(self) -> tuple[float, float, float]:
        """``(hue°, whiteness, blackness)`` with w/b in [0, 1]."""
        return hwb.srgb_to_hwb(self.srgb)

    @property
    def xyz(self) -> tuple[float, float, float]:
        """CIE XYZ tristimulus values relative to D65 white."""
        return xyz.linear_rgb_to_xyz(self.linear_rgb)

    @property
    def lab(self) -> tuple[float, float, float]:
        """CIE L*a*b* (D65). L in [0, 100], a/b roughly in [-128, 128]."""
        return lab.xyz_to_lab(self.xyz)

    @property
    def lch(self) -> tuple[float, float, float]:
        """CIE LCh — polar Lab. ``(lightness, chroma, hue°)``."""
        return lab.lab_to_lch(self.lab)

    @property
    def oklab(self) -> tuple[float, float, float]:
        """OKLab. L in [0, 1] (perceptual), a/b roughly in [-0.4, 0.4]."""
        return oklab.linear_rgb_to_oklab(self.linear_rgb)

    @property
    def oklch(self) -> tuple[float, float, float]:
        """OKLCh — polar OKLab. ``(lightness, chroma, hue°)``."""
        return oklab.oklab_to_oklch(self.oklab)

    @property
    def cmyk(self) -> tuple[float, float, float, float]:
        """Naive CMYK from sRGB. Not for press output without an ICC profile."""
        return _cmyk.srgb_to_cmyk(self.srgb)

    @property
    def kelvin(self) -> float | None:
        """Approximate CCT in K via McCamy's formula. ``None`` outside ~2000–25000 K."""
        from .temperature import rgb_to_kelvin
        return rgb_to_kelvin(self)

    @property
    def p3(self) -> tuple[float, float, float]:
        """Gamma-encoded Display-P3 components in [0, 1] (clamped)."""
        x, y, z = self.xyz
        lin = _p3.xyz_to_linear_p3((x, y, z))
        r, g, b = _p3.p3_encode(lin)
        return (max(0.0, min(1.0, r)), max(0.0, min(1.0, g)), max(0.0, min(1.0, b)))

    @property
    def p3_unclamped(self) -> tuple[float, float, float]:
        """Display-P3 components without clamping (may be outside [0, 1])."""
        x, y, z = self.xyz
        return _p3.p3_encode(_p3.xyz_to_linear_p3((x, y, z)))

    @property
    def luminance(self) -> float:
        """WCAG 2.x relative luminance (Y from linear sRGB, clamped to gamut)."""
        r, g, b = (max(0.0, min(1.0, c)) for c in self.linear_rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    @property
    def name(self) -> str:
        """Closest CSS named color."""
        return named.closest_name(self.srgb)

    # ── In-gamut check ────────────────────────────────────────────────────

    def in_gamut(self, space: Literal["srgb"] = "srgb", tolerance: float = 1e-4) -> bool:
        """``True`` if this color fits within the given gamut. Currently sRGB only."""
        if space != "srgb":
            raise NotImplementedError(f"in_gamut for {space} not yet supported")
        return all(-tolerance <= c <= 1.0 + tolerance for c in self.linear_rgb)

    # ── Manipulations (return new Color) ──────────────────────────────────

    def with_alpha(self, alpha: float) -> Self:
        """Return a new color with the alpha channel replaced."""
        return type(self)._from_linear(self._lr, self._lg, self._lb, alpha)

    def lighten(self, amount: float) -> Self:
        """Increase OKLab lightness by ``amount`` (clamped to [0, 1])."""
        L, c, h = self.oklch
        return type(self).from_oklch(min(1.0, max(0.0, L + amount)), c, h, self._a)

    def darken(self, amount: float) -> Self:
        """Decrease OKLab lightness by ``amount``. Equivalent to ``lighten(-amount)``."""
        return self.lighten(-amount)

    def saturate(self, amount: float) -> Self:
        """Add ``amount`` (scaled) to the OKLCh chroma, clamped at zero."""
        L, c, h = self.oklch
        new_c = max(0.0, c + amount * 0.4)
        return type(self).from_oklch(L, new_c, h, self._a)

    def desaturate(self, amount: float) -> Self:
        """Subtract ``amount`` from the OKLCh chroma. Equivalent to ``saturate(-amount)``."""
        return self.saturate(-amount)

    def rotate(self, degrees: float) -> Self:
        """Rotate hue in OKLCh by ``degrees``. Returns ``self`` when rotation is a multiple of 360°."""
        if degrees % 360.0 == 0.0:
            return self
        L, c, h = self.oklch
        return type(self).from_oklch(L, c, (h + degrees) % 360.0, self._a)

    def grayscale(self) -> Self:
        """Collapse chroma to zero, preserving OKLab lightness."""
        L, _, _ = self.oklch
        return type(self).from_oklch(L, 0.0, 0.0, self._a)

    def invert(self) -> Self:
        """Invert each linear sRGB component (``1 - c``)."""
        r, g, b = self.linear_rgb
        return type(self)._from_linear(1.0 - r, 1.0 - g, 1.0 - b, self._a)

    def complement(self) -> Self:
        """Rotate hue by 180°."""
        return self.rotate(180.0)

    def mix(self, other: Color, amount: float = 0.5, space: Space = "oklab") -> Self:
        """Mix with ``other`` in ``space``. ``amount`` weights ``other`` (0 → self, 1 → other)."""
        from .manipulate import mix as _mix
        return _mix(self, other, amount, space=space)  # type: ignore[return-value]

    def contrast(self, other: Color, *, method: Literal["wcag", "apca"] = "wcag") -> float:
        """Contrast against ``other``. Returns WCAG ratio (default) or signed APCA Lc."""
        from .contrast import apca_lc, wcag_ratio
        if method == "wcag":
            return wcag_ratio(self, other)
        return apca_lc(self, other)

    def delta_e(self, other: Color, *, method: Literal["76", "94", "2000", "cmc", "ok"] = "2000") -> float:
        """Color difference against ``other``. See :func:`hexcraft.delta_e` for methods."""
        from .distance import delta_e as _de
        return _de(self, other, method=method)

    def to_gamut(self, space: Literal["srgb"] = "srgb") -> Self:
        """Reduce OKLCh chroma until the result fits the target gamut (CSS Color 4)."""
        from .gamut import map_to_gamut
        return map_to_gamut(self, space=space)  # type: ignore[return-value]

    # ── Palette methods (return list of Color) ────────────────────────────

    def tints(self, count: int = 5) -> list[Self]:
        """``count`` colors stepping from this color toward white."""
        from .palettes import tints as _tints
        return _tints(self, count=count)  # type: ignore[return-value]

    def shades(self, count: int = 5) -> list[Self]:
        """``count`` colors stepping from this color toward black."""
        from .palettes import shades as _shades
        return _shades(self, count=count)  # type: ignore[return-value]

    lighter = tints
    darker = shades

    def tones(self, count: int = 5) -> list[Self]:
        """``count`` colors stepping from this color toward equal-luminance gray."""
        from .palettes import tones as _tones
        return _tones(self, count=count)  # type: ignore[return-value]

    def monochromatic(self, count: int = 5) -> list[Self]:
        """``count`` colors evenly spaced in OKLab lightness, same hue and chroma."""
        from .palettes import monochromatic as _mono
        return _mono(self, count=count)  # type: ignore[return-value]

    def analogous(self, count: int = 3, spread: float = 30.0) -> list[Self]:
        """``count`` analogous colors centered on this one, spaced by ``spread`` degrees."""
        from .palettes import analogous as _ana
        return _ana(self, count=count, spread=spread)  # type: ignore[return-value]

    def complementary(self) -> list[Self]:
        """Two colors: this one and its 180° complement."""
        from .palettes import complementary as _c
        return _c(self)  # type: ignore[return-value]

    def triadic(self) -> list[Self]:
        """Three colors evenly spaced 120° apart in hue."""
        from .palettes import triadic as _t
        return _t(self)  # type: ignore[return-value]

    def tetradic(self) -> list[Self]:
        """Four colors evenly spaced 90° apart in hue."""
        from .palettes import tetradic as _t
        return _t(self)  # type: ignore[return-value]

    def split_complementary(self, spread: float = 30.0) -> list[Self]:
        """Three colors: this one plus the two flanking the complement at ±``spread``°."""
        from .palettes import split_complementary as _sc
        return _sc(self, spread=spread)  # type: ignore[return-value]

    # ── CVD + accessibility ───────────────────────────────────────────────

    def simulate(self, kind: Literal["protanopia", "deuteranopia", "tritanopia"], severity: float = 1.0) -> Self:
        """Simulate how this color appears to a viewer with the given CVD."""
        from .cvd import simulate as _sim
        return _sim(self, kind, severity)  # type: ignore[return-value]

    def daltonize(self, kind: Literal["protanopia", "deuteranopia", "tritanopia"]) -> Self:
        """Adjust this color so a CVD viewer can distinguish it more easily."""
        from .cvd import daltonize as _dal
        return _dal(self, kind)  # type: ignore[return-value]

    def accessible_against(self, other: Color, *, ratio: float = 4.5,
                           direction: Literal["lighten", "darken", "auto"] = "auto") -> Self | None:
        """Return a nearby color meeting WCAG ``ratio`` against ``other``, or None."""
        from .accessibility import find_accessible_pair
        return find_accessible_pair(self, other, ratio=ratio, direction=direction)  # type: ignore[return-value]

    # ── Tonal palettes ────────────────────────────────────────────────────

    def material_palette(self) -> dict[int, Self]:
        """Material You-style 13-stop tonal palette (keys: 0–100)."""
        from .tonal import material_tonal_palette
        return material_tonal_palette(self)  # type: ignore[return-value]

    def tailwind(self) -> dict[int, Self]:
        """Tailwind-style 50–950 scale (11 stops)."""
        from .tonal import tailwind_scale
        return tailwind_scale(self)  # type: ignore[return-value]

    # ── Formatting ────────────────────────────────────────────────────────

    def css(self, fmt: Literal["hex", "rgb", "hsl", "hwb", "lab", "lch", "oklab", "oklch"] = "hex") -> str:
        """Render as a CSS string in the requested format. ``hex`` by default."""
        from .formatters import format_css
        return format_css(self, fmt)

    def __str__(self) -> str:
        return self.hex

    def __repr__(self) -> str:
        return f"Color({self.hex!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return NotImplemented
        return (
            math.isclose(self._lr, other._lr, abs_tol=1e-6)
            and math.isclose(self._lg, other._lg, abs_tol=1e-6)
            and math.isclose(self._lb, other._lb, abs_tol=1e-6)
            and math.isclose(self._a, other._a, abs_tol=1e-6)
        )

    def __hash__(self) -> int:
        return hash((round(self._lr, 6), round(self._lg, 6), round(self._lb, 6), round(self._a, 6)))


def _from_parsed(p: parsers.Parsed) -> tuple[float, float, float, float]:
    """Convert parser output to canonical (linear_r, linear_g, linear_b, alpha)."""
    space = p.space
    comp = p.components
    a = p.alpha
    if space == "srgb":
        lr, lg, lb = srgb.decode_rgb(comp)
        return lr, lg, lb, a
    if space == "linear-rgb":
        return comp[0], comp[1], comp[2], a
    if space == "hsl":
        return _from_parsed(parsers.Parsed("srgb", hsl.hsl_to_srgb(comp), a))
    if space == "hsv":
        return _from_parsed(parsers.Parsed("srgb", hsv.hsv_to_srgb(comp), a))
    if space == "hwb":
        return _from_parsed(parsers.Parsed("srgb", hwb.hwb_to_srgb(comp), a))
    if space == "lab":
        x, y, z = lab.lab_to_xyz(comp)
        lr, lg, lb = xyz.xyz_to_linear_rgb((x, y, z))
        return lr, lg, lb, a
    if space == "lch":
        return _from_parsed(parsers.Parsed("lab", lab.lch_to_lab(comp), a))
    if space == "oklab":
        lr, lg, lb = oklab.oklab_to_linear_rgb(comp)
        return lr, lg, lb, a
    if space == "oklch":
        return _from_parsed(parsers.Parsed("oklab", oklab.oklch_to_oklab(comp), a))
    if space == "xyz":
        lr, lg, lb = xyz.xyz_to_linear_rgb(comp)
        return lr, lg, lb, a
    if space == "p3":
        x, y, z = _p3.linear_p3_to_xyz(comp)
        lr, lg, lb = xyz.xyz_to_linear_rgb((x, y, z))
        return lr, lg, lb, a
    raise ValueError(f"unknown space from parser: {space}")
