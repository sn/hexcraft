# hexcraft

The complete color library for Python. Parse, convert, manipulate, mix, measure, and visualize color across 11 color spaces — with zero required dependencies and a single fluent `Color` API.

```python
from hexcraft import Color

c = Color("oklch(0.7 0.15 250)")
c.hex                        # '#5e91d8'
c.contrast(Color("white"))   # 2.83
c.lighter(5)                 # [Color, Color, Color, Color, Color]
c.material_palette()         # {0..100: Color}  Material You tonal scale
c.simulate("deuteranopia")   # color as seen by red-green color-blind viewers
```

---

## Table of contents

- [Installation](#installation)
- [Quick start](#quick-start)
- [Parsing](#parsing)
- [Color spaces](#color-spaces)
- [Reading components](#reading-components)
- [Manipulation](#manipulation)
- [Mixing and blending](#mixing-and-blending)
- [Palettes and harmonies](#palettes-and-harmonies)
- [Tonal scales (Material You, Tailwind)](#tonal-scales-material-you-tailwind)
- [Perceptual colormaps](#perceptual-colormaps)
- [Accessibility (WCAG, APCA)](#accessibility-wcag-apca)
- [Color difference (ΔE)](#color-difference-Δe)
- [Gamut mapping](#gamut-mapping)
- [Color blindness simulation and daltonization](#color-blindness-simulation-and-daltonization)
- [Color temperature (Kelvin)](#color-temperature-kelvin)
- [Closest match in a palette](#closest-match-in-a-palette)
- [Display-P3 and chromatic adaptation](#display-p3-and-chromatic-adaptation)
- [CMYK](#cmyk)
- [Numpy arrays and images](#numpy-arrays-and-images)
- [Command-line interface](#command-line-interface)
- [API reference](#api-reference)
- [License](#license)

---

## Installation

```bash
pip install hexcraft               # core, zero dependencies
pip install 'hexcraft[numpy]'      # vectorized array ops + image utilities
pip install 'hexcraft[science]'    # full color-science integration (reserved)
pip install 'hexcraft[dev]'        # tests, ruff, mypy
```

Requires Python 3.10 or newer.

---

## Quick start

```python
from hexcraft import Color

# Parse anything CSS Color 4 supports
c = Color("oklch(0.7 0.15 250)")

# Read in any space
c.hex                # '#5e91d8'
c.rgb                # (94, 145, 216)
c.hsl                # (213.16, 0.59, 0.61)
c.lab                # (58.5, -3.5, -38.7)
c.oklch              # (0.7, 0.15, 250.0)

# Manipulate (immutable — every method returns a new Color)
c.lighten(0.1)
c.rotate(60)
c.with_alpha(0.5)

# Mix in any space
c.mix(Color("red"))                       # OKLab by default
c.mix(Color("red"), 0.3, space="oklch")   # shortest-hue interpolation

# Accessibility
c.contrast(Color("white"))                # WCAG ratio
c.accessible_against(Color("white"))      # auto-shift to meet 4.5:1

# Generate palettes
c.tints(5)                                # 5 steps to white
c.material_palette()                      # 13-stop Material You scale
c.tailwind()                              # 11-stop Tailwind 50–950
c.triadic()                               # 3 colors 120° apart

# CSS output
c.css("hex")                              # '#5e91d8'
c.css("oklch")                            # 'oklch(0.7 0.15 250)'
```

---

## Parsing

`Color(value)` accepts every CSS Color 4 syntax, all 148 CSS named colors, hex with optional alpha, and existing `Color` objects:

```python
Color("#ff0000")
Color("#f00")                              # 3-digit
Color("#f008")                             # 4-digit (with alpha)
Color("#ff000080")                         # 8-digit (with alpha)

Color("rgb(255, 0, 0)")
Color("rgb(255 0 0)")                      # space-separated CSS Color 4
Color("rgb(100%, 0%, 0%)")
Color("rgba(255, 0, 0, 0.5)")
Color("rgb(255 0 0 / 50%)")

Color("hsl(0, 100%, 50%)")
Color("hsl(120deg 100% 50%)")
Color("hsl(0.333turn 100% 50%)")
Color("hsla(0, 100%, 50%, 0.5)")

Color("hwb(0 0% 0%)")
Color("lab(54 81 70)")
Color("lch(54 100 41)")
Color("oklab(0.628 0.225 0.126)")
Color("oklch(0.628 0.258 29.234)")

Color("color(srgb 1 0 0)")
Color("color(srgb-linear 1 0 0)")
Color("color(display-p3 1 0 0)")
Color("color(xyz 0.412 0.213 0.019)")

Color("rebeccapurple")                     # any of 148 CSS named colors
Color("transparent")                       # also valid; alpha = 0

Color(other_color)                         # copy
```

Hue accepts `deg` (default), `rad`, `turn`, or `grad` units. `none` is treated as `0`. Errors raise `hexcraft.ColorParseError`.

```python
from hexcraft import parse, ColorParseError

try:
    c = Color("not-a-color")
except ColorParseError as e:
    print(e)                               # could not parse color: 'not-a-color'

# Direct parser if you need the intermediate representation:
parse("oklch(0.7 0.15 250)")              # Parsed(space='oklch', components=(0.7, 0.15, 250.0), alpha=1.0)
```

---

## Color spaces

`hexcraft` works canonically in linear sRGB and converts to any space on demand. Out-of-gamut and HDR values pass through; gamut mapping is applied at output.

| Space          | Property             | Constructor                             |
|----------------|----------------------|-----------------------------------------|
| sRGB (gamma)   | `c.rgb`, `c.srgb`, `c.hex` | `Color.from_rgb(255, 0, 0)`         |
| Linear sRGB    | `c.linear_rgb`       | `Color.from_linear_rgb(1, 0, 0)`        |
| HSL            | `c.hsl`              | `Color.from_hsl(0, 1, 0.5)`             |
| HSV            | `c.hsv`              | `Color.from_hsv(0, 1, 1)`               |
| HWB            | `c.hwb`              | `Color.from_hwb(0, 0, 0)`               |
| CIE XYZ (D65)  | `c.xyz`              | `Color.from_xyz(0.412, 0.213, 0.019)`   |
| CIE Lab        | `c.lab`              | `Color.from_lab(54, 81, 70)`            |
| CIE LCh        | `c.lch`              | `Color.from_lch(54, 107, 41)`           |
| OKLab          | `c.oklab`            | `Color.from_oklab(0.63, 0.22, 0.13)`    |
| OKLCh          | `c.oklch`            | `Color.from_oklch(0.63, 0.26, 29)`      |
| Display-P3     | `c.p3`               | `Color.from_p3(1, 0, 0)`                |
| CMYK (naive)   | `c.cmyk`             | `Color.from_cmyk(0, 1, 1, 0)`           |
| Kelvin (CCT)   | `c.kelvin`           | `Color.from_kelvin(2700)`               |

`hsl/hsv/hwb` use degrees for hue; `lab/lch/oklab/oklch` use the CIE/OK natural units. Hue is in `[0, 360)`. CMYK is naive algebraic — see [CMYK](#cmyk) for caveats.

---

## Reading components

```python
c = Color("#3498db")

c.alpha                    # 1.0
c.rgb                      # (52, 152, 219)
c.rgba                     # (52, 152, 219, 1.0)
c.srgb                     # (0.204, 0.596, 0.859)  — gamma-encoded, clamped
c.srgb_unclamped           # same but allows out-of-gamut
c.linear_rgb               # (0.034, 0.318, 0.708)
c.hsl                      # (204.1, 0.70, 0.53)
c.hsv                      # (204.1, 0.76, 0.86)
c.hwb                      # (204.1, 0.20, 0.14)
c.xyz                      # (0.222, 0.247, 0.700)
c.lab                      # (56.9, -2.4, -39.0)
c.lch                      # (56.9, 39.0, 266.5)
c.oklab                    # (0.65, -0.06, -0.12)
c.oklch                    # (0.65, 0.13, 242.7)
c.p3                       # (0.252, 0.589, 0.851)
c.cmyk                     # (0.76, 0.31, 0.0, 0.14)
c.kelvin                   # ~10500 (or None for non-blackbody chromaticities)

c.luminance                # 0.281 — WCAG relative luminance
c.name                     # 'dodgerblue' — closest CSS named color
c.in_gamut()               # True/False — within sRGB
```

`linear_rgb` and `srgb_unclamped` may contain values outside `[0, 1]` to faithfully represent wide-gamut and HDR colors. Use `c.to_gamut()` to fold back into sRGB.

---

## Manipulation

Every method is immutable and returns a new `Color`. Operations work in OKLCh by default for perceptual uniformity.

```python
c = Color("#3498db")

c.lighten(0.1)             # +0.1 in OKLab L
c.darken(0.1)
c.saturate(0.2)            # +chroma in OKLCh
c.desaturate(0.2)
c.rotate(60)               # rotate hue by 60°
c.complement()             # rotate(180)
c.grayscale()              # collapse chroma to 0
c.invert()                 # 1 - rgb in linear sRGB
c.with_alpha(0.5)
```

Equality and hashing use linear-sRGB tolerance (≈ 1e-6) and are well-behaved across round-trips:

```python
Color("red") == Color("#ff0000") == Color("rgb(255, 0, 0)")  # True
{Color("red"), Color("#ff0000")}                              # set of size 1
```

---

## Mixing and blending

`mix` interpolates two colors in any space; the default is OKLab for smooth, hue-faithful results. Hue spaces (`hsl`, `hsv`, `hwb`, `lch`, `oklch`) automatically take the shortest-arc path.

```python
from hexcraft import Color, mix, blend

mix(Color("red"), Color("blue"))                       # OKLab midpoint
mix(Color("red"), Color("blue"), 0.3)                  # 30% toward blue
mix(Color("red"), Color("blue"), 0.5, space="oklch")   # different perceptual path
mix(Color("red"), Color("blue"), 0.5, space="srgb")    # naive sRGB lerp

# Method form (always defaults to OKLab):
Color("red").mix(Color("blue"), 0.5)
```

`blend` does Porter-Duff "over" composite in linear sRGB, the gamma-correct way to alpha-composite:

```python
fg = Color("blue").with_alpha(0.5)
bg = Color("red")
blend(bg, fg)              # red showing through 50% blue
```

---

## Palettes and harmonies

Module-level functions return a list of `Color`. Equivalent methods on `Color` return the same lists:

```python
from hexcraft import (
    complementary, analogous, triadic, tetradic, split_complementary,
    monochromatic, shades, tints, tones, scale, stops,
)

c = Color("#3498db")

complementary(c)                 # [c, c.rotate(180)]
triadic(c)                       # 3 colors 120° apart
tetradic(c)                      # 4 colors 90° apart
split_complementary(c)           # base + 2 colors flanking the complement
analogous(c, count=5, spread=20) # N colors spaced by 20° hue

shades(c, count=5)               # toward black
tints(c, count=5)                # toward white
tones(c, count=5)                # toward equal-lightness gray
monochromatic(c, count=7)        # full lightness ramp at fixed hue/chroma

# Method-style (return type-stable lists):
c.tints(10)
c.lighter(10)                    # alias for .tints()
c.darker(10)                     # alias for .shades()
c.triadic()
c.analogous(count=5)
```

Two-color and multi-stop scales:

```python
scale(Color("red"), Color("blue"), steps=10, space="oklab")
stops([Color("red"), Color("green"), Color("blue")], steps=20, space="oklab")
```

`steps` includes both endpoints. `space` accepts any mixing space.

---

## Tonal scales (Material You, Tailwind)

```python
c = Color("#3498db")

c.material_palette()
# {0: '#000000', 10: '#00040a', 20: '#00182a', 30: '#00314f', 40: '#004c77',
#  50: '#0069a1', 60: '#1d87c9', 70: '#45a7eb', 80: '#7bc6ff', 90: '#c0e3ff',
#  95: '#e0f1ff', 99: '#f9fcff', 100: '#ffffff'}

c.tailwind()
# {50: '#edf7ff', 100: '#d4ebff', 200: '#9fd5ff', 300: '#65b3ed', 400: '#308ecc',
#  500: '#0069a1', 600: '#00527f', 700: '#003b5e', 800: '#002943', 900: '#00182a',
#  950: '#000a16'}
```

Both implementations build on OKLCh — they preserve the source hue, hold chroma roughly constant for Material, and ramp chroma for Tailwind so the extreme stops stay legible. Out-of-gamut points are folded back into sRGB via OKLCh chroma reduction.

```python
from hexcraft import (
    material_tonal_palette, tailwind_scale,
    MATERIAL_TONES, TAILWIND_STOPS,
)

material_tonal_palette(c)        # equivalent to c.material_palette()
tailwind_scale(c)                # equivalent to c.tailwind()
MATERIAL_TONES                   # (0, 10, 20, ..., 100)
TAILWIND_STOPS                   # (50, 100, 200, ..., 950)
```

---

## Perceptual colormaps

Eleven named colormaps are bundled, each interpolated in OKLab so that any sample size stays perceptually uniform.

| Name        | Type         | Notes                                                            |
|-------------|--------------|------------------------------------------------------------------|
| `viridis`   | sequential   | Purple → yellow, default for matplotlib                          |
| `magma`     | sequential   | Black → cream, warm                                              |
| `plasma`    | sequential   | Purple → yellow, more saturated than viridis                     |
| `inferno`   | sequential   | Black → cream, hotter than magma                                 |
| `cividis`   | sequential   | Color-blind friendly dark blue → yellow                          |
| `turbo`     | rainbow      | Blue → red, replaces `jet`                                       |
| `rdbu`      | diverging    | ColorBrewer Red–Blue                                             |
| `brbg`      | diverging    | ColorBrewer Brown–Bluegreen                                      |
| `spectral`  | diverging    | ColorBrewer Spectral                                             |
| `tab10`     | qualitative  | matplotlib's Tableau 10                                          |
| `set1`      | qualitative  | ColorBrewer Set1                                                 |

Each map is callable and exposes a `.colors(n)` discrete sampler:

```python
from hexcraft import viridis, magma, rdbu, tab10, colormap

viridis(0.5)                     # Color at midpoint
viridis.colors(8)                # 8 evenly spaced Colors

magma(0.0).hex                   # '#000004' (deep black)
magma(1.0).hex                   # '#fcfdbf' (cream)

rdbu(0.0)                        # red end
rdbu(0.5)                        # neutral midpoint
rdbu(1.0)                        # blue end

tab10.colors()                   # all 10 categorical colors
tab10.colors(15)                 # extends with interpolation if you ask for more

colormap("viridis")(0.5)         # lookup by string
```

Maps are also grouped:

```python
from hexcraft import SEQUENTIAL_MAPS, DIVERGING_MAPS, QUALITATIVE_MAPS, ALL_MAPS

list(SEQUENTIAL_MAPS)            # ['viridis', 'magma', ..., 'turbo']
ALL_MAPS["RdBu"](0.7)
```

---

## Accessibility (WCAG, APCA)

```python
from hexcraft import (
    Color, wcag_ratio, passes_wcag, apca_lc,
    find_accessible_pair, best_text_color,
)

wcag_ratio(Color("white"), Color("black"))     # 21.0
wcag_ratio(Color("#777"), Color("#fff"))       # 4.48

passes_wcag(Color("#777"), Color("#fff"))                 # False (AA, normal text)
passes_wcag(Color("#777"), Color("#fff"), large=True)     # True (AA, large text)
passes_wcag(Color("#777"), Color("#fff"), level="AAA")    # False

apca_lc(Color("black"), Color("white"))        # -106.04 (dark on light → negative)
apca_lc(Color("white"), Color("black"))        #  107.88 (light on dark → positive)
apca_lc(Color("#888"), Color("white"))         #  -63.06
```

`find_accessible_pair` walks lightness in OKLCh until a target ratio is met:

```python
fg = Color("#888888")
bg = Color("white")
fixed = find_accessible_pair(fg, bg, ratio=4.5)
# fixed = Color('#777777') — minimal nudge, still close to original

# Method form
Color("#888").accessible_against(Color("white"), ratio=4.5)

# Specify direction
find_accessible_pair(fg, bg, ratio=7.0, direction="darken")
```

For a quick "black or white?" decision:

```python
best_text_color(Color("#3498db"))   # Color('#000000')
best_text_color(Color("#222"))      # Color('#ffffff')
```

WCAG ratios are symmetric, in `[1, 21]`. APCA Lc is signed: negative for dark text on light backgrounds, positive for light on dark; magnitude is what you compare against the published readability tables.

---

## Color difference (ΔE)

```python
from hexcraft import delta_e

delta_e(a, b, method="76")     # CIE76 — Euclidean in Lab, fastest
delta_e(a, b, method="94")     # CIE94 — graphic-arts weighting
delta_e(a, b, method="2000")   # CIEDE2000 — current CIE recommendation (default)
delta_e(a, b, method="cmc")    # CMC(l:c) with l=2 c=1, textile standard
delta_e(a, b, method="ok")     # Euclidean in OKLab, modern alternative

# Method form
Color("red").delta_e(Color("orangered"))
```

Rough thresholds for CIEDE2000: `<1` imperceptible, `1–2` perceptible to a trained eye, `>5` clearly different.

---

## Gamut mapping

When a color exceeds sRGB (e.g., `oklch(0.7 0.4 30)` is more saturated than sRGB can show), `to_gamut()` reduces its OKLCh chroma until it fits, preserving lightness and hue (CSS Color 4 algorithm):

```python
wide = Color.from_oklch(0.7, 0.4, 30)
wide.in_gamut()                  # False
mapped = wide.to_gamut()
mapped.in_gamut()                # True
mapped.hex                       # '#ff6551'

# Cheaper alternative: per-channel clip in linear sRGB
from hexcraft import clip
clip(wide).hex
```

---

## Color blindness simulation and daltonization

```python
from hexcraft import Color, simulate, daltonize

red = Color("red")

simulate(red, "protanopia")          # red as protans (red-blind) see it
simulate(red, "deuteranopia")        # red as deutans (green-blind) see it
simulate(red, "tritanopia")          # red as tritans (blue-blind) see it
simulate(red, "deuteranopia", severity=0.5)   # interpolate to anomalous trichromacy

daltonize(red, "deuteranopia")       # adjust the color so deutans can distinguish it

# Method forms
red.simulate("deuteranopia")
red.daltonize("deuteranopia")
```

Simulation uses Machado/Oliveira/Fernandes (2009) physiologically-based matrices; `severity` interpolates between full vision (`0.0`) and complete dichromacy (`1.0`). Daltonization uses Fidaner-style error redistribution onto channels the viewer can still perceive.

```python
# Concrete example: red and green look similar to deutans → daltonize for a UI
button_a = Color("#10b981")          # success green
button_b = Color("#ef4444")          # error red
button_a.daltonize("deuteranopia")   # shifted green so it remains distinguishable
button_b.daltonize("deuteranopia")
```

---

## Color temperature (Kelvin)

```python
from hexcraft import Color

Color.from_kelvin(2700).hex      # '#ffa757'  warm tungsten
Color.from_kelvin(5500).hex      # '#ffedde'  daylight
Color.from_kelvin(6500).hex      # '#fffefa'  D65 (sRGB white point)
Color.from_kelvin(9000).hex      # '#d2dfff'  cool blue

c = Color("#fffefa")
c.kelvin                         # ~6300 K (returns None outside ~2000–25000 K)
```

Forward direction uses Tanner Helland's piecewise approximation. Inverse (CCT from a color) uses McCamy's cubic in CIE xy chromaticity. Both are visualization-grade, not photometric.

---

## Closest match in a palette

```python
from hexcraft import Color, closest_from, closest_n_from

brand = [
    Color("#3b82f6"),  # blue
    Color("#10b981"),  # green
    Color("#ef4444"),  # red
    Color("#f59e0b"),  # amber
]

closest_from(Color("#ee5544"), brand)
# Color('#ef4444') — best perceptual match by CIEDE2000

closest_n_from(Color("#ee5544"), brand, n=2)
# [Color('#ef4444'), Color('#f59e0b')] — sorted by ΔE

# Use a different metric for image-scale work
closest_from(target, brand, method="ok")
```

The default metric is `"2000"` (CIEDE2000). Use `"ok"` for fast batch matching and `"cmc"` for textile/print contexts.

---

## Display-P3 and chromatic adaptation

```python
red_p3 = Color("color(display-p3 1 0 0)")
red_p3.hex                       # '#ff0000' (out-of-gamut clipped to sRGB red)
red_p3.p3                        # (1.0, 0.0, 0.0) — round-trips through P3

c = Color("#3498db")
c.p3                             # gamma-encoded P3 in [0, 1]
Color.from_p3(0.252, 0.589, 0.851)
```

For converting XYZ between white points (e.g., D65 ↔ D50 for ICC v4 work):

```python
from hexcraft import adapt, D50, D65
from hexcraft import D55, D75, A      # also available

adapt((0.5, 0.6, 0.7), D65, D50)              # Bradford (default)
adapt((0.5, 0.6, 0.7), D65, D50, method="cat16")
adapt((0.5, 0.6, 0.7), D65, D50, method="xyz")  # simplest, von Kries XYZ scaling
```

---

## CMYK

```python
Color("red").cmyk                # (0.0, 1.0, 1.0, 0.0)
Color.from_cmyk(0.5, 0.2, 0.0, 0.1)
```

This is the algebraic CMYK that browsers and design tools display when no profile is attached. **It is not color-accurate for press output** — real print workflows go through ICC profiles (SWOP, FOGRA, GRACoL, etc.). Use it for quick previews and color picker UI only.

---

## Numpy arrays and images

`hexcraft.arrays` (requires `numpy`) provides vectorized conversions for image-scale work:

```python
import numpy as np
from hexcraft.arrays import (
    srgb_decode, srgb_encode,
    linear_rgb_to_xyz, xyz_to_linear_rgb,
    linear_rgb_to_oklab, oklab_to_linear_rgb,
    srgb_to_oklab, oklab_to_srgb,
    relative_luminance, wcag_ratio, delta_e_ok,
)

img = np.random.rand(1024, 1024, 3)         # gamma sRGB image
ok = srgb_to_oklab(img)                     # (H, W, 3) in OKLab
luma = relative_luminance(img)              # (H, W) WCAG relative luminance
ratios = wcag_ratio(img, np.array([1, 1, 1]))  # contrast against white
diffs = delta_e_ok(img, np.array([1, 0, 0]))   # per-pixel OKLab ΔE vs red
```

`hexcraft.image` provides higher-level image utilities:

```python
import numpy as np
from hexcraft.image import dominant_colors, average_color

img = np.array(...).astype(np.uint8)         # or float in [0, 1]; (H, W, 3) or (H, W, 4)

# k-means clustering in OKLab space (perceptually meaningful)
top5 = dominant_colors(img, n=5)
# [Color('#3a8fd2'), Color('#f4ecd0'), Color('#221d18'), ...]
# ordered by cluster size (most-common first)

# Median-cut alternative (faster, less perceptual)
top5 = dominant_colors(img, n=5, method="median_cut")

# For very large images, dominant_colors subsamples to 50_000 pixels by default;
# pass sample=None to use every pixel, or sample=N to control:
dominant_colors(img, n=5, sample=10_000, seed=42)

# Gamma-correct mean
average_color(img)
```

---

## Command-line interface

Installing `hexcraft` registers a `hexcraft` console script. Output uses ANSI 24-bit color blocks when stdout is a TTY.

```text
$ hexcraft inspect "#3498db"
#3498db
  hex      #3498db
  rgb      rgb(52, 152, 219)
  hsl      hsl(204.1 69.9% 53.1%)
  lab      lab(60.2 -6.1 -42.2)
  oklch    oklch(0.653 0.135 242.7)
  cmyk     76.3% 30.6% 0.0% 14.1%
  luma     0.2830
  kelvin   ~10500 K
  name     dodgerblue
  in sRGB  True
```

```text
$ hexcraft convert red --to oklch
oklch(0.628 0.258 29.23)

$ hexcraft palette "#3498db" --type material
       0  #000000
      10  #00040a
      20  #00182a
      ...
     100  #ffffff

$ hexcraft palette red --type triadic
       0  #ff0000
       1  #00ae00
       2  #4f6fff

$ hexcraft contrast "#888" white
  fg          #888888
  bg          #ffffff
  WCAG ratio  3.54:1
  AA          FAIL  (large: PASS)
  AAA         FAIL  (large: FAIL)
  APCA Lc     -63.1
  → try fg #777777 for AA

$ hexcraft closest "#ee5544" "#3b82f6" "#10b981" "#ef4444" "#f59e0b"
  target  #ee5544
  match   #ef4444
```

Subcommands:

| Command       | Purpose                                                     |
|---------------|-------------------------------------------------------------|
| `inspect`     | Show all common representations + closest CSS name + CCT    |
| `convert`     | Render a color as a CSS string in any space                 |
| `palette`     | Emit a palette of any type to stdout                        |
| `contrast`    | WCAG ratio + AA/AAA pass + APCA Lc + suggested fix on fail  |
| `closest`     | Find the closest entry in a palette by ΔE                   |

Use `hexcraft <command> --help` for full options.

---

## API reference

### `hexcraft.Color`

**Constructors**

| Method                                  | Notes                                              |
|-----------------------------------------|----------------------------------------------------|
| `Color(value)`                          | string / Color / `(r,g,b)` or `(r,g,b,a)` tuple    |
| `Color.parse(s)`                        | same as `Color(s)`; raises `ColorParseError`       |
| `Color.from_rgb(r, g, b, a=1)`          | accepts 0–1 floats or 0–255 ints                    |
| `Color.from_hex(value)`                 |                                                    |
| `Color.from_linear_rgb(r, g, b, a=1)`   |                                                    |
| `Color.from_hsl(h, s, l, a=1)`          | h in degrees, s/l in `[0, 1]`                       |
| `Color.from_hsv(h, s, v, a=1)`          |                                                    |
| `Color.from_hwb(h, w, b, a=1)`          |                                                    |
| `Color.from_lab(L, a, b, alpha=1)`      | L `[0, 100]`, a/b roughly `[-128, 128]`             |
| `Color.from_lch(L, c, h, a=1)`          |                                                    |
| `Color.from_oklab(L, a, b, alpha=1)`    | L `[0, 1]`, a/b roughly `[-0.4, 0.4]`               |
| `Color.from_oklch(L, c, h, a=1)`        |                                                    |
| `Color.from_xyz(x, y, z, a=1)`          | D65 reference white                                |
| `Color.from_p3(r, g, b, a=1, gamma=True)` |                                                  |
| `Color.from_cmyk(c, m, y, k, a=1)`      | naive (no profile)                                 |
| `Color.from_kelvin(temperature, a=1)`   | Helland approximation                              |

**Properties**

`alpha`, `rgb`, `rgba`, `hex`, `srgb`, `srgb_unclamped`, `linear_rgb`, `hsl`, `hsv`, `hwb`, `xyz`, `lab`, `lch`, `oklab`, `oklch`, `p3`, `p3_unclamped`, `cmyk`, `kelvin`, `luminance`, `name`.

**Methods**

| Method                                  | Returns         |
|-----------------------------------------|-----------------|
| `with_alpha(a)`                         | `Color`         |
| `lighten(amount)` / `darken(amount)`    | `Color`         |
| `saturate(amount)` / `desaturate(amount)` | `Color`       |
| `rotate(degrees)`                       | `Color`         |
| `complement()`                          | `Color`         |
| `grayscale()` / `invert()`              | `Color`         |
| `mix(other, t=0.5, space="oklab")`      | `Color`         |
| `contrast(other, method="wcag")`        | `float`         |
| `delta_e(other, method="2000")`         | `float`         |
| `simulate(kind, severity=1.0)`          | `Color`         |
| `daltonize(kind)`                       | `Color`         |
| `accessible_against(other, ratio=4.5)`  | `Color \| None` |
| `to_gamut(space="srgb")`                | `Color`         |
| `in_gamut(space="srgb")`                | `bool`          |
| `tints(count=5)` / `lighter(count=5)`   | `list[Color]`   |
| `shades(count=5)` / `darker(count=5)`   | `list[Color]`   |
| `tones(count=5)`                        | `list[Color]`   |
| `monochromatic(count=5)`                | `list[Color]`   |
| `analogous(count=3, spread=30)`         | `list[Color]`   |
| `complementary()`, `triadic()`, `tetradic()`, `split_complementary(spread=30)` | `list[Color]` |
| `material_palette()`                    | `dict[int, Color]` |
| `tailwind()`                            | `dict[int, Color]` |
| `css(fmt="hex")`                        | `str` — `"hex"`, `"rgb"`, `"hsl"`, `"hwb"`, `"lab"`, `"lch"`, `"oklab"`, `"oklch"` |

### Free functions

```python
from hexcraft import (
    parse, ColorParseError,                       # parsing
    mix, blend,                                   # mixing
    wcag_ratio, passes_wcag, apca_lc,             # contrast
    find_accessible_pair, best_text_color,        # accessibility
    delta_e, closest_from, closest_n_from,        # difference
    map_to_gamut, clip,                           # gamut
    simulate, daltonize,                          # CVD
    material_tonal_palette, tailwind_scale,       # tonal palettes
    complementary, analogous, triadic, tetradic,  # harmonies
    split_complementary, square,
    monochromatic, shades, tints, tones,
    scale, stops,                                 # gradients
    kelvin_to_rgb, rgb_to_kelvin,                 # temperature
    adapt, D65, D50, D55, D75, A,                 # chromatic adaptation
    viridis, magma, plasma, inferno, cividis,     # colormaps
    turbo, rdbu, brbg, spectral, tab10, set1,
    colormap, ALL_MAPS,
    SEQUENTIAL_MAPS, DIVERGING_MAPS, QUALITATIVE_MAPS,
)
```

### Submodules

| Module                | Purpose                                                          |
|-----------------------|------------------------------------------------------------------|
| `hexcraft.spaces`     | Low-level pure-function space conversions                        |
| `hexcraft.arrays`     | Numpy-vectorized conversions and metrics (numpy required)        |
| `hexcraft.image`      | Dominant color extraction, average color (numpy required)        |
| `hexcraft.cli`        | Console-script entry point                                       |
| `hexcraft.adapt`      | Chromatic adaptation, white-point constants                      |
| `hexcraft.colormaps`  | Colormap objects                                                 |
| `hexcraft.temperature` | Kelvin / CCT helpers                                            |
| `hexcraft.tonal`      | Material You and Tailwind tonal generators                       |
| `hexcraft.cvd`        | Color vision deficiency simulation and daltonization             |
| `hexcraft.accessibility` | High-level helpers built on contrast metrics                  |

---

## License

MIT.
