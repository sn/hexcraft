"""CVD simulation and daltonization."""

from __future__ import annotations

import pytest

from hexcraft import Color, daltonize, simulate


def test_simulate_severity_zero_unchanged():
    c = Color("#3498db")
    assert simulate(c, "protanopia", severity=0.0) == c
    assert simulate(c, "deuteranopia", severity=0.0) == c
    assert simulate(c, "tritanopia", severity=0.0) == c


@pytest.mark.parametrize("kind", ["protanopia", "deuteranopia", "tritanopia"])
def test_simulate_changes_color(kind):
    red = Color("red")
    out = simulate(red, kind, severity=1.0)
    assert out != red


def test_protan_red_dims():
    """Protanopes see red as darker / less saturated."""
    red = Color("red")
    sim = simulate(red, "protanopia")
    assert sim.luminance < red.luminance


def test_unknown_kind_raises():
    with pytest.raises(ValueError):
        simulate(Color("red"), "deuteran")  # type: ignore[arg-type]


def test_daltonize_changes_red_for_deutan():
    red = Color("red")
    dal = daltonize(red, "deuteranopia")
    assert dal != red


def test_color_simulate_method():
    c = Color("#3498db")
    assert c.simulate("deuteranopia") == simulate(c, "deuteranopia")


def test_color_daltonize_method():
    c = Color("#ff0000")
    assert c.daltonize("protanopia") == daltonize(c, "protanopia")


def test_severity_interpolates():
    c = Color("red")
    out_half = simulate(c, "protanopia", severity=0.5)
    out_full = simulate(c, "protanopia", severity=1.0)
    # Half-severity should be between original and full simulation in luminance.
    assert min(c.luminance, out_full.luminance) <= out_half.luminance <= max(c.luminance, out_full.luminance) + 1e-6
