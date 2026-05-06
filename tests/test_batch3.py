"""Colormaps, temperature, CIE94/CMC, closest_from, CMYK, CLI."""

from __future__ import annotations

import io
from contextlib import redirect_stdout

import pytest

from hexcraft import (
    Color,
    cividis,
    closest_from,
    closest_n_from,
    colormap,
    delta_e,
    inferno,
    magma,
    plasma,
    rdbu,
    set1,
    tab10,
    turbo,
    viridis,
)
from hexcraft.cli import main as cli_main
from hexcraft.spaces import cmyk
from hexcraft.temperature import kelvin_to_rgb, rgb_to_kelvin

# ── Colormaps ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize("cm", [viridis, magma, plasma, inferno, cividis, turbo, rdbu])
def test_colormap_endpoints_distinct(cm):
    assert cm(0.0).hex != cm(1.0).hex


def test_viridis_starts_dark_ends_light():
    assert viridis(0.0).luminance < 0.05
    assert viridis(1.0).luminance > 0.7


def test_magma_dark_to_light():
    assert magma(0.0).luminance < 0.05
    assert magma(1.0).luminance > 0.6


@pytest.mark.parametrize("cm", [viridis, magma, plasma, inferno, cividis])
def test_sequential_monotone_lightness(cm):
    """Sequential perceptual maps (excluding rainbow turbo) should be monotonic."""
    samples = [cm(i / 20).luminance for i in range(21)]
    diffs = [samples[i + 1] - samples[i] for i in range(20)]
    assert sum(1 for d in diffs if d < 0) <= 3


def test_colormap_clamps():
    assert viridis(-0.5).hex == viridis(0.0).hex
    assert viridis(1.5).hex == viridis(1.0).hex


def test_colormap_colors_n():
    cs = viridis.colors(8)
    assert len(cs) == 8
    assert cs[0].hex == viridis(0.0).hex
    assert cs[-1].hex == viridis(1.0).hex


def test_qualitative_gives_distinct():
    cs = tab10.colors()
    assert len(cs) == 10
    assert len({c.hex for c in cs}) == 10


def test_qualitative_request_more_than_stops():
    cs = set1.colors(15)
    assert len(cs) == 15


def test_colormap_lookup():
    assert colormap("viridis")(0.5).hex == viridis(0.5).hex
    with pytest.raises(ValueError):
        colormap("does-not-exist")


# ── Temperature ───────────────────────────────────────────────────────────


def test_kelvin_6500_close_to_white():
    r, g, b = kelvin_to_rgb(6500)
    assert min(r, g, b) > 0.9
    assert max(abs(r - g), abs(g - b), abs(r - b)) < 0.1


def test_kelvin_warm_red_dominant():
    r, g, b = kelvin_to_rgb(2000)
    assert r > g > b


def test_kelvin_cool_blue_dominant():
    r, g, b = kelvin_to_rgb(20000)
    assert b >= g
    assert b > r


def test_color_from_kelvin():
    c = Color.from_kelvin(2700)
    r, g, b = c.rgb
    assert r >= g >= b


def test_kelvin_round_trip_warm_white():
    c = Color.from_kelvin(3500)
    cct = rgb_to_kelvin(c)
    assert cct is not None
    assert abs(cct - 3500) < 500


def test_kelvin_undefined_for_pure_color():
    assert rgb_to_kelvin(Color("transparent")) is None


# ── CIE94 / CMC / closest_from ────────────────────────────────────────────


def test_de94_zero_for_same():
    c = Color("#abcdef")
    assert delta_e(c, c, method="94") == pytest.approx(0.0, abs=1e-9)


def test_de_cmc_zero_for_same():
    c = Color("#abcdef")
    assert delta_e(c, c, method="cmc") == pytest.approx(0.0, abs=1e-9)


def test_de94_orderings():
    a = Color("#ff0000")
    b = Color("#ff0a00")
    c = Color("#00ff00")
    assert delta_e(a, b, method="94") < delta_e(a, c, method="94")


def test_closest_from_finds_match():
    palette = [Color("red"), Color("green"), Color("blue"), Color("yellow")]
    target = Color("#ff1010")
    assert closest_from(target, palette).hex == "#ff0000"


def test_closest_from_empty_raises():
    with pytest.raises(ValueError):
        closest_from(Color("red"), [])


def test_closest_n_from_returns_n_sorted():
    palette = [Color("red"), Color("orangered"), Color("blue"), Color("orange")]
    out = closest_n_from(Color("red"), palette, n=3)
    assert len(out) == 3
    assert out[0].hex == "#ff0000"


# ── CMYK ──────────────────────────────────────────────────────────────────


def test_cmyk_white():
    assert cmyk.srgb_to_cmyk((1.0, 1.0, 1.0)) == (0.0, 0.0, 0.0, 0.0)


def test_cmyk_black():
    assert cmyk.srgb_to_cmyk((0.0, 0.0, 0.0)) == (0.0, 0.0, 0.0, 1.0)


def test_cmyk_red():
    c, m, y, k = cmyk.srgb_to_cmyk((1.0, 0.0, 0.0))
    assert c == pytest.approx(0.0)
    assert m == pytest.approx(1.0)
    assert y == pytest.approx(1.0)
    assert k == pytest.approx(0.0)


def test_cmyk_round_trip():
    rgb = (0.4, 0.6, 0.8)
    out = cmyk.cmyk_to_srgb(cmyk.srgb_to_cmyk(rgb))
    assert all(abs(o - r) < 1e-9 for o, r in zip(out, rgb, strict=True))


def test_color_cmyk_property():
    c = Color("red")
    assert c.cmyk == cmyk.srgb_to_cmyk(c.srgb)


def test_color_from_cmyk():
    c = Color.from_cmyk(0.0, 1.0, 1.0, 0.0)
    assert c.rgb == (255, 0, 0)


# ── CLI ───────────────────────────────────────────────────────────────────


def _run(args: list[str]) -> str:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cli_main(args)
    assert rc == 0, f"CLI returned {rc} for {args!r}"
    return buf.getvalue()


def test_cli_inspect():
    out = _run(["inspect", "#3498db"])
    assert "#3498db" in out
    assert "rgb" in out
    assert "oklch" in out


def test_cli_convert():
    out = _run(["convert", "red", "--to", "hsl"])
    assert "hsl" in out


def test_cli_palette_material():
    out = _run(["palette", "#3498db", "--type", "material"])
    assert "#000000" in out
    assert "#ffffff" in out


def test_cli_palette_triadic():
    out = _run(["palette", "red", "--type", "triadic"])
    assert "#ff0000" in out


def test_cli_contrast_passes():
    out = _run(["contrast", "black", "white"])
    assert "21.00" in out
    assert "AA" in out and "PASS" in out


def test_cli_closest():
    out = _run(["closest", "#ff1010", "red", "blue", "green"])
    assert "#ff0000" in out
