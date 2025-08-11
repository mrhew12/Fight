# AI Pipeline Deep Dive: SpriteShift AI

## 1. Introduction

The core of SpriteShift AI is its automated pipeline that transforms a single static 2D character image into a fully animated sprite. This document provides a technical breakdown of each step in the pipeline, the models used, and conceptual code examples to guide implementation.

The pipeline is a sequence of independent stages that progressively process the image.

**Input:** A single user-provided character image (e.g., `character.png`).
**Output:** A sprite sheet (`character_sprites.png`) and a metadata file (`character_anim.json`).

---

## 2. Step 1: Background Removal

**Goal:** Isolate the character from its original background.
**Model:** `rembg`

Before any animation can occur, the character must be separated from its background to create a clean sprite with a transparent alpha channel. `rembg` is a user-friendly, effective, open-source tool for this purpose.

**Conceptual Code:**
```python
from rembg import remove
from PIL import Image

def remove_background(input_path: str, output_path: str):
    """Removes the background from an image."""
    try:
        input_image = Image.open(input_path)
        output_image = remove(input_image)
        output_image.save(output_path)
        print(f"Background removed. Image saved to {output_path}")
    except FileNotFoundError:
        print(f"Error: Input file not found at {input_path}")

# --- Usage ---
# remove_background("character_upload.png", "character_no_bg.png")
```

---

## 3. Step 2: Pose Extraction

**Goal:** Identify the character's skeletal structure from the static image.
**Model:** `MediaPipe Pose`

To animate the character realistically, we first need to understand its pose. `MediaPipe Pose` is a high-performance, open-source pose estimation model that can detect keypoints (joints) on a character's body. This skeletal data serves as the foundation for generating new poses during animation.

**Conceptual Code:**
```python
import cv2
import mediapipe as mp

def extract_pose(image_path: str) -> list:
    """Extracts pose landmarks from an image."""
    mp_pose = mp.solutions.pose
    pose_landmarks = []

    with mp_pose.Pose(static_image_mode=True) as pose:
        image = cv2.imread(image_path)
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                pose_landmarks.append({"x": landmark.x, "y": landmark.y, "z": landmark.z})

    print(f"Extracted {len(pose_landmarks)} landmarks.")
    return pose_landmarks

# --- Usage ---
# initial_pose = extract_pose("character_no_bg.png")
```

---

## 4. Step 3: Animation Generation

**Goal:** Create new animation frames based on the character's appearance and a target motion.
**Models:** `AnimateDiff` + `AnimateDiff-Lightning`

This is the core generative step. We use a motion generation model (`AnimateDiff`) to create a sequence of new poses, and then an image-to-video model (`AnimateDiff-Lightning`) to render the character's appearance onto those poses.

1.  **Motion Generation:** A pre-trained motion module (e.g., "walk," "punch") is used to generate a sequence of skeletal poses, starting from the character's initial pose.
2.  **Frame Rendering:** `AnimateDiff-Lightning` takes the original character image (with background removed) as a style and structure reference. It uses this reference to render new frames of the character conforming to the generated pose sequence.

**Conceptual Code (using Hugging Face `diffusers`):**
```python
from diffusers import AnimateDiffPipeline, MotionAdapter
from diffusers.utils import export_to_gif
import torch

def generate_animation_frames(character_image_path: str, motion_prompt: str):
    """Generates animation frames for a character."""
    adapter = MotionAdapter.from_pretrained("guoyww/animatediff-motion-adapter-v1-5-2")
    pipe = AnimateDiffPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", motion_adapter=adapter)

    # In a real implementation, we would feed the extracted pose data here.
    # For this conceptual example, we use a text prompt to guide the motion.
    output = pipe(prompt=f"A character in the style of the input image, performing a {motion_prompt} animation.")

    frames = output.frames[0]
    export_to_gif(frames, f"{motion_prompt}_animation.gif")
    print(f"Animation saved to {motion_prompt}_animation.gif")

# --- Usage ---
# generate_animation_frames("character_no_bg.png", "light punch")
```

---

## 5. Step 4: Hitbox Generation

**Goal:** Automatically create hitboxes for collision detection in-game.
**Method:** Algorithmic (Contour Detection)

Hitboxes are essential for game mechanics. We can programmatically generate them by analyzing the non-transparent pixels of each animation frame.

1.  Read each generated frame.
2.  Use an image processing library like OpenCV to find the contours of the character on the alpha channel.
3.  Calculate the bounding box for each significant contour (e.g., head, limbs).
4.  Store these bounding box coordinates (`x, y, width, height`) in the metadata file.

**Conceptual Code:**
```python
import cv2
import numpy as np

def generate_hitboxes(frame_path: str) -> list:
    """Generates hitboxes by finding contours in an image's alpha channel."""
    image = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)
    alpha_channel = image[:, :, 3]
    contours, _ = cv2.findContours(alpha_channel, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    hitboxes = []
    for contour in contours:
        if cv2.contourArea(contour) > 100: # Filter out small noise
            x, y, w, h = cv2.boundingRect(contour)
            hitboxes.append({"x": x, "y": y, "width": w, "height": h})

    return hitboxes

# --- Usage ---
# frame_hitboxes = generate_hitboxes("animation_frame_01.png")
```

---

## 6. Step 5: Style Harmonization

**Goal:** Adjust the color palette of the generated sprite to match a target game's aesthetic.
**Method:** Algorithmic (Color Quantization)

To ensure visual consistency, we can map the colors of the generated sprite to a predefined color palette provided by the user.

**Conceptual Code (using PIL):**
```python
from PIL import Image

def harmonize_style(image_path: str, target_palette: Image.Image, output_path: str):
    """Harmonizes the image's colors to a target palette."""
    source_image = Image.open(image_path).convert("RGB")

    # Create a new image with the target palette and apply it
    harmonized_image = source_image.quantize(palette=target_palette)
    harmonized_image = harmonized_image.convert("RGB")

    harmonized_image.save(output_path)
    print(f"Harmonized image saved to {output_path}")

# --- Usage ---
# target_palette_img = Image.new("P", (16, 16))
# colors = [255,0,0, 0,255,0, 0,0,255] # Example: a simple RGB palette
# target_palette_img.putpalette(colors)
# harmonize_style("character_sprites.png", target_palette_img, "character_harmonized.png")
```
