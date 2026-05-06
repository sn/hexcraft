"""Generate a complete design-system palette from one brand color.

Outputs both Material You (HCT-style 0-100 tonal) and Tailwind (50-950)
scales, side by side, the way a real design system would consume them.

Run: python examples/05_design_system.py
"""

from hexcraft import Color


def chip(c: Color, width: int = 6) -> str:
    r, g, b = c.rgb
    return f"\x1b[48;2;{r};{g};{b}m{' ' * width}\x1b[0m"


def main() -> None:
    brand = Color("#3b82f6")  # Tailwind blue-500-ish
    print(f"Brand color: {brand.hex}\n")

    material = brand.material_palette()
    print("Material You tonal palette (0-100):")
    for tone in sorted(material):
        print(f"  tone {tone:>3}  {chip(material[tone])}  {material[tone].hex}")
    print()

    tailwind = brand.tailwind()
    print("Tailwind 50-950 scale:")
    for stop in sorted(tailwind):
        print(f"  brand-{stop:>4}  {chip(tailwind[stop])}  {tailwind[stop].hex}")
    print()

    print("Side-by-side at common pairs:")
    pairs = [(50, 50), (100, 100), (300, 300), (500, 500), (700, 700), (900, 900)]
    print(f"  {'Material':>10}  {'  Tailwind':>16}")
    for m, t in pairs:
        m_c = material.get(m)
        t_c = tailwind.get(t)
        if m_c and t_c:
            print(f"  {m:>3} {chip(m_c, 5)} {m_c.hex}    {t:>3} {chip(t_c, 5)} {t_c.hex}")


if __name__ == "__main__":
    main()
