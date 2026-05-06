"""Round-trip and reference-value tests for color space conversions."""

from __future__ import annotations

import math

import pytest

from hexcraft.spaces import hsl, hsv, hwb, lab, oklab, srgb, xyz


def _close(a, b, tol=1e-6):
    return all(math.isclose(x, y, abs_tol=tol) for x, y in zip(a, b, strict=True))


@pytest.mark.parametrize("c", [0.0, 0.04045, 0.5, 1.0, 0.0031308])
def test_srgb_round_trip(c):
    assert math.isclose(srgb.decode(srgb.encode(c)), c, abs_tol=1e-12)


def test_srgb_negative_passthrough():
    assert math.isclose(srgb.encode(-0.5), -srgb.encode(0.5), abs_tol=1e-12)


@pytest.mark.parametrize(
    "rgb",
    [
        (0.0, 0.0, 0.0),
        (1.0, 1.0, 1.0),
        (1.0, 0.0, 0.0),
        (0.5, 0.25, 0.75),
        (0.123, 0.456, 0.789),
    ],
)
def test_xyz_round_trip(rgb):
    out = xyz.xyz_to_linear_rgb(xyz.linear_rgb_to_xyz(rgb))
    assert _close(out, rgb, tol=1e-9)


@pytest.mark.parametrize(
    "rgb",
    [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (0.4, 0.6, 0.2)],
)
def test_oklab_round_trip(rgb):
    out = oklab.oklab_to_linear_rgb(oklab.linear_rgb_to_oklab(rgb))
    assert _close(out, rgb, tol=1e-5)


def test_oklab_white_reference():
    """OKLab of linear white should be ~(1, 0, 0). Reference: Ottosson's paper."""
    L, a, b = oklab.linear_rgb_to_oklab((1.0, 1.0, 1.0))
    assert math.isclose(L, 1.0, abs_tol=1e-3)
    assert abs(a) < 1e-3
    assert abs(b) < 1e-3


def test_oklab_black_zero():
    L, a, b = oklab.linear_rgb_to_oklab((0.0, 0.0, 0.0))
    assert abs(L) < 1e-9 and abs(a) < 1e-9 and abs(b) < 1e-9


def test_lab_white_reference():
    """Lab of D65 white should be (100, 0, 0)."""
    L, a, b = lab.xyz_to_lab(xyz.linear_rgb_to_xyz((1.0, 1.0, 1.0)))
    assert math.isclose(L, 100.0, abs_tol=1e-3)
    assert abs(a) < 1e-3
    assert abs(b) < 1e-3


@pytest.mark.parametrize(
    "rgb", [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0), (0.3, 0.6, 0.9)]
)
def test_lab_round_trip(rgb):
    L, a, b = lab.xyz_to_lab(xyz.linear_rgb_to_xyz(rgb))
    out = xyz.xyz_to_linear_rgb(lab.lab_to_xyz((L, a, b)))
    assert _close(out, rgb, tol=1e-9)


def test_lab_lch_round_trip():
    out = lab.lch_to_lab(lab.lab_to_lch((50.0, 30.0, -20.0)))
    assert _close(out, (50.0, 30.0, -20.0), tol=1e-9)


@pytest.mark.parametrize(
    "rgb", [(1.0, 0.0, 0.0), (0.5, 0.5, 0.5), (0.2, 0.8, 0.6)]
)
def test_hsl_round_trip(rgb):
    out = hsl.hsl_to_srgb(hsl.srgb_to_hsl(rgb))
    assert _close(out, rgb, tol=1e-9)


def test_hsl_red():
    h, s, L = hsl.srgb_to_hsl((1.0, 0.0, 0.0))
    assert math.isclose(h, 0.0, abs_tol=1e-9)
    assert math.isclose(s, 1.0, abs_tol=1e-9)
    assert math.isclose(L, 0.5, abs_tol=1e-9)


@pytest.mark.parametrize(
    "rgb", [(1.0, 0.0, 0.0), (0.5, 0.5, 0.5), (0.2, 0.8, 0.6)]
)
def test_hsv_round_trip(rgb):
    out = hsv.hsv_to_srgb(hsv.srgb_to_hsv(rgb))
    assert _close(out, rgb, tol=1e-9)


@pytest.mark.parametrize(
    "rgb", [(1.0, 0.0, 0.0), (0.5, 0.5, 0.5), (0.2, 0.8, 0.6)]
)
def test_hwb_round_trip(rgb):
    out = hwb.hwb_to_srgb(hwb.srgb_to_hwb(rgb))
    assert _close(out, rgb, tol=1e-9)
