# Examples

Twelve runnable scripts that show off everything `hexcraft` can do. Each
prints colored output to the terminal using ANSI 24-bit color, so the
gradients, palettes, and contrast comparisons are visible at a glance.

Run any example directly:

```bash
pip install -e ".[numpy]"   # `[numpy]` only needed for example 11
python examples/01_quickstart.py
```

| #   | File                                     | What it shows                                                                 |
| --- | ---------------------------------------- | ----------------------------------------------------------------------------- |
| 01  | `01_quickstart.py`                       | The 60-second tour - parse, convert, manipulate, contrast, mix, format        |
| 02  | `02_parsing_anything.py`                 | All 23 input syntaxes (CSS Color 4, hex variants, named colors, units)        |
| 03  | `03_perceptual_vs_naive_mixing.py`       | The same gradient interpolated in five spaces - sRGB muddies, OKLab doesn't   |
| 04  | `04_palette_harmonies.py`                | Every classic harmony (complementary, triadic, tetradic, analogous) + ramps  |
| 05  | `05_design_system.py`                    | Full Material You + Tailwind 50-950 scales from one brand color               |
| 06  | `06_accessibility_audit.py`              | Audit a UI for WCAG/APCA, with auto-suggested fixes when something fails       |
| 07  | `07_color_blindness.py`                  | Simulate protanopia / deuteranopia / tritanopia, then daltonize the palette   |
| 08  | `08_perceptual_colormaps.py`             | All 11 bundled colormaps (viridis, magma, RdBu, tab10, ...) sampled side-by-side |
| 09  | `09_color_temperature.py`                | Common Kelvin temperatures (1000-20000 K) with their sRGB approximations      |
| 10  | `10_brand_color_match.py`                | Find the closest brand color for an arbitrary input via deltaE                |
| 11  | `11_image_palette.py` *(numpy)*           | Synthesize a painted image and extract its dominant colors via k-means        |
| 12  | `12_theme_generator.py`                  | Generate a full light + dark theme (surfaces, text, semantic) from one brand  |

## Tips for terminal viewing

- These all use ANSI true-color escapes (`\x1b[48;2;R;G;B`). Any modern
  terminal supports them: iTerm2, Terminal.app, GNOME Terminal, Windows
  Terminal, Alacritty, etc.
- If the swatches look like garbled text, your terminal lacks 24-bit color
  support; the hex codes alongside still convey the result.
- Output is always plain text - pipe through `tee`, redirect to a file,
  or grep freely.

## Using these as building blocks

Each script is self-contained and intentionally small. Copy any of them
into your own project as a starting point - the imports map directly to
the public API documented in the main `README.md`.
