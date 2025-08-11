import cv2
import numpy as np
import logging
from typing import List, Dict
from PIL import Image

logger = logging.getLogger(__name__)

Hitbox = Dict[str, int]
AnimationHitboxes = List[Hitbox]

def generate_hitboxes_for_animation(frames: List[Image.Image], contour_area_threshold: int = 100) -> AnimationHitboxes:
    """
    Generates hitboxes for a sequence of animation frames by finding the largest contour.

    Args:
        frames: A list of PIL Image objects, expected to be in RGBA format.
        contour_area_threshold: The minimum pixel area to be considered a valid contour.

    Returns:
        A list of hitbox dictionaries, one for each frame. If no valid contour is found
        for a frame, a zero-sized hitbox is returned for that frame.
    """
    animation_hitboxes = []
    logger.info(f"Generating hitboxes for {len(frames)} animation frames...")

    for i, frame in enumerate(frames):
        hitbox = {"x": 0, "y": 0, "width": 0, "height": 0} # Default empty hitbox
        try:
            # Convert PIL Image to a NumPy array that OpenCV can process.
            # The image must be in RGBA format to have an alpha channel for contour detection.
            if frame.mode != 'RGBA':
                logger.warning(f"Frame {i} is not in RGBA mode. Converting...")
                frame_rgba = frame.convert('RGBA')
            else:
                frame_rgba = frame

            frame_np = np.array(frame_rgba)

            # The alpha channel is the 4th channel in an RGBA image.
            alpha_channel = frame_np[:, :, 3]

            # Find contours in the alpha channel. cv2.RETR_EXTERNAL retrieves only the outer contours.
            contours, _ = cv2.findContours(alpha_channel, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                logger.warning(f"No contours found for frame {i}.")
                animation_hitboxes.append(hitbox)
                continue

            # Find the largest contour by area to represent the main character body.
            largest_contour = max(contours, key=cv2.contourArea)

            if cv2.contourArea(largest_contour) < contour_area_threshold:
                logger.warning(f"Largest contour in frame {i} is below the area threshold.")
                animation_hitboxes.append(hitbox)
                continue

            # Calculate the bounding box for the largest contour.
            x, y, w, h = cv2.boundingRect(largest_contour)
            hitbox = {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}
            animation_hitboxes.append(hitbox)

        except Exception as e:
            logger.error(f"Failed to generate hitbox for frame {i}: {e}")
            animation_hitboxes.append(hitbox) # Append default hitbox on error

    logger.info(f"Successfully generated hitboxes for {len(animation_hitboxes)} frames.")
    return animation_hitboxes
