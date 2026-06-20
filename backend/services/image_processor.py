"""
services/image_processor.py
Classical image-processing step: Canny edge detection.

Why Canny?
- Reveals cell boundaries and structural detail invisible in the raw intensity image.
- Deterministic, fast, and well-understood — good fit for microscopy QC.
- Single OpenCV call with no trainable parameters.
"""
from __future__ import annotations
import base64
# import io
import logging
import numpy as np

logger = logging.getLogger(__name__)

def _b64_to_numpy(b64: str) -> np.ndarray:
    import cv2
    # Strip data-URL prefix if present (e.g. "data:image/png;base64,...")
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    # Fix missing padding before decoding
    b64 = b64.strip()
    b64 += "=" * (-len(b64) % 4)
    raw = base64.b64decode(b64)
    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode base64 image")
    return img

def _numpy_to_b64(img: np.ndarray) -> str:
    import cv2
    _, buf = cv2.imencode(".png", img)
    return base64.b64encode(buf.tobytes()).decode("utf-8")

def is_valid_image(image_b64: str) -> bool:
    """Return False if the base64 data cannot be decoded as a valid image."""
    try:
        _b64_to_numpy(image_b64)
        return True
    except Exception:
        return False


def apply_canny_edges(image_b64: str) -> str:
    """
    Convert image to grayscale, apply Gaussian blur, then Canny edge detection.
    Returns the processed image as a base64-encoded PNG.
    """
    import cv2
    img = _b64_to_numpy(image_b64)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=30, threshold2=100)

    # Convert single-channel edge map back to 3-channel so the frontend
    # can display it identically to the original (both are RGB PNGs).
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    logger.debug("Canny edge detection applied")
    return _numpy_to_b64(edges_rgb)
