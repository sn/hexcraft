"""Generate the README images in ``assets/`` from hexcraft itself.

Every color in these SVGs is computed by the library, so re-running this after
a behavior change keeps the docs honest. Run from the repository root::

    python scripts/readme_assets.py

Images use a transparent background and mid-gray (#888) text so they read on
both GitHub's light and dark themes.
"""

from __future__ import annotations

import contextlib
import io
import re
from html import escape
from pathlib import Path
from typing import Literal
from unittest import mock

from hexcraft import (
    Color,
    best_text_color,
    clip,
    closest_n_from,
    delta_e,
    monochromatic,
    shades,
    tints,
    tones,
)
from hexcraft import cli as _cli
from hexcraft.colormaps import magma, turbo, viridis

ASSETS = Path(__file__).resolve().parent.parent / "assets"
MUTED = "#888888"
SANS = "sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
BASE = Color("#3498db")


# ── SVG primitives (same conventions as the existing assets) ──────────────


def _svg(width: float, height: float, body: list[str], *, preserve_space: bool = False) -> str:
    space = ' xml:space="preserve" style="white-space:pre"' if preserve_space else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}" '
        f'width="{width:g}" height="{height:g}" role="img"{space}>\n'
        + "\n".join(body)
        + "\n</svg>\n"
    )


def _text(x: float, y: float, s: str, *, size: int = 13, weight: int = 400, fill: str = MUTED,
          anchor: str = "start", family: str = SANS) -> str:
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="{family}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>'
    )


def _rect(x: float, y: float, w: float, h: float, fill: str, *, rx: float = 10,
          stroke: str = MUTED, stroke_opacity: float = 0.25, stroke_width: float = 1) -> str:
    return (
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx:g}" ry="{rx:g}" '
        f'fill="{fill}" stroke="{stroke}" stroke-opacity="{stroke_opacity:g}" stroke-width="{stroke_width:g}"/>'
    )


def _ink(c: Color) -> str:
    """Black or white, whichever reads better on ``c``."""
    return best_text_color(c).hex


def _title(s: str) -> str:
    return _text(24, 24, s, weight=600)


# ── Images ────────────────────────────────────────────────────────────────


def parsing() -> str:
    """Every CSS notation hexcraft writes, parsed back by ``Color()``."""
    c = Color("tomato")
    r, g, b = c.p3
    fmts: tuple[Literal["rgb", "hsl", "hwb", "lab", "lch", "oklab", "oklch"], ...] = (
        "rgb", "hsl", "hwb", "lab", "lch", "oklab", "oklch",
    )
    notations = ["tomato", c.hex] + [c.css(f) for f in fmts]
    notations.append(f"color(display-p3 {r:.4f} {g:.4f} {b:.4f})")
    body = [_title("One color, every notation - each string parsed by Color()")]
    y = 44.0
    for s in notations:
        parsed = Color(s)
        body.append(_text(24, y + 19, s, family=MONO))
        body.append(_rect(452, y, 64, 28, parsed.hex, rx=7))
        body.append(_text(530, y + 19, parsed.hex, family=MONO))
        y += 36
    return _svg(720, y + 12, body)


def manipulation() -> str:
    """One base color through each manipulation method."""
    steps = [
        ("base", BASE),
        ("lighten(0.15)", BASE.lighten(0.15)),
        ("darken(0.15)", BASE.darken(0.15)),
        ("saturate(0.1)", BASE.saturate(0.1)),
        ("desaturate(0.1)", BASE.desaturate(0.1)),
        ("rotate(60)", BASE.rotate(60)),
        ("grayscale()", BASE.grayscale()),
        ("invert()", BASE.invert()),
    ]
    gap = 12.0
    w = (880 - 48 - gap * (len(steps) - 1)) / len(steps)
    body = [_title(f"Manipulation methods on {BASE.hex} - each returns a new Color")]
    for i, (label, c) in enumerate(steps):
        x = 24 + i * (w + gap)
        body.append(_rect(x, 42, w, 72, c.hex))
        body.append(_text(x + w / 2, 82, c.hex, size=10, fill=_ink(c), anchor="middle"))
        body.append(_text(x + w / 2, 134, label, size=11, anchor="middle", family=MONO))
    return _svg(880, 152, body)


