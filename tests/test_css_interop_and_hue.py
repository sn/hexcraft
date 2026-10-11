"""Regression tests: CSS lab()/lch() white point, display-p3 parsing, achromatic hue mixing."""

from __future__ import annotations

import pytest

from hexcraft import Color, mix

# CSS Color 4 reference for sRGB red: lab()/lch() are D50-relative.
_RED_CSS_LAB = (54.2905, 80.8049, 69.8910)
_RED_CSS_LCH = (54.2905, 106.8372, 40.8526)


def _components(css: str) -> tuple[float, ...]:
    body = css[css.index("(") + 1 : css.index(")")]
    return tuple(float(t) for t in body.split())


# ── 1. CSS lab()/lch() use the D50 white point ────────────────────────────


def test_parse_css_lab_is_d50():
    assert Color("lab(54.2905 80.8049 69.891)").hex == "#ff0000"


def test_parse_css_lch_is_d50():
    assert Color("lch(54.2905 106.8372 40.8526)").hex == "#ff0000"


def test_format_css_lab_is_d50():
    assert _components(Color("red").css("lab")) == pytest.approx(_RED_CSS_LAB, abs=0.01)


def test_format_css_lch_is_d50():
    assert _components(Color("red").css("lch")) == pytest.approx(_RED_CSS_LCH, abs=0.01)


@pytest.mark.parametrize("fmt", ["lab", "lch"])
def test_css_lab_lch_round_trip(fmt):
    c = Color("#3b82f6")
    assert Color(c.css(fmt)).hex == c.hex


def test_lab_property_stays_d65():
    """The Python API is unchanged: Color.lab remains D65-relative."""
    L, a, b = Color("red").lab
    assert (L, a, b) == pytest.approx((53.2371, 80.0901, 67.2033), abs=0.01)


# ── 2. color(display-p3 ...) components are gamma-encoded ─────────────────


def test_parse_display_p3_decodes_gamma():
    assert Color("color(display-p3 0.5 0.5 0.5)") == Color.from_p3(0.5, 0.5, 0.5)


def test_parse_display_p3_mid_gray_is_808080():
    assert Color("color(display-p3 0.5 0.5 0.5)").hex == "#808080"


# ── 3. Achromatic colors have no hue when mixing in polar spaces ──────────


_HUE_INDEX = {"oklch": 2, "lch": 2, "hsl": 0, "hsv": 0, "hwb": 0}


@pytest.mark.parametrize("space", list(_HUE_INDEX))
@pytest.mark.parametrize("gray", ["white", "black", "#808080"])
def test_mix_with_achromatic_keeps_chromatic_hue(space, gray):
    blue = Color("blue")
    m = mix(Color(gray), blue, 0.5, space=space)
    i = _HUE_INDEX[space]
    assert getattr(m, space)[i] == pytest.approx(getattr(blue, space)[i], abs=0.5)


@pytest.mark.parametrize("space", list(_HUE_INDEX))
def test_mix_achromatic_order_does_not_matter(space):
    blue = Color("blue")
    i = _HUE_INDEX[space]
    m = mix(blue, Color("white"), 0.5, space=space)
    assert getattr(m, space)[i] == pytest.approx(getattr(blue, space)[i], abs=0.5)


def test_mix_white_blue_oklch_is_not_teal():
    m = mix(Color("white"), Color("blue"), 0.5, space="oklch")
    r, g, b = m.rgb
    assert b > r and b > g


def test_mix_two_grays_stays_gray():
    m = mix(Color("white"), Color("black"), 0.5, space="oklch")
    assert m.oklch[1] == pytest.approx(0.0, abs=1e-4)
