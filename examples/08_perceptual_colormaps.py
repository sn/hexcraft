"""Sample every bundled perceptual colormap as a row of swatches.

Useful for picking a colormap that matches your data's character:
  - sequential: viridis/magma/plasma/inferno/cividis
  - rainbow:    turbo (replaces matplotlib's old jet)
  - diverging:  RdBu, BrBG, Spectral
  - qualitative: tab10, Set1

Run: python examples/08_perceptual_colormaps.py
"""

from hexcraft import (
    ALL_MAPS,
    DIVERGING_MAPS,
    QUALITATIVE_MAPS,
    SEQUENTIAL_MAPS,
    Color,
)


def bar(colors: list[Color], width: int = 2) -> str:
    out = []
    for c in colors:
        r, g, b = c.rgb
        out.append(f"\x1b[48;2;{r};{g};{b}m{' ' * width}\x1b[0m")
    return "".join(out)


def section(title: str, names: list[str], steps: int) -> None:
    print(f"\n{title}:")
    for name in names:
        cmap = ALL_MAPS[name]
        sample = cmap.colors(steps)
        print(f"  {name:<10} {bar(sample)}")


def main() -> None:
    section("Sequential (luminance-monotone)", list(SEQUENTIAL_MAPS), steps=32)
    section("Diverging (anchored midpoint)", list(DIVERGING_MAPS), steps=32)
    section("Qualitative (categorical)", list(QUALITATIVE_MAPS), steps=10)

    print("\nUsing a colormap to encode data:")
    values = [0.05, 0.2, 0.4, 0.5, 0.6, 0.8, 0.95]
    print("  data   value -> color")
    for v in values:
        c = ALL_MAPS["viridis"](v)
        r, g, b = c.rgb
        print(f"  {v:>5.2f}  -> \x1b[48;2;{r};{g};{b}m      \x1b[0m {c.hex}")


if __name__ == "__main__":
    main()
