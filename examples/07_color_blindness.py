"""See your palette through color-blind eyes, then fix it.

Simulates protanopia / deuteranopia / tritanopia for a small UI palette and
shows what daltonization (Fidaner-style error redistribution) does to keep
the colors distinguishable.

Run: python examples/07_color_blindness.py
"""

from hexcraft import Color, daltonize, simulate


def chip(c: Color, width: int = 6) -> str:
    r, g, b = c.rgb
    return f"\x1b[48;2;{r};{g};{b}m{' ' * width}\x1b[0m"


def main() -> None:
    palette = {
        "success": Color("#10b981"),
        "warning": Color("#f59e0b"),
        "error":   Color("#ef4444"),
        "info":    Color("#3b82f6"),
        "neutral": Color("#6b7280"),
    }

    cvd_kinds = ("protanopia", "deuteranopia", "tritanopia")

    print("Original palette:")
    for name, c in palette.items():
        print(f"  {name:<8} {chip(c)} {c.hex}")
    print()

    print("How each color appears to viewers with each CVD type:\n")
    header = f"  {'role':<8} {'normal':<14}"
    for k in cvd_kinds:
        header += f"{k:<14}"
    print(header)

    for name, c in palette.items():
        row = f"  {name:<8} {chip(c)} {c.hex}  "
        for k in cvd_kinds:
            sim = simulate(c, k)
            row += f"{chip(sim)} {sim.hex}  "
        print(row)

    print()
    print("Daltonized variants - same colors, redistributed so a CVD viewer")
    print("can still tell them apart (red shifts toward pink/orange, etc.):\n")

    print(f"  {'role':<8} {'original':<14} {'protan-friendly':<20} "
          f"{'deutan-friendly':<20} {'tritan-friendly':<20}")
    for name, c in palette.items():
        d_p = daltonize(c, "protanopia")
        d_d = daltonize(c, "deuteranopia")
        d_t = daltonize(c, "tritanopia")
        print(f"  {name:<8} {chip(c)} {c.hex}  "
              f"{chip(d_p)} {d_p.hex}      "
              f"{chip(d_d)} {d_d.hex}      "
              f"{chip(d_t)} {d_t.hex}")


if __name__ == "__main__":
    main()
