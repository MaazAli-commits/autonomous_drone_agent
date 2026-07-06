"""
Mission simulator: fakes flying a drone along the planned waypoints and
capturing an image at each one.

There's no real drone here -- this simulates the "capture" step by
cycling through a folder of sample images. In a real deployment, this
function would instead pull frames from a live drone camera feed.
"""

import os
import random

SAMPLE_IMAGES_DIR = os.path.join(os.path.dirname(__file__), "..", "vision", "sample_images")


def simulate_flight(waypoints: list) -> list:
    """
    Takes a list of [lat, lon, alt] waypoints, "visits" each one, and
    returns a list of dicts pairing each waypoint with a captured image path.

    Returns:
        [{"waypoint": [lat, lon, alt], "image_path": "path/to/image.jpg"}, ...]
    """
    images = [
        f for f in os.listdir(SAMPLE_IMAGES_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]

    if not images:
        raise FileNotFoundError(
            f"No sample images found in {SAMPLE_IMAGES_DIR}. "
            "Add a few .jpg/.png files there to simulate captured photos."
        )

    captures = []
    for wp in waypoints:
        # cycle through available images rather than requiring exactly
        # as many images as waypoints
        image_name = random.choice(images)
        captures.append({
            "waypoint": wp,
            "image_path": os.path.join(SAMPLE_IMAGES_DIR, image_name),
        })

    return captures