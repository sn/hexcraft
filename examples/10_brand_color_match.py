"""Find the closest brand color for any input - useful for normalizing
user-submitted hex values, mapping screenshots to a corporate palette,
or building a "did you mean...?" hint in a design tool.

Run: python examples/10_brand_color_match.py
"""

from hexcraft import Color, closest_from, closest_n_from, delta_e


def chip(c: Color, width: int = 4) -> str:
    r, g, b = c.rgb
    return f"\x1b[48;2;{r};{g};{b}m{' ' * width}\x1b[0m"


# A small "approved brand palette".
BRAND = [
    Color("#1d4ed8"),  # primary blue
    Color("#10b981"),  # success green
    Color("#ef4444"),  # error red
    Color("#f59e0b"),  # warning amber
    Color("#8b5cf6"),  # accent purple
    Color("#0f172a"),  # ink
    Color("#f8fafc"),  # paper
]


def main() -> None:
    print("Brand palette:")
    for c in BRAND:
        print(f"  {chip(c)} {c.hex}")
    print()

    targets = [
        ("user typed '#ee5544'",     Color("#ee5544")),
        ("screenshot pixel #2962d1", Color("#2962d1")),
        ("logo color from PNG",       Color("#0d9488")),
        ("midnight from CSS",         Color("#020617")),
    ]

    print("Single best match per target:")
    for label, t in targets:
        best = closest_from(t, BRAND)
        de = delta_e(t, best, method="2000")
        print(f"  {chip(t)} {t.hex} ({label:<30}) -> "
              f"{chip(best)} {best.hex}  deltaE2000={de:.2f}")
    print()

    print(f"Top-3 candidates for {targets[0][1].hex} (using deltaE OK for speed):")
    top3 = closest_n_from(targets[0][1], BRAND, n=3, method="ok")
    for rank, c in enumerate(top3, 1):
        de = delta_e(targets[0][1], c, method="ok")
        print(f"  #{rank}  {chip(c)} {c.hex}  deltaE_OK={de:.3f}")

    print("\nMethod sensitivity (same target, four metrics):")
    t = Color("#ee5544")
    for method in ("76", "94", "2000", "ok"):
        m = closest_from(t, BRAND, method=method)
        de = delta_e(t, m, method=method)
        print(f"  method={method:<5}  best={chip(m)} {m.hex}  deltaE={de:.3f}")


if __name__ == "__main__":
    main()
