"""HSV (gamma sRGB)."""

from __future__ import annotations


def srgb_to_hsv(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert gamma sRGB to HSV. h in degrees [0, 360); s, v in [0, 1]."""
    r, g, b = rgb
    mx = max(r, g, b)
    mn = min(r, g, b)
    d = mx - mn
    v = mx
    s = 0.0 if mx == 0.0 else d / mx
    if d == 0.0:
        h = 0.0
    elif mx == r:
        h = ((g - b) / d) % 6.0
    elif mx == g:
        h = (b - r) / d + 2.0
    else:
        h = (r - g) / d + 4.0
    h *= 60.0
    if h < 0.0:
        h += 360.0
    return (h, s, v)


def hsv_to_srgb(hsv: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert HSV to gamma sRGB. h in degrees, s/v in [0, 1]."""
    h, s, v = hsv
    h = h % 360.0
    c = v * s
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
    m = v - c
    return (r1 + m, g1 + m, b1 + m)
