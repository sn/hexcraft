"""Generate every classic color harmony from a single brand color.

Run: python examples/04_palette_harmonies.py
"""

from hexcraft import Color


def show(label: str, colors: list[Color]) -> None:
    chips = []
    for c in colors:
        r, g, b = c.rgb
        chips.append(f"\x1b[48;2;{r};{g};{b}m  {c.hex}  \x1b[0m")
    print(f"  {label:<20} {' '.join(chips)}")


def main() -> None:
    base = Color("#3498db")  # a classic web blue
    print(f"Base color: {base.hex}\n")

    show("complementary", base.complementary())
    show("analogous (5)", base.analogous(count=5, spread=20))
    show("triadic", base.triadic())
    show("tetradic", base.tetradic())
    show("split-complement", base.split_complementary())
    print()

    print("Lightness ramps (preserve hue, vary L):")
    show("monochromatic", base.monochromatic(count=7))
    show("tints (toward white)", base.tints(7))
    show("shades (toward black)", base.shades(7))
    show("tones (toward gray)", base.tones(7))


if __name__ == "__main__":
    main()
