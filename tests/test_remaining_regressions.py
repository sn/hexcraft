"""Regression tests: parse errors, alpha range, immutability, kelvin, material tones, invert, CLI lab."""

from __future__ import annotations

import copy
import pickle
import re

import pytest

from hexcraft import Color, ColorParseError, material_tonal_palette
from hexcraft.cli import main

# ── Malformed numbers raise ColorParseError ──────────────────────────────


@pytest.mark.parametrize("s", [
    "rgb(foo, 0, 0)",
    "hsl(x 50% 50%)",
    "lab(50 abc 0)",
    "oklch(0.5 abc 30)",
    "color(srgb a b c)",
    "rgb(1 2 3 / zz)",
])
def test_malformed_number_raises_color_parse_error(s):
    with pytest.raises(ColorParseError):
        Color(s)


def test_cli_reports_malformed_number_without_traceback(capsys):
    assert main(["inspect", "rgb(foo,0,0)"]) == 2
    assert "hexcraft:" in capsys.readouterr().err


# ── Alpha is clamped to [0, 1] ───────────────────────────────────────────


@pytest.mark.parametrize(("alpha", "expected"), [(-0.2, 0.0), (1.5, 1.0), (0.25, 0.25)])
def test_with_alpha_clamps(alpha, expected):
    assert Color("red").with_alpha(alpha).alpha == expected


def test_constructors_clamp_alpha():
    assert Color.from_rgb(1, 0, 0, 2.0).alpha == 1.0
    assert Color.from_oklch(0.6, 0.1, 30, a=-1.0).alpha == 0.0
    assert Color((1.0, 0.0, 0.0, 5.0)).alpha == 1.0


@pytest.mark.parametrize("alpha", [-0.2, 0.0, 0.5, 0.999, 1.0, 1.5])
def test_hex_is_always_valid(alpha):
    assert re.fullmatch(r"#[0-9a-f]{6}([0-9a-f]{2})?", Color("red").with_alpha(alpha).hex)


def test_hex_omits_alpha_that_rounds_to_opaque():
    assert Color("red").with_alpha(0.999).hex == "#ff0000"


# ── Color is immutable ───────────────────────────────────────────────────


def test_color_rejects_attribute_assignment():
    c = Color("red")
    with pytest.raises(AttributeError):
        c._lr = 0.5  # type: ignore[misc]
    assert c.hex == "#ff0000"


@pytest.mark.parametrize("clone", [copy.copy, copy.deepcopy, lambda c: pickle.loads(pickle.dumps(c))])
def test_color_copies_and_pickles(clone):
    c = Color("#3366cc80")
    assert clone(c) == c


# ── kelvin is None far from the blackbody locus ──────────────────────────


@pytest.mark.parametrize("s", ["lime", "magenta", "red", "#3498db"])
def test_kelvin_none_for_saturated_colors(s):
    assert Color(s).kelvin is None


def test_kelvin_of_white_is_d65():
    assert Color("white").kelvin == pytest.approx(6504, abs=50)


@pytest.mark.parametrize("t", [2000, 3000, 4000, 6500, 10000, 15000])
def test_kelvin_defined_for_blackbody_colors(t):
    assert Color.from_kelvin(t).kelvin is not None


# ── Material tones are CIE L* ────────────────────────────────────────────


@pytest.mark.parametrize("src", ["#6750a4", "#3498db", "#ff0000", "#00ff00", "#808080"])
def test_material_tone_is_cie_lstar(src):
    for tone, c in material_tonal_palette(Color(src)).items():
        assert c.lab[0] == pytest.approx(tone, abs=0.5), (src, tone)


# ── invert() works in gamma-encoded sRGB ─────────────────────────────────


def test_invert_mid_gray_is_mid_gray():
    assert Color("#808080").invert().hex == "#7f7f7f"


def test_invert_matches_css_filter():
    assert Color("#3366cc").invert().hex == "#cc9933"


def test_invert_preserves_alpha():
    assert Color("#33669980").invert().alpha == pytest.approx(128 / 255)


# ── CLI inspect prints CSS (D50) lab ─────────────────────────────────────


def test_cli_inspect_lab_is_css_d50(capsys):
    assert main(["inspect", "red"]) == 0
    assert "lab(54.3 80.8 69.9)" in capsys.readouterr().out
