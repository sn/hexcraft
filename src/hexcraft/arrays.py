"""Vectorized color operations for numpy arrays.

Numpy is a soft dependency; importing this module without numpy raises a
clear ImportError pointing to ``pip install hexcraft[numpy]``.

All array functions accept and return arrays with shape (..., 3) for
3-component spaces or (..., 4) when alpha is present. Values are normalized
to [0, 1] for sRGB-family spaces; perceptual spaces use natural units.
"""

from __future__ import annotations

try:
    import numpy as np
except ImportError as e:
    raise ImportError(
        "hexcraft.arrays requires numpy. Install with: pip install 'hexcraft[numpy]'"
    ) from e

from typing import Any

from .spaces import oklab as _oklab_scalar
from .spaces import xyz as _xyz_scalar

NDArray = Any


# Single source of truth: scalar matrices live in hexcraft.spaces; we wrap
# them in numpy arrays here so a future correction stays in lock-step.
_M_RGB_TO_XYZ = np.array(_xyz_scalar._M_RGB_TO_XYZ)
_M_XYZ_TO_RGB = np.array(_xyz_scalar._M_XYZ_TO_RGB)
_M1 = np.array(_oklab_scalar._M1)
_M2 = np.array(_oklab_scalar._M2)
_M2_INV = np.array(_oklab_scalar._M2_INV)
_M1_INV = np.array(_oklab_scalar._M1_INV)


def srgb_decode(rgb: NDArray) -> NDArray:
    """Vectorized sRGB transfer function: gamma sRGB → linear sRGB."""
    rgb = np.asarray(rgb, dtype=np.float64)
    sign = np.sign(rgb)
    a = np.abs(rgb)
    out = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    return sign * out


def srgb_encode(rgb: NDArray) -> NDArray:
    """Vectorized inverse sRGB transfer function: linear → gamma sRGB."""
    rgb = np.asarray(rgb, dtype=np.float64)
    sign = np.sign(rgb)
    a = np.abs(rgb)
    out = np.where(a <= 0.0031308, 12.92 * a, 1.055 * (a ** (1.0 / 2.4)) - 0.055)
    return sign * out


def linear_rgb_to_xyz(rgb: NDArray) -> NDArray:
    """Vectorized linear sRGB → CIE XYZ (D65)."""
    return np.einsum("ij,...j->...i", _M_RGB_TO_XYZ, np.asarray(rgb, dtype=np.float64))


def xyz_to_linear_rgb(xyz: NDArray) -> NDArray:
    """Vectorized CIE XYZ (D65) → linear sRGB."""
    return np.einsum("ij,...j->...i", _M_XYZ_TO_RGB, np.asarray(xyz, dtype=np.float64))


def linear_rgb_to_oklab(rgb: NDArray) -> NDArray:
    """Vectorized linear sRGB → OKLab."""
    rgb = np.asarray(rgb, dtype=np.float64)
    lms = np.einsum("ij,...j->...i", _M1, rgb)
    lms_ = np.cbrt(lms)
    return np.einsum("ij,...j->...i", _M2, lms_)


def oklab_to_linear_rgb(lab: NDArray) -> NDArray:
    """Vectorized OKLab → linear sRGB."""
    lab = np.asarray(lab, dtype=np.float64)
    lms_ = np.einsum("ij,...j->...i", _M2_INV, lab)
    lms = lms_**3
    return np.einsum("ij,...j->...i", _M1_INV, lms)


def srgb_to_oklab(rgb: NDArray) -> NDArray:
    """Convenience: gamma sRGB → linear sRGB → OKLab."""
    return linear_rgb_to_oklab(srgb_decode(rgb))


def oklab_to_srgb(lab: NDArray) -> NDArray:
    """Convenience: OKLab → linear sRGB → gamma sRGB (no clipping or gamut mapping)."""
    return srgb_encode(oklab_to_linear_rgb(lab))


def relative_luminance(rgb: NDArray) -> NDArray:
    """WCAG relative luminance from gamma-encoded sRGB in [0, 1]."""
    lin = srgb_decode(np.clip(np.asarray(rgb), 0.0, 1.0))
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def wcag_ratio(rgb_a: NDArray, rgb_b: NDArray) -> NDArray:
    """Vectorized WCAG 2.x contrast ratio between two sRGB arrays. Range [1, 21]."""
    la = relative_luminance(rgb_a)
    lb = relative_luminance(rgb_b)
    lighter = np.maximum(la, lb)
    darker = np.minimum(la, lb)
    return (lighter + 0.05) / (darker + 0.05)


def delta_e_ok(rgb_a: NDArray, rgb_b: NDArray) -> NDArray:
    """Per-pixel Euclidean ΔE in OKLab between two sRGB arrays."""
    la = srgb_to_oklab(rgb_a)
    lb = srgb_to_oklab(rgb_b)
    return np.linalg.norm(la - lb, axis=-1)
