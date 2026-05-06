"""Parser tests for hex / CSS function / named color syntax."""

from __future__ import annotations

import pytest

from hexcraft import Color, ColorParseError


@pytest.mark.parametrize(
    "value,expected_rgb,expected_alpha",
    [
        ("#fff", (255, 255, 255), 1.0),
        ("#ffffff", (255, 255, 255), 1.0),
        ("#000", (0, 0, 0), 1.0),
        ("#ff0000", (255, 0, 0), 1.0),
        ("#FF0000", (255, 0, 0), 1.0),
        ("#f00f", (255, 0, 0), 1.0),
        ("#ff000080", (255, 0, 0), pytest.approx(128 / 255, abs=1e-3)),
        ("#0000", (0, 0, 0), 0.0),
    ],
)
def test_hex(value, expected_rgb, expected_alpha):
    c = Color(value)
    assert c.rgb == expected_rgb
    assert c.alpha == expected_alpha


@pytest.mark.parametrize(
    "value,rgb",
    [
        ("rgb(255, 0, 0)", (255, 0, 0)),
        ("rgb(255 0 0)", (255, 0, 0)),
        ("rgb(100%, 0%, 0%)", (255, 0, 0)),
        ("rgba(255, 0, 0, 0.5)", (255, 0, 0)),
        ("rgb(255 0 0 / 50%)", (255, 0, 0)),
    ],
)
def test_rgb(value, rgb):
    assert Color(value).rgb == rgb


def test_rgb_alpha():
    c = Color("rgba(255, 0, 0, 0.5)")
    assert c.alpha == pytest.approx(0.5)


@pytest.mark.parametrize(
    "value,name",
    [
        ("red", (255, 0, 0)),
        ("rebeccapurple", (102, 51, 153)),
        ("transparent", (0, 0, 0)),
    ],
)
def test_named(value, name):
    c = Color(value)
    assert c.rgb == name


def test_transparent_alpha():
    assert Color("transparent").alpha == 0.0


def test_hsl():
    assert Color("hsl(0, 100%, 50%)").rgb == (255, 0, 0)
    assert Color("hsl(120 100% 50%)").rgb == (0, 255, 0)


def test_hwb():
    assert Color("hwb(0 0% 0%)").rgb == (255, 0, 0)
    assert Color("hwb(0 100% 0%)").rgb == (255, 255, 255)


def test_oklch_red():
    """oklch(0.628 0.258 29.234) should be near sRGB red."""
    c = Color("oklch(0.628 0.258 29.234)")
    r, g, b = c.rgb
    assert r > 240 and g < 20 and b < 20


def test_lab_white():
    c = Color("lab(100 0 0)")
    assert c.rgb == (255, 255, 255)


def test_color_func_srgb():
    assert Color("color(srgb 1 0 0)").rgb == (255, 0, 0)


def test_invalid():
    with pytest.raises(ColorParseError):
        Color("not-a-color")
    with pytest.raises(ColorParseError):
        Color("#xyz")


def test_construct_from_color():
    a = Color("red")
    b = Color(a)
    assert a == b
