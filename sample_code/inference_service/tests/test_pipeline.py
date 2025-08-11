import pytest
import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image

# Add the parent directory to the sys.path to allow imports from sibling modules (main, pipeline, etc.)
# This is a common pattern for simple project structures without a full package installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import process_full_pipeline, InferenceTask, InferenceTaskParams

# --- Test Helper Functions ---

def create_dummy_image(path: Path, size=(64, 64), color='red') -> Path:
    """Creates a simple dummy PNG image for testing and saves it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new('RGBA', size, color)
    img.save(path, 'PNG')
    return path

def create_dummy_frames(num_frames=16, size=(512, 512)) -> list:
    """Creates a list of dummy PIL Image frames in memory."""
    return [Image.new('RGBA', size, (i * 15, 50, 100, 255)) for i in range(num_frames)]

# --- Pytest Fixtures ---

@pytest.fixture
def tmp_dirs(tmp_path: Path) -> tuple[Path, Path]:
    """Pytest fixture to create and provide temporary directories for a test run."""
    temp_dir = tmp_path / "temp_processing"
    output_dir = tmp_path / "outputs"
    temp_dir.mkdir()
    output_dir.mkdir()
    return temp_dir, output_dir

@pytest.fixture
def test_image(tmp_path: Path) -> Path:
    """Pytest fixture to create a dummy image file for tests to use as a source."""
    asset_path = tmp_path / "test_assets"
    return create_dummy_image(asset_path / "test_character.png")

# --- Test Case ---

@patch('main.image_utils.download_image')
@patch('main.background_remover.remove_background')
@patch('main.pose_extractor.extract_pose')
@patch('main.animator.generate_animation')
def test_full_pipeline_successful_run(
    mock_generate_animation: MagicMock,
    mock_extract_pose: MagicMock,
    mock_remove_background: MagicMock,
    mock_download_image: MagicMock,
    tmp_dirs: tuple[Path, Path],
    test_image: Path
):
    """
    Tests the successful execution of the entire `process_full_pipeline`.

    This is an integration test for the orchestration logic, where the actual slow
    AI and I/O-bound functions are mocked out. This allows us to verify that the
    pipeline steps are called in the correct order and that the final artifacts
    are generated correctly from the (mocked) intermediate data.
    """
    # 1. --- Setup Mocks ---
    temp_dir, output_dir = tmp_dirs

    # Mock download_image: it should "download" our local test image.
    def download_side_effect(url: str, save_path: Path) -> bool:
        import shutil
        shutil.copy(test_image, save_path)
        return True
    mock_download_image.side_effect = download_side_effect

    # Mock remove_background: it should just copy the input to the output.
    def remove_bg_side_effect(input_path: Path, output_path: Path):
        import shutil
        shutil.copy(input_path, output_path)
    mock_remove_background.side_effect = remove_bg_side_effect

    # Mock extract_pose: return some valid-looking dummy data.
    mock_extract_pose.return_value = [{"x": 0.5, "y": 0.5, "z": -0.5, "visibility": 0.99}]

    # Mock generate_animation: return a list of dummy PIL frames.
    num_frames = 16
    dummy_frames = create_dummy_frames(num_frames=num_frames)
    mock_generate_animation.return_value = dummy_frames

    # 2. --- Setup Test Data ---
    job_id = "test-job-12345"
    task = InferenceTask(
        job_id=job_id,
        source_image_url="http://example.com/fake_image.png",
        params=InferenceTaskParams(num_frames=num_frames, num_columns_sprite_sheet=4)
    )

    # 3. --- Run the Pipeline ---
    result = process_full_pipeline(task=task, temp_base_dir=temp_dir, output_base_dir=output_dir)

    # 4. --- Assert Results ---

    # Assert return value is correct
    assert result['status'] == 'complete'
    assert result['job_id'] == job_id

    # Assert that the final output files were created
    output_job_dir = output_dir / job_id
    sprite_sheet_path = output_job_dir / "character_sprites.png"
    metadata_path = output_job_dir / "character_anim.json"

    assert sprite_sheet_path.exists(), "The final sprite sheet was not created."
    assert metadata_path.exists(), "The final metadata JSON file was not created."

    # Assert that the mocked functions were called as expected
    mock_download_image.assert_called_once()
    mock_remove_background.assert_called_once()
    mock_extract_pose.assert_called_once()
    mock_generate_animation.assert_called_once()

    # Assert the content of the metadata file is correct
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    assert metadata['job_id'] == job_id
    assert metadata['animation_properties']['num_frames'] == num_frames
    assert metadata['animation_properties']['columns'] == 4
    assert len(metadata['frames']) == num_frames

    # The hitbox generator is NOT mocked, so it runs on the dummy frames.
    # Since dummy frames are solid colors, the hitbox should be the full frame size.
    first_hitbox = metadata['frames'][0]
    assert first_hitbox['x'] == 0
    assert first_hitbox['y'] == 0
    assert first_hitbox['width'] == dummy_frames[0].width
    assert first_hitbox['height'] == dummy_frames[0].height

    # Assert the created sprite sheet has the correct dimensions
    sprite_sheet_img = Image.open(sprite_sheet_path)
    assert sprite_sheet_img.width == 4 * dummy_frames[0].width
    assert sprite_sheet_img.height == (num_frames // 4) * dummy_frames[0].height