def scales() -> str:
    """tints / shades / tones / monochromatic ramps, in the harmonies layout."""
    rows = [
        ("tints", tints(BASE, count=7)),
        ("shades", shades(BASE, count=7)),
        ("tones", tones(BASE, count=7)),
        ("monochromatic", monochromatic(BASE, count=7)),
    ]
    body = [_title(f"Tints, shades, tones and monochromatic ramps from {BASE.hex}")]
    y = 42.0
    for label, colors in rows:
        body.append(_text(176, y + 32.55, label, anchor="end"))
        for i, c in enumerate(colors):
            body.append(_rect(192 + i * 68, y, 56, 56, c.hex))
        y += 74
    return _svg(720, y + 4, body)


def gamut() -> str:
    """Per-channel clipping vs chroma reduction for out-of-gamut OKLCh colors."""
    L, C = 0.7, 0.3
    hues = [i * 15.0 for i in range(24)]
    wide = [Color.from_oklch(L, C, h) for h in hues]
    rows = [("clip()", [clip(c) for c in wide]), ("to_gamut()", [c.to_gamut() for c in wide])]

    def hue_error(results: list[Color]) -> float:
        return max(abs(((r.oklch[2] - h + 540.0) % 360.0) - 180.0) for r, h in zip(results, hues, strict=True))

    gap = 4.0
    x0 = 128.0
    w = (880 - 24 - x0 - gap * (len(hues) - 1)) / len(hues)
    body = [_title(f"Out-of-gamut oklch({L} {C} h) brought into sRGB, hue 0-345°")]
    y = 42.0
    for label, colors in rows:
        body.append(_text(x0 - 14, y + 26.55, label, anchor="end", family=MONO))
        for i, c in enumerate(colors):
            body.append(_rect(x0 + i * (w + gap), y, w, 44, c.hex, rx=5))
        y += 56
    body.append(_text(
        x0, y + 14,
        f"clip() drifts hue by up to {hue_error(rows[0][1]):.0f}°; "
        f"to_gamut() keeps hue within {hue_error(rows[1][1]):.1f}° by reducing chroma instead",
        size=12,
    ))
    return _svg(880, y + 30, body)


def closest() -> str:
    """closest_n_from() ranking a palette by CIEDE2000."""
    target = Color("#ee5544")
    brand = [Color(s) for s in ("#3b82f6", "#10b981", "#ef4444", "#f59e0b")]
    ranked = closest_n_from(target, brand, n=len(brand))
    body = [_title(f"closest_n_from({target.hex}, brand) - ranked by CIEDE2000")]
    body.append(_rect(24, 44, 96, 96, target.hex, rx=12))
    body.append(_text(72, 97, "target", size=11, fill=_ink(target), anchor="middle"))
    body.append(_text(72, 160, target.hex, size=11, anchor="middle", family=MONO))
    body.append(_text(152, 97, "→", size=20, anchor="middle"))
    for i, c in enumerate(ranked):
        x = 184 + i * 132
        best = i == 0
        body.append(_rect(x, 44, 96, 96, c.hex, rx=12, stroke_opacity=1 if best else 0.25,
                          stroke_width=3 if best else 1))
        body.append(_text(x + 48, 97, f"ΔE {delta_e(target, c):.1f}", size=12, weight=600,
                          fill=_ink(c), anchor="middle"))
        body.append(_text(x + 48, 160, c.hex, size=11, anchor="middle", family=MONO))
        if best:
            body.append(_text(x + 48, 178, "closest", size=11, weight=600, anchor="middle"))
    return _svg(720, 192, body)


