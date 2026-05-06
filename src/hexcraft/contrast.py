"""Contrast metrics: WCAG 2.x and APCA (Lc).

WCAG 2.1 ratio is symmetric, range [1, 21]. APCA Lc is signed and direction-
sensitive (text-on-background); we expose absolute Lc but preserve the sign of
the polarity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .color import Color


def wcag_ratio(a: Color, b: Color) -> float:
    """WCAG 2.x contrast ratio between two colors. Range [1, 21]."""
    la, lb = a.luminance, b.luminance
    lighter, darker = (la, lb) if la >= lb else (lb, la)
    return (lighter + 0.05) / (darker + 0.05)


def passes_wcag(fg: Color, bg: Color, level: str = "AA", *, large: bool = False) -> bool:
    """True if fg-on-bg meets WCAG ``level`` ('AA' or 'AAA'); large text flag relaxes."""
    ratio = wcag_ratio(fg, bg)
    if level.upper() == "AAA":
        return ratio >= (4.5 if large else 7.0)
    return ratio >= (3.0 if large else 4.5)


# APCA - SAPC W3-style implementation. Constants from APCA-W3 / SAPC-APCA.
# Reference: https://www.w3.org/TR/WCAG-3-conformance/#contrast-apca
_NORM_BG = 0.56
_NORM_TXT = 0.57
_REV_TXT = 0.62
_REV_BG = 0.65
_BLK_THRS = 0.022
_BLK_CLMP = 1.414
_SCALE_BoW = 1.14
_LO_BoW_OFFSET = 0.027
_SCALE_WoB = 1.14
_LO_WoB_OFFSET = 0.027
_DELTA_Y_MIN = 0.0005
_LO_CLIP = 0.1


def _apca_y(c: Color) -> float:
    """APCA-style screen Y from gamma-encoded sRGB with simple ^2.4 (not the toe)."""
    r, g, b = (max(0.0, min(1.0, x)) for x in c.srgb)
    return 0.2126729 * (r ** 2.4) + 0.7151522 * (g ** 2.4) + 0.0721750 * (b ** 2.4)


def apca_lc(text: Color, bg: Color) -> float:
    """APCA Lc value (text on background).

    Follows the APCA-W3 sign convention: positive for dark text on a light
    background, negative for light text on a dark background. Magnitude is
    what most readability tables (e.g. Lc 60 for body text) refer to.
    """
    y_txt = _apca_y(text)
    y_bg = _apca_y(bg)
    if y_txt < _BLK_THRS:
        y_txt = y_txt + (_BLK_THRS - y_txt) ** _BLK_CLMP
    if y_bg < _BLK_THRS:
        y_bg = y_bg + (_BLK_THRS - y_bg) ** _BLK_CLMP
    if abs(y_bg - y_txt) < _DELTA_Y_MIN:
        return 0.0
    if y_bg > y_txt:
        s = (y_bg ** _NORM_BG) - (y_txt ** _NORM_TXT)
        c = s * _SCALE_BoW
        if c < _LO_CLIP:
            return 0.0
        out = c - _LO_BoW_OFFSET
    else:
        s = (y_bg ** _REV_BG) - (y_txt ** _REV_TXT)
        c = s * _SCALE_WoB
        if c > -_LO_CLIP:
            return 0.0
        out = c + _LO_WoB_OFFSET
    return out * 100.0
