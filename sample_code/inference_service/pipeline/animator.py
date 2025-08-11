import torch
from diffusers import AnimateDiffPipeline, MotionAdapter
from diffusers.utils import export_to_gif
from pathlib import Path
import logging
from typing import List
from PIL import Image

logger = logging.getLogger(__name__)

class Animator:
    """
    A wrapper class for the AnimateDiff pipeline to generate animations.
    """
    def __init__(self, model_id: str = "runwayml/stable-diffusion-v1-5"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.pipe = None

        logger.info(f"Initializing Animator on device: {self.device} with dtype: {self.dtype}")

        try:
            adapter = MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2")
            self.pipe = AnimateDiffPipeline.from_pretrained(
                model_id,
                motion_adapter=adapter,
                torch_dtype=self.dtype
            )
            # The .to(device) call is deferred to the generate method
            # to allow for more flexible resource management if needed.
            logger.info("AnimateDiff pipeline and motion adapter loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load the AnimateDiff pipeline: {e}")
            raise

    def generate(
        self,
        motion_prompt: str,
        character_prompt: str,
        output_path: Path,
        num_frames: int = 16,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 25
    ) -> List[Image.Image]:
        """
        Generates an animation based on prompts and saves it as a GIF.

        Args:
            motion_prompt: A prompt describing the motion (e.g., "jumping", "walking").
            character_prompt: A prompt describing the character (e.g., "a knight in shining armor").
            output_path: The path to save the output GIF file.
            num_frames: The number of frames to generate for the animation.
            guidance_scale: The scale for classifier-free guidance.
            num_inference_steps: The number of denoising steps.

        Returns:
            A list of PIL.Image.Image objects representing the generated frames.
        """
        if not self.pipe:
            raise RuntimeError("Animator pipeline is not initialized.")

        logger.info(f"Generating animation for motion: '{motion_prompt}'")

        self.pipe.to(self.device)
        full_prompt = f"masterpiece, best quality, {character_prompt}, {motion_prompt}"
        negative_prompt = "bad quality, worse quality, low resolution, blurry, deformed"

        if self.device == 'cuda':
            free_before, total_before = torch.cuda.mem_get_info()
            logger.info(f"GPU Memory (before generation): {(total_before - free_before) / 1024**3:.2f}GB used / {total_before / 1024**3:.2f}GB total")

        output = self.pipe(
            prompt=full_prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            num_frames=num_frames,
        )
        frames = output.frames[0]

        if self.device == 'cuda':
            free_after, total_after = torch.cuda.mem_get_info()
            logger.info(f"GPU Memory (after generation): {(total_after - free_after) / 1024**3:.2f}GB used / {total_after / 1024**3:.2f}GB total")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        export_to_gif(frames, str(output_path))
        logger.info(f"Animation saved successfully to '{output_path}'")

        return frames

# --- Module-level function for easy use ---

# Note: In a production environment, you would want to initialize the Animator
# class once and reuse it across requests to avoid reloading the model,
# e.g., by managing its lifecycle with the FastAPI application.
# For this self-contained module, we instantiate it on each call.

def generate_animation(
    motion_prompt: str,
    character_prompt: str,
    output_path: Path,
    num_frames: int = 16
) -> List[Image.Image]:
    """
    High-level function to initialize the animator and generate an animation.
    """
    try:
        logger.info("Initializing animator for generation task...")
        animator = Animator()
        logger.info("Animator initialized. Starting animation generation...")
        generated_frames = animator.generate(
            motion_prompt=motion_prompt,
            character_prompt=character_prompt,
            output_path=output_path,
            num_frames=num_frames
        )
        return generated_frames
    except Exception as e:
        logger.error(f"Animation generation task failed: {e}")
        raise