def cli() -> str:
    """Terminal rendering of the CLI, with the ANSI color blocks drawn as swatches."""
    marker = "\x00"
    lines: list[str] = []
    # Swap the ANSI color block for a marker that is drawn as a swatch below.
    with mock.patch.object(_cli, "_bar", lambda c, width=6: f"{marker}{c.hex}"):
        for argv in (["inspect", "#3498db"], ["contrast", "#888", "white"]):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                _cli.main(argv)
            shown = " ".join(a if a.isalnum() else f'"{a}"' for a in argv)
            lines += [f"$ hexcraft {shown}", *buf.getvalue().rstrip("\n").split("\n"), ""]
    lines.pop()

    char_w, line_h, pad = 7.8, 20.0, 20.0
    width = 720.0
    height = 44 + len(lines) * line_h + pad
    body = [
        f'<rect x="0" y="0" width="{width:g}" height="{height:g}" rx="12" ry="12" fill="#1e1e1e"/>',
        '<circle cx="20" cy="18" r="6" fill="#ff5f56"/>',
        '<circle cx="40" cy="18" r="6" fill="#ffbd2e"/>',
        '<circle cx="60" cy="18" r="6" fill="#27c93f"/>',
    ]
    for n, line in enumerate(lines):
        y = 50 + n * line_h
        fill = "#9cdcfe" if line.startswith("$ ") else "#d4d4d4"
        x = pad
        for part in re.split(f"({marker}#[0-9a-f]{{6}})", line):
            if not part:
                continue
            if part.startswith(marker):
                hexcode = part[1:]
                body.append(f'<rect x="{x:.2f}" y="{y - 12:.2f}" width="{6 * char_w:.2f}" '
                            f'height="15" fill="{hexcode}"/>')
                x += 7 * char_w
                part = hexcode
            body.append(_text(x, y, part, fill=fill, family=MONO))
            x += len(part) * char_w
    return _svg(width, height, body, preserve_space=True)


def tonal_scales() -> str:
    """Material You and Tailwind scales (layout matches the original asset)."""
    body = [_title(f"Tonal scales from {BASE.hex}")]
    for label, palette, y in (("Material You", BASE.material_palette(), 42.0),
                              ("Tailwind", BASE.tailwind(), 118.0)):
        body.append(_text(106, y + 31.55, label, weight=600, anchor="end"))
        w = (856 - 120 - 4 * (len(palette) - 1)) / len(palette)
        for i, (stop, c) in enumerate(palette.items()):
            x = 120 + i * (w + 4)
            body.append(_rect(x, y, w, 54, c.hex, rx=7))
            body.append(_text(x + w / 2, y + 30.5, str(stop), size=10, fill=_ink(c), anchor="middle"))
    return _svg(880, 194, body)


# ── Refresh colormap gradients inside hand-laid-out assets ────────────────

_GRADIENT_MAPS = {
    "colormaps.svg": {"g8": viridis, "g9": magma, "g13": turbo},
    "showcase.svg": {"g2": viridis, "g3": magma, "g4": turbo},
}


def refresh_gradients(name: str) -> str:
    """Recompute stop colors of the listed gradients, keeping every offset and layout."""
    svg = (ASSETS / name).read_text()
    for gid, cmap in _GRADIENT_MAPS[name].items():
        pattern = re.compile(rf'(<linearGradient id="{gid}"[^>]*>)(.*?)(</linearGradient>)', re.S)
        m = pattern.search(svg)
        if m is None:
            raise ValueError(f"{name}: gradient {gid} not found")
        stops = re.sub(
            r'<stop offset="([0-9.]+)%" stop-color="#[0-9a-f]{6}"/>',
            lambda s, cmap=cmap: f'<stop offset="{s.group(1)}%" stop-color="{cmap(float(s.group(1)) / 100).hex}"/>',
            m.group(2),
        )
        svg = svg[: m.start(2)] + stops + svg[m.end(2):]
    return svg


def main() -> None:
    generated = {
        "parsing.svg": parsing(),
        "manipulation.svg": manipulation(),
        "scales.svg": scales(),
        "gamut.svg": gamut(),
        "closest.svg": closest(),
        "cli.svg": cli(),
        "tonal-scales.svg": tonal_scales(),
        "colormaps.svg": refresh_gradients("colormaps.svg"),
        "showcase.svg": refresh_gradients("showcase.svg"),
    }
    for name, svg in generated.items():
        (ASSETS / name).write_text(svg)
        print(f"wrote assets/{name}")


if __name__ == "__main__":
    main()
