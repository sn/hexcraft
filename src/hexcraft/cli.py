"""``hexcraft`` command-line interface.

Subcommands:
  inspect <color>                show all common representations
  convert <color> --to <space>   print one representation
  palette <color> [--type ...]   emit a palette (material, tailwind, triadic, ...)
  contrast <fg> <bg>             WCAG ratio + AA/AAA pass + APCA Lc
  closest <color> <c1> <c2> ...  find the closest match in a palette
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from . import (
    Color,
    ColorParseError,
    apca_lc,
    find_accessible_pair,
    material_tonal_palette,
    passes_wcag,
    tailwind_scale,
    wcag_ratio,
)
from .distance import closest_from
from .palettes import (
    analogous,
    complementary,
    monochromatic,
    shades,
    split_complementary,
    tetradic,
    tints,
    triadic,
)


def _bar(c: Color, width: int = 6) -> str:
    """Render a colored block using ANSI 24-bit color, if the terminal supports it."""
    if not sys.stdout.isatty():
        return c.hex
    r, g, b = c.rgb
    return f"\033[48;2;{r};{g};{b}m{' ' * width}\033[0m {c.hex}"


def _cmd_inspect(args: argparse.Namespace) -> int:
    c = Color(args.color)
    bar = _bar(c)
    L_lab, A, B = c.lab
    L_ok, c_ok, h_ok = c.oklch
    h, s, l = c.hsl
    print(f"{bar}")
    print(f"  hex      {c.hex}")
    print(f"  rgb      rgb({c.rgb[0]}, {c.rgb[1]}, {c.rgb[2]})")
    print(f"  hsl      hsl({h:.1f} {s * 100:.1f}% {l * 100:.1f}%)")
    print(f"  lab      lab({L_lab:.1f} {A:.1f} {B:.1f})")
    print(f"  oklch    oklch({L_ok:.3f} {c_ok:.3f} {h_ok:.1f})")
    print(f"  cmyk     {' '.join(f'{v * 100:.1f}%' for v in c.cmyk)}")
    print(f"  luma     {c.luminance:.4f}")
    if c.kelvin is not None:
        print(f"  kelvin   ~{c.kelvin:.0f} K")
    print(f"  name     {c.name}")
    print(f"  in sRGB  {c.in_gamut()}")
    return 0


def _cmd_convert(args: argparse.Namespace) -> int:
    print(Color(args.color).css(args.to))
    return 0


def _cmd_palette(args: argparse.Namespace) -> int:
    c = Color(args.color)
    type_ = args.type
    if type_ == "material":
        items = material_tonal_palette(c).items()
    elif type_ == "tailwind":
        items = tailwind_scale(c).items()
    elif type_ == "complementary":
        items = enumerate(complementary(c))
    elif type_ == "triadic":
        items = enumerate(triadic(c))
    elif type_ == "tetradic":
        items = enumerate(tetradic(c))
    elif type_ == "split":
        items = enumerate(split_complementary(c))
    elif type_ == "analogous":
        items = enumerate(analogous(c, count=args.count))
    elif type_ == "monochromatic":
        items = enumerate(monochromatic(c, count=args.count))
    elif type_ == "tints":
        items = enumerate(tints(c, count=args.count))
    elif type_ == "shades":
        items = enumerate(shades(c, count=args.count))
    else:
        print(f"unknown palette type: {type_}", file=sys.stderr)
        return 2
    for key, col in items:
        print(f"  {key:>6}  {_bar(col)}")
    return 0


def _cmd_contrast(args: argparse.Namespace) -> int:
    fg = Color(args.fg)
    bg = Color(args.bg)
    ratio = wcag_ratio(fg, bg)
    apca = apca_lc(fg, bg)
    print(f"  fg          {_bar(fg)}")
    print(f"  bg          {_bar(bg)}")
    print(f"  WCAG ratio  {ratio:.2f}:1")
    print(f"  AA          {'PASS' if passes_wcag(fg, bg, level='AA') else 'FAIL'}  "
          f"(large: {'PASS' if passes_wcag(fg, bg, level='AA', large=True) else 'FAIL'})")
    print(f"  AAA         {'PASS' if passes_wcag(fg, bg, level='AAA') else 'FAIL'}  "
          f"(large: {'PASS' if passes_wcag(fg, bg, level='AAA', large=True) else 'FAIL'})")
    print(f"  APCA Lc     {apca:+.1f}")
    if not passes_wcag(fg, bg, level="AA"):
        suggestion = find_accessible_pair(fg, bg, ratio=4.5)
        if suggestion is not None:
            print(f"  → try fg {_bar(suggestion)} for AA")
    return 0


def _cmd_closest(args: argparse.Namespace) -> int:
    target = Color(args.color)
    palette = [Color(s) for s in args.palette]
    match = closest_from(target, palette, method=args.method)
    print(f"  target  {_bar(target)}")
    print(f"  match   {_bar(match)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level ``argparse`` parser for the ``hexcraft`` CLI."""
    p = argparse.ArgumentParser(prog="hexcraft", description="Swiss-army color tool")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("inspect", help="show all representations of a color")
    sp.add_argument("color")
    sp.set_defaults(func=_cmd_inspect)

    sp = sub.add_parser("convert", help="render a color as a CSS string")
    sp.add_argument("color")
    sp.add_argument("--to", default="hex",
                    choices=["hex", "rgb", "hsl", "hwb", "lab", "lch", "oklab", "oklch"])
    sp.set_defaults(func=_cmd_convert)

    sp = sub.add_parser("palette", help="generate a palette from a color")
    sp.add_argument("color")
    sp.add_argument(
        "--type", default="material",
        choices=["material", "tailwind", "complementary", "triadic", "tetradic",
                 "split", "analogous", "monochromatic", "tints", "shades"],
    )
    sp.add_argument("--count", type=int, default=5)
    sp.set_defaults(func=_cmd_palette)

    sp = sub.add_parser("contrast", help="WCAG/APCA contrast between two colors")
    sp.add_argument("fg")
    sp.add_argument("bg")
    sp.set_defaults(func=_cmd_contrast)

    sp = sub.add_parser("closest", help="find the closest color in a palette")
    sp.add_argument("color")
    sp.add_argument("palette", nargs="+", help="palette colors (parsed individually)")
    sp.add_argument("--method", default="2000",
                    choices=["76", "94", "2000", "cmc", "ok"])
    sp.set_defaults(func=_cmd_closest)

    return p


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ColorParseError as e:
        print(f"hexcraft: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
