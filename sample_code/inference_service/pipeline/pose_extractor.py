import cv2
import mediapipe as mp
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Define a type alias for pose landmarks for clarity
PoseLandmarks = List[Dict[str, float]]

def extract_pose(image_path: Path) -> Optional[PoseLandmarks]:
    """
    Extracts pose landmarks from an image using MediaPipe Pose.

    Args:
        image_path: Path to the input image file.

    Returns:
        A list of landmark dictionaries (containing x, y, z, visibility),
        or None if no pose is detected.
    """
    mp_pose = mp.solutions.pose
    pose_landmarks = []

    try:
        logger.info(f"Extracting pose from '{image_path}'...")
        image = cv2.imread(str(image_path))
        if image is None:
            logger.error(f"Failed to read image from '{image_path}'. Is the file corrupted or path incorrect?")
            return None

        # MediaPipe processes RGB images, but OpenCV reads them in BGR format.
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Initialize MediaPipe Pose with high complexity for better accuracy on static images.
        with mp_pose.Pose(static_image_mode=True, model_complexity=2, enable_segmentation=False) as pose:
            results = pose.process(image_rgb)

            if not results.pose_landmarks:
                logger.warning(f"No pose detected in image '{image_path}'.")
                return None

            for landmark in results.pose_landmarks.landmark:
                pose_landmarks.append({
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility,
                })

            logger.info(f"Successfully extracted {len(pose_landmarks)} landmarks from '{image_path}'.")
            return pose_landmarks

    except Exception as e:
        logger.error(f"An unexpected error occurred during pose extraction: {e}")
        raise
