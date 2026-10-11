"""Regression tests: colormap stop data and qualitative-map indexing."""

from __future__ import annotations

import pytest

from hexcraft import ALL_MAPS, Color, magma, set1, tab10, turbo

# matplotlib reference samples at t = 0, 0.1, ..., 1.0
_MPL_MAGMA = (
    "#000004", "#140e36", "#3b0f70", "#641a80", "#8c2981", "#b73779",
    "#de4968", "#f7705c", "#fe9f6d", "#fecf92", "#fcfdbf",
)
_MPL_TURBO = (
    "#30123b", "#4559cb", "#3e9bfe", "#19d5cd", "#46f884", "#a4fc3c",
    "#e1dd37", "#fea431", "#f05b12", "#c32503", "#7a0403",
)


@pytest.mark.parametrize(("cmap", "ref"), [(magma, _MPL_MAGMA), (turbo, _MPL_TURBO)])
def test_colormap_matches_matplotlib_samples(cmap, ref):
    assert [cmap(i / 10).hex for i in range(11)] == list(ref)


def test_turbo_ends_in_dark_red():
    assert turbo(1.0).hex == "#7a0403"


@pytest.mark.parametrize("name", sorted(ALL_MAPS))
def test_no_repeated_adjacent_stops(name):
    stops = ALL_MAPS[name].stops
    assert all(a != b for a, b in zip(stops, stops[1:], strict=False)), name


@pytest.mark.parametrize("cmap", [tab10, set1])
def test_qualitative_call_clamps_below_zero(cmap):
    assert cmap(-0.5) == Color(cmap.stops[0])


@pytest.mark.parametrize("cmap", [tab10, set1])
def test_qualitative_call_clamps_above_one(cmap):
    assert cmap(1.5) == Color(cmap.stops[-1])
