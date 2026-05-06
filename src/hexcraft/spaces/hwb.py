"""HWB (gamma sRGB). CSS Color Module Level 4."""

from __future__ import annotations

from .hsv import hsv_to_srgb, srgb_to_hsv


def srgb_to_hwb(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert gamma sRGB to HWB. h in degrees [0, 360); w, b in [0, 1]."""
    r, g, b = rgb
    h, _, _ = srgb_to_hsv(rgb)
    w = min(r, g, b)
    bl = 1.0 - max(r, g, b)
    return (h, w, bl)


def hwb_to_srgb(hwb: tuple[float, float, float]) -> tuple[float, float, float]:
    """Convert HWB to gamma sRGB. h in degrees, w/b in [0, 1]."""
    h, w, bl = hwb
    if w + bl >= 1.0:
        gray = w / (w + bl)
        return (gray, gray, gray)
    r, g, b = hsv_to_srgb((h, 1.0, 1.0))
    f = 1.0 - w - bl
    return (r * f + w, g * f + w, b * f + w)
