import requests
import logging
from pathlib import Path
from typing import List
from PIL import Image

logger = logging.getLogger(__name__)

def download_image(url: str, save_path: Path) -> bool:
    """
    Downloads an image from a URL and saves it to a local path.
    Returns True on success, False on failure.
    """
    try:
        logger.info(f"Downloading image from {url} to {save_path}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Ensure the directory exists
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"Image downloaded successfully to {save_path}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image from {url}: {e}")
        return False

def create_sprite_sheet(frames: List[Image.Image], columns: int) -> Image.Image:
    """
    Creates a single sprite sheet image from a list of animation frames.

    Args:
        frames: A list of PIL Image objects.
        columns: The number of columns in the sprite sheet grid.

    Returns:
        A single PIL Image object representing the sprite sheet.
    """
    if not frames:
        raise ValueError("Cannot create a sprite sheet from an empty list of frames.")

    frame_width = frames[0].width
    frame_height = frames[0].height
    num_frames = len(frames)

    # Calculate the number of rows required
    rows = (num_frames + columns - 1) // columns

    sprite_sheet_width = columns * frame_width
    sprite_sheet_height = rows * frame_height

    logger.info(f"Creating a {columns}x{rows} sprite sheet ({sprite_sheet_width}x{sprite_sheet_height}px).")

    # Create a new blank image with a transparent background
    sprite_sheet = Image.new('RGBA', (sprite_sheet_width, sprite_sheet_height), (0, 0, 0, 0))

    for i, frame in enumerate(frames):
        row = i // columns
        col = i % columns
        x_offset = col * frame_width
        y_offset = row * frame_height
        sprite_sheet.paste(frame, (x_offset, y_offset))

    return sprite_sheet
