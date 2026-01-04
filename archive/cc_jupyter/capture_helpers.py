#!/usr/bin/env python3
"""
Helper functions for capturing and processing rich outputs from IPython.
"""

from __future__ import annotations

from typing import Any


def extract_images_from_captured(captured_output: Any) -> list[dict[str, Any]]:
    """Extract image data from IPython captured output.

    Args:
        captured_output: The captured output object from IPython.utils.capture

    Returns:
        List of dicts with image data, each containing 'format', 'data', and 'metadata'
    """
    images: list[dict[str, Any]] = []

    if not hasattr(captured_output, "outputs") or not captured_output.outputs:
        return images

    for output in captured_output.outputs:
        if hasattr(output, "data") and isinstance(output.data, dict):
            # Check for various image formats
            for img_format in ["image/png", "image/jpeg", "image/jpg", "image/svg+xml"]:
                if img_format in output.data:
                    image_info: dict[str, Any] = {
                        "format": img_format,
                        "data": output.data[img_format],
                        "metadata": getattr(output, "metadata", {}),
                    }

                    # Get dimensions if available
                    if img_format in image_info["metadata"]:
                        image_info["dimensions"] = image_info["metadata"][img_format]

                    images.append(image_info)

    return images


def format_images_summary(images: list[dict[str, Any]]) -> str:
    """Create a text summary of captured images for including in prompts.

    Args:
        images: List of image dicts from extract_images_from_captured

    Returns:
        Formatted string describing the captured images
    """
    if not images:
        return ""

    lines = ["The following images were captured from the code execution:"]

    for i, img in enumerate(images, 1):
        format_type = img["format"]

        # Get dimensions if available
        dims = ""
        if "dimensions" in img:
            dims_data = img["dimensions"]
            if (
                isinstance(dims_data, dict)
                and "width" in dims_data
                and "height" in dims_data
            ):
                dims = f" ({dims_data['width']}x{dims_data['height']})"

        # Show a preview of the base64 data
        data_preview = (
            img["data"][:50] + "..." if len(img["data"]) > 50 else img["data"]
        )

        lines.append(f"\nImage {i}:")
        lines.append(f"  Format: {format_type}{dims}")
        lines.append(f"  Base64 data preview: {data_preview}")

    lines.append("\nNote: The full image data is available in the captured output.")
    return "\n".join(lines)
