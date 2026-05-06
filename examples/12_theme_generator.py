"""Generate a complete light + dark theme from a single brand color.

This is a recipe for design-system tokens: from one input color we derive
neutral steps, semantic colors (success/warning/error/info), and matched
light/dark surfaces with WCAG-checked text pairings.

Run: python examples/12_theme_generator.py
"""

from hexcraft import (
    Color,
    best_text_color,
    find_accessible_pair,
    wcag_ratio,
)


def chip(c: Color, width: int = 5) -> str:
    r, g, b = c.rgb
    return f"\x1b[48;2;{r};{g};{b}m{' ' * width}\x1b[0m"


def emit_token(name: str, c: Color, on: Color | None = None) -> None:
    line = f"  {name:<24}  {chip(c)} {c.hex}"
    if on is not None:
        ratio = wcag_ratio(on, c)
        line += f"   text {chip(on)} {on.hex}  ({ratio:.2f}:1)"
    print(line)


def build_theme(brand: Color, *, dark: bool) -> dict[str, Color]:
    """Build a theme dict using the brand's hue family but neutral surfaces."""
    _, _, hue = brand.oklch

    # Surface ramp: cool-tinted neutrals carrying a faint trace of the brand hue.
    if dark:
        bg = Color.from_oklch(0.18, 0.012, hue)
        surface = Color.from_oklch(0.22, 0.012, hue)
        elevated = Color.from_oklch(0.26, 0.014, hue)
        text = Color.from_oklch(0.96, 0.005, hue)
        muted = Color.from_oklch(0.72, 0.012, hue)
    else:
        bg = Color.from_oklch(0.99, 0.005, hue)
        surface = Color.from_oklch(0.96, 0.008, hue)
        elevated = Color.from_oklch(0.93, 0.012, hue)
        text = Color.from_oklch(0.18, 0.012, hue)
        muted = Color.from_oklch(0.45, 0.020, hue)

    primary = brand
    primary_hover = brand.lighten(0.05) if dark else brand.darken(0.05)

    return {
        "bg": bg, "surface": surface, "elevated": elevated,
        "text": text, "muted": muted,
        "primary": primary, "primary-hover": primary_hover,
        "success": Color("#10b981"), "warning": Color("#f59e0b"),
        "error": Color("#ef4444"), "info": Color("#3b82f6"),
    }


def report(name: str, theme: dict[str, Color]) -> None:
    print(f"\n{name}:")
    bg = theme["bg"]

    for token, color in theme.items():
        on = best_text_color(color, palette=[theme["text"], Color("#ffffff"), Color("#000000")])
        emit_token(token, color, on)

    primary = theme["primary"]
    if wcag_ratio(primary, bg) < 4.5:
        fixed = find_accessible_pair(primary, bg, ratio=4.5)
        if fixed:
            print("\n  primary is unreadable as text on bg - shift it for AA?")
            print(f"    suggested: {chip(fixed)} {fixed.hex}  "
                  f"({wcag_ratio(fixed, bg):.2f}:1 vs {wcag_ratio(primary, bg):.2f}:1)")


def main() -> None:
    brand = Color("#3b82f6")
    print(f"Brand color: {chip(brand)} {brand.hex}")

    report("Light theme", build_theme(brand, dark=False))
    report("Dark theme", build_theme(brand, dark=True))


if __name__ == "__main__":
    main()
