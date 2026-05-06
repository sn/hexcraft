"""HSL (gamma sRGB)."""

from __future__ import annotations


def srgb_to_hsl(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert gamma sRGB to HSL. h in degrees [0, 360); s, l in [0, 1]."""
    r, g, b = rgb
    mx = max(r, g, b)
    mn = min(r, g, b)
    L = (mx + mn) / 2.0
    d = mx - mn
    if d == 0.0:
        return (0.0, 0.0, L)
    s = d / (1.0 - abs(2.0 * L - 1.0)) if L not in (0.0, 1.0) else 0.0
    if mx == r:
        h = ((g - b) / d) % 6.0
    elif mx == g:
        h = (b - r) / d + 2.0
    else:
        h = (r - g) / d + 4.0
    h *= 60.0
    if h < 0.0:
        h += 360.0
    return (h, s, L)


def hsl_to_srgb(hsl: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert HSL to gamma sRGB. h in degrees, s/l in [0, 1]."""
    h, s, L = hsl
    h = h % 360.0
    c = (1.0 - abs(2.0 * L - 1.0)) * s
    hp = h / 60.0
    x = c * (1.0 - abs(hp % 2.0 - 1.0))
    if hp < 1.0:
        r1, g1, b1 = c, x, 0.0
    elif hp < 2.0:
        r1, g1, b1 = x, c, 0.0
    elif hp < 3.0:
        r1, g1, b1 = 0.0, c, x
    elif hp < 4.0:
        r1, g1, b1 = 0.0, x, c
    elif hp < 5.0:
        r1, g1, b1 = x, 0.0, c
    else:
        r1, g1, b1 = c, 0.0, x
    m = L - c / 2.0
    return (r1 + m, g1 + m, b1 + m)
