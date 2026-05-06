"""Color class API tests."""

from __future__ import annotations

import pytest

from hexcraft import Color


def test_constructors_equivalent():
    a = Color.from_rgb(255, 0, 0)
    b = Color("#ff0000")
    c = Color("red")
    assert a == b == c


def test_hex_property():
    assert Color("red").hex == "#ff0000"
    assert Color.from_rgb(0, 0, 0).hex == "#000000"
    assert Color.from_rgb(255, 255, 255).hex == "#ffffff"


def test_hex_with_alpha():
    c = Color.from_rgb(255, 0, 0, a=0.5)
    assert c.hex.startswith("#ff0000")
    assert len(c.hex) == 9


def test_rgb_tuple():
    assert Color("red").rgb == (255, 0, 0)
    assert Color("#80c0ff").rgb == (128, 192, 255)


def test_hsl_red():
    h, s, L = Color("red").hsl
    assert h == pytest.approx(0.0)
    assert s == pytest.approx(1.0)
    assert pytest.approx(0.5) == L


def test_oklch_for_known():
    """Reference: red ≈ oklch(0.628 0.258 29.23)."""
    L, c, h = Color("red").oklch
    assert pytest.approx(0.628, abs=0.01) == L
    assert c == pytest.approx(0.258, abs=0.01)
    assert h == pytest.approx(29.23, abs=0.5)


def test_immutable():
    c = Color("red")
    with pytest.raises(AttributeError):
        c.something_new = 1  # type: ignore[attr-defined]


def test_with_alpha():
    a = Color("red")
    b = a.with_alpha(0.5)
    assert a.alpha == 1.0
    assert b.alpha == 0.5
    assert b.rgb == (255, 0, 0)


def test_lighten_darken_inverse_ish():
    a = Color("#808080")
    lighter = a.lighten(0.1)
    darker = a.darken(0.1)
    assert lighter.luminance > a.luminance
    assert darker.luminance < a.luminance


def test_grayscale():
    c = Color("red").grayscale()
    r, g, b = c.rgb
    assert abs(r - g) <= 2 and abs(g - b) <= 2


def test_invert():
    assert Color("white").invert().rgb == (0, 0, 0)
    assert Color("black").invert().rgb == (255, 255, 255)


def test_complement():
    c = Color("red").complement()
    L, _, h = c.oklch
    L0, _, h0 = Color("red").oklch
    diff = ((h - h0) % 360.0)
    assert min(abs(diff - 180.0), abs(diff + 180.0)) < 0.01
    assert pytest.approx(L0, abs=1e-4) == L


def test_repr_and_str():
    c = Color("red")
    assert str(c) == "#ff0000"
    assert repr(c) == "Color('#ff0000')"


def test_hash_equals():
    s = {Color("red"), Color("#ff0000")}
    assert len(s) == 1


def test_in_gamut():
    assert Color("red").in_gamut()
    wide = Color.from_oklch(0.7, 0.4, 30)
    assert wide.in_gamut() is False


def test_to_gamut_keeps_alpha():
    wide = Color.from_oklch(0.7, 0.4, 30, a=0.5)
    mapped = wide.to_gamut()
    assert mapped.alpha == 0.5
    assert mapped.in_gamut()


def test_css_formats():
    c = Color("red")
    assert c.css("hex") == "#ff0000"
    assert "rgb" in c.css("rgb")
    assert "hsl" in c.css("hsl")
    assert "oklch" in c.css("oklch")


def test_name_closest():
    assert Color("#ff0000").name == "red"
    assert Color("#000000").name == "black"


def test_method_tints_from_black():
    p = Color("#000000").tints(10)
    assert len(p) == 10
    assert p[0].rgb == (0, 0, 0)
    r, g, b = p[-1].rgb
    assert r > 250 and g > 250 and b > 250


def test_method_shades_from_red():
    p = Color("red").shades(5)
    assert len(p) == 5
    assert p[0] == Color("red")
    r, g, b = p[-1].rgb
    assert r < 5 and g < 5 and b < 5


def test_lighter_darker_aliases():
    c = Color("#3498db")
    assert c.lighter(5) == c.tints(5)
    assert c.darker(5) == c.shades(5)


def test_method_triadic_complementary_etc():
    c = Color("#3498db")
    assert len(c.complementary()) == 2
    assert len(c.triadic()) == 3
    assert len(c.tetradic()) == 4
    assert len(c.split_complementary()) == 3
    assert len(c.analogous(count=5)) == 5
    assert len(c.monochromatic(count=7)) == 7
    assert len(c.tones(count=4)) == 4
