from rembg import remove
from PIL import Image
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def remove_background(input_path: Path, output_path: Path):
    """
    Removes the background from an image using rembg.

    Args:
        input_path: Path to the input image file.
        output_path: Path to save the output image with a transparent background.
    """
    try:
        logger.info(f"Removing background from '{input_path}'...")
        input_image = Image.open(input_path)
        output_image = remove(input_image)

        # Ensure the output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_image.save(output_path)
        logger.info(f"Background removed. Image saved to '{output_path}'")
    except FileNotFoundError:
        logger.error(f"Error: Input file not found at '{input_path}'")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred during background removal: {e}")
        raise
