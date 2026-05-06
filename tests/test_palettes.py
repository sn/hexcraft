"""Palette generators and gradient scales."""

from __future__ import annotations

from hexcraft import (
    Color,
    analogous,
    complementary,
    monochromatic,
    scale,
    shades,
    split_complementary,
    stops,
    tetradic,
    tints,
    tones,
    triadic,
)


def test_complementary():
    p = complementary(Color("red"))
    assert len(p) == 2
    assert p[0] == Color("red")


def test_triadic_count():
    assert len(triadic(Color("red"))) == 3


def test_tetradic_count():
    assert len(tetradic(Color("red"))) == 4


def test_split_complementary_count():
    assert len(split_complementary(Color("red"))) == 3


def test_analogous_default():
    p = analogous(Color("red"))
    assert len(p) == 3
    assert p[1] == Color("red")  # middle


def test_analogous_count_one():
    assert analogous(Color("red"), count=1) == [Color("red")]


def test_monochromatic_endpoints():
    p = monochromatic(Color("red"), count=5)
    assert len(p) == 5
    assert p[0].oklch[0] < 0.05
    assert p[-1].oklch[0] > 0.95


def test_shades_to_black():
    p = shades(Color("red"), count=5)
    assert p[0].rgb == (255, 0, 0)
    r, g, b = p[-1].rgb
    assert r < 5 and g < 5 and b < 5


def test_tints_to_white():
    p = tints(Color("red"), count=5)
    assert p[0].rgb == (255, 0, 0)
    r, g, b = p[-1].rgb
    assert r > 250 and g > 250 and b > 250


def test_tones_to_gray():
    p = tones(Color("red"), count=5)
    last = p[-1]
    r, g, b = last.rgb
    assert abs(r - g) < 5 and abs(g - b) < 5


def test_scale_endpoints():
    p = scale(Color("red"), Color("blue"), steps=10)
    assert len(p) == 10
    assert p[0].rgb == (255, 0, 0)
    r, g, b = p[-1].rgb
    assert b > 240 and r < 5


def test_stops_through_three():
    g = stops([Color("red"), Color("green"), Color("blue")], steps=5, space="oklab")
    assert len(g) == 5
    assert g[0].rgb == (255, 0, 0)
    r, gv, b = g[-1].rgb
    assert b > 240


def test_scale_is_monotone_lightness_for_grays():
    p = scale(Color("black"), Color("white"), steps=5)
    Ls = [c.luminance for c in p]
    assert Ls == sorted(Ls)
