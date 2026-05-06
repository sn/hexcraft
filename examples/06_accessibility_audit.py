"""Audit a design's color pairs for WCAG / APCA compliance and auto-suggest fixes.

Models a typical UI: text on backgrounds in three states. For every failing
combination, hexcraft proposes the closest in-gamut variant that does pass.

Run: python examples/06_accessibility_audit.py
"""

from hexcraft import Color, apca_lc, find_accessible_pair, passes_wcag, wcag_ratio


def chip(c: Color, width: int = 4) -> str:
    r, g, b = c.rgb
    return f"\x1b[48;2;{r};{g};{b}m{' ' * width}\x1b[0m"


def audit(role: str, fg: Color, bg: Color) -> None:
    ratio = wcag_ratio(fg, bg)
    apca = apca_lc(fg, bg)
    aa = passes_wcag(fg, bg, level="AA")
    aaa = passes_wcag(fg, bg, level="AAA")

    status = "PASS AA" if aa else "FAIL"
    aaa_status = "PASS AAA" if aaa else "fail AAA"

    line = (
        f"  {role:<24} fg {chip(fg)} {fg.hex}  on  bg {chip(bg)} {bg.hex}  "
        f"WCAG {ratio:>5.2f}:1  APCA {apca:+6.1f}  [{status}, {aaa_status}]"
    )
    print(line)

    if not aa:
        suggested = find_accessible_pair(fg, bg, ratio=4.5)
        if suggested:
            new_ratio = wcag_ratio(suggested, bg)
            print(f"    -> suggested fg {chip(suggested)} {suggested.hex}  "
                  f"WCAG {new_ratio:.2f}:1")


def main() -> None:
    print("Auditing a hypothetical button system on a light background:\n")

    bg_light = Color("#ffffff")
    bg_card = Color("#f3f4f6")

    pairs = [
        ("primary text", Color("#111827"), bg_light),
        ("secondary text", Color("#6b7280"), bg_light),
        ("link", Color("#3b82f6"), bg_light),
        ("muted (often fails)", Color("#9ca3af"), bg_light),
        ("success badge", Color("#10b981"), bg_light),
        ("error text", Color("#ef4444"), bg_light),
        ("light text on card", Color("#a1a1aa"), bg_card),
    ]

    for role, fg, bg in pairs:
        audit(role, fg, bg)

    print("\nDark theme spot check:")
    bg_dark = Color("#0b0f19")
    audit("primary text", Color("#e5e7eb"), bg_dark)
    audit("muted text", Color("#52525b"), bg_dark)
    audit("link", Color("#60a5fa"), bg_dark)


if __name__ == "__main__":
    main()
