"""Parse every CSS Color 4 syntax, named colors, and hex variants.

Run: python examples/02_parsing_anything.py
"""

from hexcraft import Color, ColorParseError


def swatch(c: Color, label: str) -> str:
    r, g, b = c.rgb
    return f"  \x1b[48;2;{r};{g};{b}m    \x1b[0m {c.hex}  {label}"


SAMPLES: list[str] = [
    # Hex variants
    "#f00",
    "#f008",
    "#ff0000",
    "#ff000080",
    # Functional notation
    "rgb(255, 0, 0)",
    "rgb(255 0 0)",
    "rgb(255 0 0 / 50%)",
    "rgba(255, 0, 0, 0.5)",
    "hsl(0, 100%, 50%)",
    "hsl(120deg 100% 50%)",
    "hsl(0.333turn 100% 50%)",
    "hwb(0 0% 0%)",
    # Modern perceptual spaces
    "lab(54 81 70)",
    "lch(54 100 41)",
    "oklab(0.628 0.225 0.126)",
    "oklch(0.628 0.258 29.234)",
    # Explicit color() function
    "color(srgb 1 0 0)",
    "color(srgb-linear 1 0 0)",
    "color(display-p3 1 0 0)",
    "color(xyz 0.412 0.213 0.019)",
    # Named colors (148 supported)
    "rebeccapurple",
    "papayawhip",
    "transparent",
]


def main() -> None:
    print("Parsing the same color 23 different ways:\n")
    for src in SAMPLES:
        try:
            c = Color(src)
            print(swatch(c, src))
        except ColorParseError as e:
            print(f"  ERROR {src}: {e}")

    print("\nInvalid inputs raise ColorParseError:")
    for bad in ["not-a-color", "#xyz", "rgb(1, 2)"]:
        try:
            Color(bad)
        except ColorParseError as e:
            print(f"  {bad!r:>20}  ->  {e}")


if __name__ == "__main__":
    main()
