"""WCAG, APCA, and deltaE."""

from __future__ import annotations

import pytest

from hexcraft import Color, apca_lc, delta_e, passes_wcag, wcag_ratio


def test_wcag_max_ratio():
    assert wcag_ratio(Color("white"), Color("black")) == pytest.approx(21.0, abs=0.01)


def test_wcag_min_ratio():
    assert wcag_ratio(Color("red"), Color("red")) == pytest.approx(1.0)


def test_wcag_symmetric():
    a, b = Color("#222"), Color("#eee")
    assert wcag_ratio(a, b) == pytest.approx(wcag_ratio(b, a))


def test_passes_aa_easy():
    assert passes_wcag(Color("black"), Color("white"), level="AA")
    assert passes_wcag(Color("black"), Color("white"), level="AAA")


def test_fails_aa_close():
    assert not passes_wcag(Color("#777"), Color("#888"), level="AA")


def test_apca_signs():
    """APCA-W3 polarity: dark text on light bg → positive Lc; light on dark → negative."""
    light_on_dark = apca_lc(Color("white"), Color("black"))
    dark_on_light = apca_lc(Color("black"), Color("white"))
    assert dark_on_light > 90.0
    assert light_on_dark < -90.0


def test_apca_zero_for_same():
    assert apca_lc(Color("red"), Color("red")) == 0.0


def test_delta_e_zero_for_same():
    c = Color("#888")
    for m in ("76", "2000", "ok"):
        assert delta_e(c, c, method=m) == pytest.approx(0.0, abs=1e-9)


def test_delta_e_2000_known():
    """CIEDE2000 reference: 50,2.6772,-79.7751 vs 50,0,-82.7485 ≈ 2.0425."""
    a = Color.from_lab(50.0, 2.6772, -79.7751)
    b = Color.from_lab(50.0, 0.0, -82.7485)
    assert delta_e(a, b, method="2000") == pytest.approx(2.0425, abs=0.01)


def test_delta_e_orderings():
    a = Color("#ff0000")
    b = Color("#ff0a00")
    c = Color("#00ff00")
    assert delta_e(a, b) < delta_e(a, c)


def test_color_method_aliases():
    a, b = Color("white"), Color("black")
    assert a.contrast(b, method="wcag") == pytest.approx(wcag_ratio(a, b))
    assert a.delta_e(b, method="2000") == pytest.approx(delta_e(a, b, method="2000"))
