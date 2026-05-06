"""Dominant color extraction from images.

Numpy is required. Two algorithms are offered:

- ``"kmeans"`` — Lloyd's algorithm in OKLab (perceptually meaningful clusters).
  k-means++ seeding for stability. Default.
- ``"median_cut"`` — Heckbert's classic algorithm in linear sRGB. Faster, more
  deterministic, slightly less perceptual.

Both accept a numpy array of shape (H, W, 3) or (N, 3) with sRGB values in
[0, 1]. uint8 arrays are auto-scaled.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

try:
    import numpy as np
except ImportError as e:
    raise ImportError(
        "hexcraft.image requires numpy. Install with: pip install 'hexcraft[numpy]'"
    ) from e

from .arrays import oklab_to_srgb, srgb_to_oklab

if TYPE_CHECKING:
    from .color import Color


def _normalize(image: np.ndarray) -> np.ndarray:
    arr = np.asarray(image)
    arr = arr.astype(np.float64) / 255.0 if arr.dtype == np.uint8 else arr.astype(np.float64)
    if arr.ndim == 3:
        arr = arr.reshape(-1, arr.shape[-1])
    if arr.shape[-1] == 4:
        arr = arr[:, :3]
    return arr


def _kmeanspp_init(points: np.ndarray, k: int, rng: np.random.Generator) -> np.ndarray:
    n = points.shape[0]
    centroids = np.empty((k, points.shape[1]))
    centroids[0] = points[rng.integers(n)]
    closest_sq = np.sum((points - centroids[0]) ** 2, axis=1)
    for i in range(1, k):
        total = closest_sq.sum()
        if total <= 0.0:
            centroids[i] = points[rng.integers(n)]
        else:
            probs = closest_sq / total
            centroids[i] = points[rng.choice(n, p=probs)]
        new_sq = np.sum((points - centroids[i]) ** 2, axis=1)
        closest_sq = np.minimum(closest_sq, new_sq)
    return centroids


def _kmeans(points: np.ndarray, k: int, *, max_iter: int, seed: int | None) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    centroids = _kmeanspp_init(points, k, rng)
    for _ in range(max_iter):
        d2 = ((points[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
        labels = d2.argmin(axis=1)
        new = np.empty_like(centroids)
        for j in range(k):
            mask = labels == j
            if mask.any():
                new[j] = points[mask].mean(axis=0)
            else:
                new[j] = points[rng.integers(points.shape[0])]
        if np.allclose(new, centroids, atol=1e-6):
            centroids = new
            break
        centroids = new
    counts = np.bincount(labels, minlength=k)
    return centroids, counts


def _median_cut(points: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    buckets = [points]
    while len(buckets) < k:
        buckets.sort(key=lambda b: 0 if len(b) == 0 else (b.max(axis=0) - b.min(axis=0)).max(), reverse=True)
        biggest = buckets.pop(0)
        if len(biggest) <= 1:
            buckets.append(biggest)
            break
        ranges = biggest.max(axis=0) - biggest.min(axis=0)
        axis = int(ranges.argmax())
        sorted_b = biggest[biggest[:, axis].argsort()]
        mid = len(sorted_b) // 2
        buckets.append(sorted_b[:mid])
        buckets.append(sorted_b[mid:])
    centroids = np.stack([b.mean(axis=0) for b in buckets if len(b) > 0])
    counts = np.array([len(b) for b in buckets if len(b) > 0])
    return centroids, counts


def dominant_colors(
    image: np.ndarray,
    n: int = 5,
    *,
    method: Literal["kmeans", "median_cut"] = "kmeans",
    max_iter: int = 30,
    sample: int | None = 50_000,
    seed: int | None = None,
) -> list[Color]:
    """Extract the ``n`` most representative colors from an image.

    image:
      A numpy array of sRGB values, shape (H, W, 3), (H, W, 4), or (N, 3).
      Values in [0, 1] floating-point or [0, 255] uint8.
    method:
      ``"kmeans"`` clusters in OKLab (perceptual). ``"median_cut"`` runs
      Heckbert's algorithm in linear sRGB.
    sample:
      If the input has more than ``sample`` pixels, a random subsample is used
      for speed. Pass ``None`` to disable subsampling.

    Returns colors ordered from most to least common.
    """
    from .color import Color

    pts = _normalize(image)
    if sample is not None and pts.shape[0] > sample:
        rng = np.random.default_rng(seed)
        idx = rng.choice(pts.shape[0], size=sample, replace=False)
        pts = pts[idx]

    if method == "kmeans":
        ok = srgb_to_oklab(pts)
        centroids_ok, counts = _kmeans(ok, n, max_iter=max_iter, seed=seed)
        centroids_rgb = np.clip(oklab_to_srgb(centroids_ok), 0.0, 1.0)
    elif method == "median_cut":
        centroids_rgb, counts = _median_cut(pts, n)
        centroids_rgb = np.clip(centroids_rgb, 0.0, 1.0)
    else:
        raise ValueError(f"unknown method: {method!r}")

    order = np.argsort(-counts)
    return [Color.from_rgb(*centroids_rgb[i]) for i in order]


def average_color(image: np.ndarray) -> Color:
    """Mean color of an image, computed in linear sRGB to avoid gamma bias."""
    from .arrays import srgb_decode, srgb_encode
    from .color import Color
    pts = _normalize(image)
    linear = srgb_decode(pts)
    mean_lin = linear.mean(axis=0)
    return Color.from_rgb(*srgb_encode(mean_lin))
