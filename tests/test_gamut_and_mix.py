"""Gamut mapping and mixing semantics."""

from __future__ import annotations

import pytest

from hexcraft import Color, blend, mix


def test_mix_default_oklab():
    a = Color("red")
    b = Color("blue")
    m = mix(a, b, 0.5)
    L_a, _, _ = a.oklab
    L_b, _, _ = b.oklab
    L_m, _, _ = m.oklab
    assert L_m == pytest.approx((L_a + L_b) / 2, abs=1e-6)


def test_mix_zero_returns_a():
    assert mix(Color("red"), Color("blue"), 0.0) == Color("red")


def test_mix_one_returns_b():
    assert mix(Color("red"), Color("blue"), 1.0) == Color("blue")


def test_mix_alpha_interpolated():
    a = Color("red").with_alpha(0.0)
    b = Color("blue").with_alpha(1.0)
    m = mix(a, b, 0.5, space="srgb")
    assert m.alpha == pytest.approx(0.5)


def test_mix_hue_short_path():
    """350° -> 10° should go through 0°, not via 180°."""
    a = Color.from_oklch(0.7, 0.1, 350.0)
    b = Color.from_oklch(0.7, 0.1, 10.0)
    m = mix(a, b, 0.5, space="oklch")
    _, _, h = m.oklch
    assert h < 1.0 or h > 359.0


def test_blend_full_opaque_returns_fg():
    bg = Color("red")
    fg = Color("blue")
    assert blend(bg, fg).rgb == (0, 0, 255)


def test_blend_zero_alpha_returns_bg():
    bg = Color("red")
    fg = Color("blue").with_alpha(0.0)
    assert blend(bg, fg).rgb == (255, 0, 0)


def test_blend_half_over_white():
    bg = Color("white")
    fg = Color("black").with_alpha(0.5)
    out = blend(bg, fg)
    r, g, b = out.rgb
    assert 180 <= r <= 195  # linear-blend midpoint of white/black
    assert 180 <= g <= 195
    assert 180 <= b <= 195


def test_to_gamut_in_gamut_unchanged():
    c = Color("red")
    assert c.to_gamut() == c


def test_to_gamut_wide():
    c = Color.from_oklch(0.7, 0.4, 30)
    mapped = c.to_gamut()
    assert mapped.in_gamut()


def test_to_gamut_lightness_extremes():
    above = Color.from_oklch(1.5, 0.3, 30)
    assert above.to_gamut().rgb == (255, 255, 255)
    below = Color.from_oklch(-0.1, 0.3, 30)
    assert below.to_gamut().rgb == (0, 0, 0)
