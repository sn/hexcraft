"""Tonal palettes, accessibility helpers, P3, chromatic adaptation."""

from __future__ import annotations

import pytest

from hexcraft import (
    MATERIAL_TONES,
    TAILWIND_STOPS,
    Color,
    best_text_color,
    find_accessible_pair,
    material_tonal_palette,
    tailwind_scale,
    wcag_ratio,
)
from hexcraft.adapt import D50, D65, adapt


def test_material_palette_keys():
    p = material_tonal_palette(Color("#3498db"))
    assert tuple(sorted(p.keys())) == tuple(sorted(MATERIAL_TONES))
    assert p[0].rgb == (0, 0, 0)
    assert p[100].rgb == (255, 255, 255)


def test_material_palette_lightness_monotone():
    p = material_tonal_palette(Color("#3498db"))
    Ls = [p[t].luminance for t in MATERIAL_TONES]
    assert Ls == sorted(Ls)


def test_tailwind_keys():
    p = tailwind_scale(Color("#3498db"))
    assert tuple(sorted(p.keys())) == tuple(sorted(TAILWIND_STOPS))


def test_tailwind_500_close_to_input_chroma():
    base = Color("#3498db")
    p = tailwind_scale(base)
    _, c500, h500 = p[500].oklch
    _, cb, hb = base.oklch
    assert h500 == pytest.approx(hb, abs=1.0)
    assert c500 == pytest.approx(cb, abs=cb * 0.05 + 0.01)


def test_tailwind_lightness_descends():
    p = tailwind_scale(Color("#3498db"))
    Ls = [p[s].luminance for s in TAILWIND_STOPS]
    assert Ls == sorted(Ls, reverse=True)


def test_color_methods():
    c = Color("#3498db")
    assert c.material_palette()[50] == material_tonal_palette(c)[50]
    assert c.tailwind()[500] == tailwind_scale(c)[500]


def test_find_accessible_pair_already_passing():
    fg = Color("black")
    bg = Color("white")
    assert find_accessible_pair(fg, bg) == fg


def test_find_accessible_pair_lighten():
    base = Color("#888888")
    bg = Color("white")
    found = find_accessible_pair(base, bg, ratio=4.5, direction="darken")
    assert found is not None
    assert wcag_ratio(found, bg) >= 4.49


def test_find_accessible_pair_auto_picks_closer():
    base = Color("#777777")
    bg = Color("white")
    found = find_accessible_pair(base, bg, ratio=4.5, direction="auto")
    assert found is not None
    assert wcag_ratio(found, bg) >= 4.49


def test_best_text_color():
    assert best_text_color(Color("white")).hex == "#000000"
    assert best_text_color(Color("black")).hex == "#ffffff"


def test_p3_color_func_parses():
    c = Color("color(display-p3 1 0 0)")
    r, _, _ = c.rgb
    assert r > 230


def test_p3_round_trip():
    """P3 round-trip should preserve the linear sRGB representation closely."""
    c = Color("#3498db")
    r, g, b = c.p3
    back = Color.from_p3(r, g, b)
    assert back.hex == c.hex


def test_chromatic_adapt_identity():
    """Adapting from D65 to D65 should be identity (within numerical noise)."""
    out = adapt((0.5, 0.6, 0.7), D65, D65)
    assert out == pytest.approx((0.5, 0.6, 0.7), abs=1e-6)


def test_chromatic_adapt_d65_to_d50():
    """White-point should map exactly when adapting white."""
    out = adapt(D65, D65, D50)
    assert out == pytest.approx(D50, abs=1e-3)


def test_chromatic_adapt_round_trip():
    pt = (0.4, 0.5, 0.55)
    a = adapt(pt, D65, D50)
    b = adapt(a, D50, D65)
    assert b == pytest.approx(pt, abs=1e-6)
