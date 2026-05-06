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

NDArray = Any


_M_RGB_TO_XYZ = np.array(
    [
        [0.4123907992659595, 0.3575843393838780, 0.1804807884018343],
        [0.2126390058715104, 0.7151686787677559, 0.0721923153607337],
        [0.0193308187155918, 0.1191947797946259, 0.9505321522496608],
    ]
)
_M_XYZ_TO_RGB = np.array(
    [
        [3.2409699419045226, -1.5373831775700939, -0.4986107602930034],
        [-0.9692436362808796, 1.8759675015077202, 0.0415550574071756],
        [0.0556300796969936, -0.2039769588889765, 1.0569715142428784],
    ]
)
_M1 = np.array(
    [
        [0.4122214708, 0.5363325363, 0.0514459929],
        [0.2119034982, 0.6806995451, 0.1073969566],
        [0.0883024619, 0.2817188376, 0.6299787005],
    ]
)
_M2 = np.array(
    [
        [0.2104542553, 0.7936177850, -0.0040720468],
        [1.9779984951, -2.4285922050, 0.4505937099],
        [0.0259040371, 0.7827717662, -0.8086757660],
    ]
)
_M2_INV = np.array(
    [
        [1.0, 0.3963377774, 0.2158037573],
        [1.0, -0.1055613458, -0.0638541728],
        [1.0, -0.0894841775, -1.2914855480],
    ]
)
_M1_INV = np.array(
    [
        [4.0767416621, -3.3077115913, 0.2309699292],
        [-1.2684380046, 2.6097574011, -0.3413193965],
        [-0.0041960863, -0.7034186147, 1.7076147010],
    ]
)


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
