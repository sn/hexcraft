"""Extract dominant colors from an image. Synthesizes a small painted image
in-memory so the example needs no asset files; swap for any real numpy array
or PIL Image (`np.array(Image.open(...))`) in production.

Requires: pip install 'hexcraft[numpy]'

Run: python examples/11_image_palette.py
"""

import numpy as np

from hexcraft import Color
from hexcraft.image import average_color, dominant_colors


def chip(c: Color, width: int = 6) -> str:
    r, g, b = c.rgb
    return f"\x1b[48;2;{r};{g};{b}m{' ' * width}\x1b[0m"


def synthesize_painting(seed: int = 7) -> np.ndarray:
    """Build a 256x256 RGB image with five dominant colors plus film-grain noise."""
    rng = np.random.default_rng(seed)
    h, w = 256, 256
    image = np.zeros((h, w, 3), dtype=np.float64)

    palette = [
        np.array([0.95, 0.93, 0.87]),  # cream
        np.array([0.10, 0.18, 0.32]),  # midnight blue
        np.array([0.85, 0.27, 0.20]),  # rust red
        np.array([0.28, 0.55, 0.40]),  # forest green
        np.array([0.75, 0.62, 0.30]),  # ochre
    ]
    weights = [0.40, 0.20, 0.15, 0.15, 0.10]

    labels = rng.choice(len(palette), size=(h, w), p=weights)
    for i, base in enumerate(palette):
        image[labels == i] = base

    image += rng.normal(0.0, 0.025, image.shape)
    return np.clip(image, 0.0, 1.0)


def main() -> None:
    img = synthesize_painting()
    print(f"Synthetic image: {img.shape[0]}x{img.shape[1]} pixels.\n")

    print("Average color (linear-sRGB mean - the gamma-correct way):")
    avg = average_color(img)
    print(f"  {chip(avg)} {avg.hex}\n")

    print("Top 5 dominant colors via OKLab k-means (perceptual clustering):")
    palette = dominant_colors(img, n=5, method="kmeans", seed=0)
    for c in palette:
        print(f"  {chip(c)} {c.hex}  (closest CSS name: {c.name})")
    print()

    print("Same image via median-cut (faster, less perceptual):")
    palette_mc = dominant_colors(img, n=5, method="median_cut")
    for c in palette_mc:
        print(f"  {chip(c)} {c.hex}")


if __name__ == "__main__":
    main()
