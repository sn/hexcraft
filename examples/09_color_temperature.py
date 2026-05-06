"""Visualize blackbody color temperature across the camera/lighting range.

Every Kelvin value maps to a sRGB color via Tanner Helland's piecewise
approximation, and McCamy's CCT formula gives a (lossy) round-trip back.

Run: python examples/09_color_temperature.py
"""

from hexcraft import Color


def chip(c: Color, width: int = 8) -> str:
    r, g, b = c.rgb
    return f"\x1b[48;2;{r};{g};{b}m{' ' * width}\x1b[0m"


COMMON_TEMPS: list[tuple[int, str]] = [
    (1000, "candle flame"),
    (1700, "match flame"),
    (2400, "tungsten standard"),
    (2700, "warm-white LED / soft tungsten"),
    (3200, "studio tungsten"),
    (3500, "warm fluorescent"),
    (4000, "cool white LED"),
    (5000, "midday sun (D50)"),
    (5500, "noon daylight"),
    (6500, "overcast daylight (D65)"),
    (7500, "blue sky"),
    (10000, "clear blue polar sky"),
    (15000, "deep sky"),
    (20000, "ultra-cool blue"),
]


def main() -> None:
    print("Common lighting temperatures:\n")
    print(f"  {'Kelvin':<8} swatch   hex      CCT round-trip   description")
    for k, label in COMMON_TEMPS:
        c = Color.from_kelvin(k)
        cct = c.kelvin
        cct_str = f"~{cct:.0f} K" if cct is not None else "N/A"
        print(f"  {k:>5} K  {chip(c)} {c.hex}  {cct_str:<14}   {label}")

    print("\nA continuous warm-to-cool gradient (1500 K to 15000 K):\n")
    bar = []
    for i in range(60):
        k = int(1500 + (15000 - 1500) * i / 59)
        c = Color.from_kelvin(k)
        r, g, b = c.rgb
        bar.append(f"\x1b[48;2;{r};{g};{b}m \x1b[0m")
    print("  " + "".join(bar))
    print(f"  {'1500 K':<25} {'6500 K (D65)':^10} {'15000 K':>20}")


if __name__ == "__main__":
    main()
