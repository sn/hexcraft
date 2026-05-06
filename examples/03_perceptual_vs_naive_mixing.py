"""Perceptual mixing matters: same gradient interpolated in five different spaces.

sRGB linear interpolation famously dips into muddy gray when crossing hues.
OKLab/OKLCh keep the gradient lightness-uniform and chromatic, which is why
modern design systems specify gradients in OKLab.

Run: python examples/03_perceptual_vs_naive_mixing.py
"""

from hexcraft import Color, scale


def bar(colors: list[Color], width: int = 4) -> str:
    out = []
    for c in colors:
        r, g, b = c.rgb
        out.append(f"\x1b[48;2;{r};{g};{b}m{' ' * width}\x1b[0m")
    return "".join(out)


def main() -> None:
    a, b = Color("blue"), Color("yellow")
    steps = 16

    print(f"Gradient from {a.hex} to {b.hex} in five interpolation spaces:\n")

    for space in ("srgb", "linear-rgb", "lab", "oklab", "oklch"):
        gradient = scale(a, b, steps=steps, space=space)
        print(f"  {space:>11}  {bar(gradient)}")

    print()
    print("Notice:")
    print("  - 'srgb' (the naive default) muddies through gray-green")
    print("  - 'linear-rgb' is brighter but pushes pure green at the midpoint")
    print("  - 'lab' / 'oklab' stay lightness-uniform and chromatic")
    print("  - 'oklch' takes the shortest hue arc - smoothest perceptually")


if __name__ == "__main__":
    main()
