"""Dominant color extraction (numpy required)."""

from __future__ import annotations

import numpy as np
import pytest

from hexcraft import Color
from hexcraft.image import average_color, dominant_colors


def _checker_image(colors, size=32):
    h = w = size
    n = len(colors)
    rng = np.random.default_rng(0)
    labels = rng.integers(0, n, size=(h, w))
    img = np.zeros((h, w, 3), dtype=np.float64)
    for i, c in enumerate(colors):
        img[labels == i] = np.array(c.srgb)
    return img


def test_dominant_colors_recovers_known_palette():
    palette = [Color("red"), Color("green"), Color("blue")]
    img = _checker_image(palette)
    out = dominant_colors(img, n=3, seed=0)
    assert len(out) == 3
    out_hexes = {c.hex for c in out}
    expected_hexes = {c.hex for c in palette}
    assert len(out_hexes & expected_hexes) >= 2


def test_dominant_colors_median_cut():
    palette = [Color("red"), Color("blue"), Color("white")]
    img = _checker_image(palette, size=64)
    out = dominant_colors(img, n=3, method="median_cut")
    assert len(out) == 3


def test_dominant_colors_uint8_input():
    arr = (np.random.default_rng(0).random((64, 64, 3)) * 255).astype(np.uint8)
    out = dominant_colors(arr, n=4, seed=0)
    assert len(out) == 4


def test_dominant_colors_unknown_method():
    with pytest.raises(ValueError):
        dominant_colors(np.zeros((4, 4, 3)), n=2, method="foo")  # type: ignore[arg-type]


def test_average_color_pure_red():
    img = np.tile(np.array([[1.0, 0.0, 0.0]]), (10, 10, 1))
    assert average_color(img).rgb == (255, 0, 0)


def test_average_color_gray_via_linear_avg():
    """Average of black and white in linear sRGB lands near 0.5 linear ≈ #bcbcbc encoded."""
    img = np.array([[[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]])
    avg = average_color(img)
    r, g, b = avg.rgb
    assert 180 <= r <= 195 and r == g == b
