import logging
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

# Import pipeline modules
from pipeline import background_remover, pose_extractor, animator, hitbox_generator
from utils import image_utils

# --- Setup ---
app = FastAPI(
    title="SpriteShift AI - Inference Service",
    description="This service orchestrates the AI pipeline for character animation.",
    version="0.2.0"
)

# Configure logging to provide detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Define base directories for storing intermediate and final files
BASE_OUTPUT_DIR = Path("./outputs")
BASE_TEMP_DIR = Path("./temp_processing")

# --- Pydantic Models for API requests ---
class InferenceTaskParams(BaseModel):
    motion_prompt: str = "idle"
    character_prompt: str = "a 2D character sprite"
    num_frames: int = 16
    num_columns_sprite_sheet: int = 4

class InferenceTask(BaseModel):
    job_id: str = str(uuid.uuid4())
    source_image_url: str
    params: InferenceTaskParams = InferenceTaskParams()

# --- Main Processing Logic ---
def process_full_pipeline(task: InferenceTask, temp_base_dir: Path, output_base_dir: Path):
    """
    Orchestrates the full AI pipeline for a single inference task,
    from downloading an image to generating the final assets.

    Args:
        task: The inference task details.
        temp_base_dir: The base directory for temporary processing files.
        output_base_dir: The base directory for final output assets.
    """
    job_id = task.job_id
    logger.info(f"--- Starting processing for job_id: {job_id} ---")

    # 1. Create dedicated working directories for this job to keep files organized.
    job_temp_dir = temp_base_dir / job_id
    job_output_dir = output_base_dir / job_id
    job_temp_dir.mkdir(parents=True, exist_ok=True)
    job_output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # 2. Download the user-provided source image.
        source_image_path = job_temp_dir / "00_source.png"
        if not image_utils.download_image(task.source_image_url, source_image_path):
            raise RuntimeError(f"Failed to download image from {task.source_image_url}")

        # 3. Remove the background from the image.
        no_bg_image_path = job_temp_dir / "01_no_bg.png"
        background_remover.remove_background(source_image_path, no_bg_image_path)

        # 4. Extract pose data. This is for logging/future use, as the current
        #    AnimateDiff setup does not use it as a direct input.
        pose_data = pose_extractor.extract_pose(no_bg_image_path)
        if pose_data:
            pose_data_path = job_temp_dir / "02_pose_data.json"
            with open(pose_data_path, 'w') as f:
                json.dump(pose_data, f, indent=4)
            logger.info(f"Pose data extracted and saved to {pose_data_path}")
        else:
            logger.warning("Pose extraction did not return any data for this image.")

        # 5. Generate the animation frames. This is the most compute-intensive step.
        animation_gif_path = job_temp_dir / "03_animation.gif"
        animation_frames = animator.generate_animation(
            motion_prompt=task.params.motion_prompt,
            character_prompt=task.params.character_prompt,
            output_path=animation_gif_path,
            num_frames=task.params.num_frames,
        )
        if not animation_frames:
            raise RuntimeError("Animation generation failed to produce any frames.")

        # 6. Generate hitboxes for each frame of the animation.
        hitboxes = hitbox_generator.generate_hitboxes_for_animation(animation_frames)

        # 7. Create the final sprite sheet from all generated frames.
        sprite_sheet_path = job_output_dir / "character_sprites.png"
        sprite_sheet = image_utils.create_sprite_sheet(
            animation_frames, columns=task.params.num_columns_sprite_sheet
        )
        sprite_sheet.save(sprite_sheet_path)
        logger.info(f"Final sprite sheet saved to {sprite_sheet_path}")

        # 8. Create the final animation metadata file.
        frame_count = len(animation_frames)
        columns = task.params.num_columns_sprite_sheet
        metadata = {
            "job_id": job_id,
            "source_image_url": task.source_image_url,
            "animation_properties": {
                "num_frames": frame_count,
                "frame_width": animation_frames[0].width,
                "frame_height": animation_frames[0].height,
                "columns": columns,
                "rows": (frame_count + columns - 1) // columns
            },
            "frames": hitboxes
        }
        metadata_path = job_output_dir / "character_anim.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)
        logger.info(f"Animation metadata saved to {metadata_path}")

        logger.info(f"--- Successfully finished processing for job_id: {job_id} ---")
        return {
            "status": "complete",
            "job_id": job_id,
            "output_files": {
                "sprite_sheet": str(sprite_sheet_path),
                "animation_metadata": str(metadata_path)
            }
        }

    except Exception as e:
        logger.error(f"!!! Pipeline processing failed for job_id {job_id}: {e}", exc_info=True)
        raise # Re-raise to be caught by the API endpoint handler

# --- API Endpoints ---
@app.get("/", summary="Health Check")
def read_root():
    return {"message": "SpriteShift AI Inference Service is running."}

@app.post("/run-task", summary="Run Animation Pipeline")
def run_inference_task(task: InferenceTask):
    """
    Accepts a task to generate a character animation from a source image.
    This endpoint orchestrates the entire AI pipeline asynchronously.
    """
    try:
        result = process_full_pipeline(
            task=task,
            temp_base_dir=BASE_TEMP_DIR,
            output_base_dir=BASE_OUTPUT_DIR
        )
        return result
    except Exception as e:
        logger.error(f"Top-level error processing task for job {task.job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline failed for job {task.job_id}: {str(e)}")

if __name__ == "__main__":
    # Ensure the base directories exist when starting the server directly.
    BASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    BASE_TEMP_DIR.mkdir(parents=True, exist_ok=True)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
