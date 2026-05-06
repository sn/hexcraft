"""Quickstart: parse, convert, manipulate, format - the 60-second tour.

Run: python examples/01_quickstart.py
"""

from hexcraft import Color


def swatch(c: Color, label: str = "", width: int = 4) -> str:
    r, g, b = c.rgb
    return f"\x1b[48;2;{r};{g};{b}m{' ' * width}\x1b[0m {c.hex}" + (f"  {label}" if label else "")


def main() -> None:
    # Parse anything CSS Color 4 understands.
    c = Color("oklch(0.7 0.15 250)")

    print("Source color:")
    print(" ", swatch(c, "from oklch(0.7 0.15 250)"))
    print()

    print("Same color in every space:")
    print(f"  hex      {c.hex}")
    print(f"  rgb      {c.rgb}")
    print(f"  hsl      {tuple(round(x, 2) for x in c.hsl)}")
    print(f"  lab      {tuple(round(x, 2) for x in c.lab)}")
    print(f"  oklch    {tuple(round(x, 3) for x in c.oklch)}")
    print(f"  cmyk     {tuple(round(x, 2) for x in c.cmyk)}")
    print(f"  closest CSS name  {c.name!r}")
    print()

    print("Manipulations (all immutable - each returns a new Color):")
    print(" ", swatch(c.lighten(0.1), "lighten(0.1)"))
    print(" ", swatch(c.darken(0.1), "darken(0.1)"))
    print(" ", swatch(c.saturate(0.2), "saturate(0.2)"))
    print(" ", swatch(c.desaturate(0.2), "desaturate(0.2)"))
    print(" ", swatch(c.rotate(60), "rotate(60)"))
    print(" ", swatch(c.complement(), "complement()"))
    print(" ", swatch(c.grayscale(), "grayscale()"))
    print()

    print("Mixing two colors in OKLab (perceptually smooth):")
    red, blue = Color("red"), Color("blue")
    for t in (0.0, 0.25, 0.5, 0.75, 1.0):
        print(f"  t={t}: {swatch(red.mix(blue, t))}")
    print()

    print("Accessibility:")
    print(f"  contrast vs white  {round(c.contrast(Color('white')), 2)}:1")
    print(f"  contrast vs black  {round(c.contrast(Color('black')), 2)}:1")
    print(f"  APCA Lc on white   {round(c.contrast(Color('white'), method='apca'), 1):+.1f}")


if __name__ == "__main__":
    main()
