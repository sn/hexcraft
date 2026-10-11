"""Regression tests: xyz mixing, eq/hash consistency, monochromatic gamut, tones alpha."""

from __future__ import annotations

import pytest

from hexcraft import Color, mix, monochromatic, tones

# ── 4. Mixing in XYZ ──────────────────────────────────────────────────────


def test_color_mix_accepts_xyz():
    m = Color("red").mix(Color("blue"), space="xyz")
    a, b = Color("red").xyz, Color("blue").xyz
    assert m.xyz == pytest.approx(tuple((p + q) / 2 for p, q in zip(a, b, strict=True)), abs=1e-9)


def test_mix_xyz_lerps_alpha():
    m = mix(Color("red").with_alpha(0.2), Color("blue"), 0.5, space="xyz")
    assert m.alpha == pytest.approx(0.6)


# ── 5. Equal colors hash equally ──────────────────────────────────────────


def test_eq_and_hash_agree_across_rounding_boundary():
    """Values 2e-7 apart straddling a 6th-decimal rounding boundary."""
    a = Color.from_linear_rgb(0.0000004, 0.0, 0.0)
    b = Color.from_linear_rgb(0.0000006, 0.0, 0.0)
    assert (a == b) == (hash(a) == hash(b))


def test_equal_colors_collapse_in_set():
    a = Color("color(display-p3 0.5 0.5 0.5)")
    b = Color.from_p3(0.5, 0.5, 0.5)
    assert a == b
    assert len({a, b}) == 1


def test_negative_zero_equals_zero():
    a = Color.from_linear_rgb(-0.0, 0.0, 0.0)
    b = Color.from_linear_rgb(0.0, 0.0, 0.0)
    assert a == b and hash(a) == hash(b)


# ── 6. monochromatic stays in gamut ───────────────────────────────────────


@pytest.mark.parametrize("src", ["#3366cc", "red", "lime", "#ff00ff"])
def test_monochromatic_steps_in_gamut(src):
    for c in monochromatic(Color(src), count=7):
        assert c.in_gamut(), c.linear_rgb


def test_monochromatic_endpoints_are_black_and_white():
    p = monochromatic(Color("#3366cc"), count=5)
    assert p[0].hex == "#000000"
    assert p[-1].hex == "#ffffff"


def test_monochromatic_preserves_hue():
    src = Color("#3366cc")
    for c in monochromatic(src, count=5)[1:-1]:
        assert c.oklch[2] == pytest.approx(src.oklch[2], abs=1.0)


def test_monochromatic_preserves_alpha():
    assert all(c.alpha == 0.5 for c in monochromatic(Color("red").with_alpha(0.5), count=5))


# ── 7. tones keeps the source alpha ───────────────────────────────────────


def test_tones_preserve_alpha():
    p = tones(Color("#3366cc80"), count=4)
    assert [c.alpha for c in p] == pytest.approx([128 / 255] * 4)
